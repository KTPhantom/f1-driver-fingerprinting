"""
Data Loader Module — FastF1 Telemetry, Laps, Results & Track Data.

Handles all data acquisition from the FastF1 API. Provides functions for:
- Raw telemetry (speed, throttle, brake, gear, position)
- Lap-level data (lap times, sector times, tire compounds)
- Session results (positions, points, status)
- Track map data (circuit outline from X/Y coordinates)
- Micro-segmentation for ML pipeline

Author: Kshitij Tripathi
"""

import logging
from typing import List, Tuple, Optional, Dict
import fastf1
import numpy as np
import pandas as pd

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import CACHE_DIR, YEAR, TARGET_DRIVERS, SegmentConfig

logger = logging.getLogger(__name__)
fastf1.Cache.enable_cache(str(CACHE_DIR))


# ═══════════════════════════════════════════════════════════════════════════════
# Session Loading (with in-memory LRU cache)
# ═══════════════════════════════════════════════════════════════════════════════

_session_cache: Dict[str, object] = {}
_SESSION_CACHE_MAX = 8

def load_session(circuit: str, session_type: str = "R", year: int = YEAR):
    """Load a FastF1 session with telemetry and lap data (cached in memory)."""
    cache_key = f"{year}_{circuit}_{session_type}"
    if cache_key in _session_cache:
        logger.info(f"  ⚡ Cache hit: {cache_key}")
        return _session_cache[cache_key]

    logger.info(f"Loading {year} {circuit} {session_type}...")
    try:
        session = fastf1.get_session(year, circuit, session_type)
        session.load(telemetry=True, laps=True, weather=False, messages=False)
        logger.info(f"  ✓ Loaded {len(session.laps)} laps")
        # Evict oldest if cache is full
        if len(_session_cache) >= _SESSION_CACHE_MAX:
            oldest = next(iter(_session_cache))
            del _session_cache[oldest]
        _session_cache[cache_key] = session
        return session
    except Exception as e:
        logger.error(f"  ✗ Failed to load {circuit}: {e}")
        raise ValueError(f"Cannot load session: {circuit} {session_type}") from e


# ═══════════════════════════════════════════════════════════════════════════════
# NEW: Session Results
# ═══════════════════════════════════════════════════════════════════════════════

def load_session_results(session) -> pd.DataFrame:
    """
    Extract session results (positions, points, teams).

    Returns DataFrame with: Position, Driver, Team, GridPosition, Status, Points, Time.
    """
    try:
        results = session.results
        if results is None or results.empty:
            return pd.DataFrame()

        df = results[["Abbreviation", "TeamName", "GridPosition",
                       "Position", "Status", "Points", "Time"]].copy()
        df = df.rename(columns={"Abbreviation": "Driver", "TeamName": "Team"})
        df["Position"] = pd.to_numeric(df["Position"], errors="coerce")
        df["GridPosition"] = pd.to_numeric(df["GridPosition"], errors="coerce")
        df["Points"] = pd.to_numeric(df["Points"], errors="coerce").fillna(0)
        df["Circuit"] = str(session.event["EventName"])
        return df.reset_index(drop=True)
    except Exception as e:
        logger.warning(f"  Could not load results: {e}")
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
# NEW: Lap Data (lap times, sectors, tires)
# ═══════════════════════════════════════════════════════════════════════════════

def load_lap_data(session, drivers: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Extract lap-level data: lap times, sector times, tire info.

    Returns DataFrame with: Driver, LapNumber, LapTime (seconds),
    Sector1/2/3Time (seconds), Compound, TyreLife, IsPersonalBest.
    """
    try:
        laps = session.laps
        if drivers:
            laps = laps[laps["Driver"].isin(drivers)]
        if laps.empty:
            return pd.DataFrame()

        cols = ["Driver", "LapNumber", "LapTime", "Sector1Time",
                "Sector2Time", "Sector3Time", "Compound", "TyreLife",
                "IsPersonalBest", "Team"]
        available = [c for c in cols if c in laps.columns]
        df = laps[available].copy()

        # Convert timedeltas to seconds
        for col in ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time"]:
            if col in df.columns:
                df[col] = df[col].dt.total_seconds()

        df["Circuit"] = str(session.event["EventName"])
        df = df.dropna(subset=["LapTime"])
        # Filter outlier laps (pit/safety car) — keep laps within 115% of best
        if not df.empty:
            best = df["LapTime"].min()
            df = df[df["LapTime"] < best * 1.15]
        return df.reset_index(drop=True)
    except Exception as e:
        logger.warning(f"  Could not load lap data: {e}")
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
# NEW: Track Map Data
# ═══════════════════════════════════════════════════════════════════════════════

def load_track_map(session) -> Optional[Dict]:
    """
    Extract circuit outline and speed data from the fastest lap.

    Returns dict with:
      - X, Y: rotated circuit coordinates
      - Speed: speed at each point
      - circuit_info: corner positions, rotation angle
    """
    try:
        fastest = session.laps.pick_fastest()
        if fastest is None:
            return None

        tel = fastest.get_telemetry()
        if tel is None or tel.empty:
            return None

        pos = tel[["X", "Y", "Speed"]].copy()

        # Get circuit info for rotation
        try:
            circuit_info = session.get_circuit_info()
            angle = circuit_info.rotation / 180 * np.pi
            # Rotate coordinates
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            x_rot = pos["X"] * cos_a - pos["Y"] * sin_a
            y_rot = pos["X"] * sin_a + pos["Y"] * cos_a
            pos["X_rot"] = x_rot
            pos["Y_rot"] = y_rot
            corners = circuit_info.corners if hasattr(circuit_info, "corners") else None
        except Exception:
            pos["X_rot"] = pos["X"]
            pos["Y_rot"] = pos["Y"]
            corners = None
            circuit_info = None

        return {
            "X": pos["X_rot"].values,
            "Y": pos["Y_rot"].values,
            "Speed": pos["Speed"].values,
            "circuit_info": circuit_info,
            "corners": corners,
            "circuit_name": str(session.event["EventName"]),
        }
    except Exception as e:
        logger.warning(f"  Could not load track map: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# Existing: Raw Telemetry Extraction
# ═══════════════════════════════════════════════════════════════════════════════

def extract_driver_telemetry(session, driver: str, max_laps: int = 15) -> Optional[pd.DataFrame]:
    """Extract clean telemetry data for a specific driver."""
    try:
        driver_laps = session.laps.pick_drivers(driver).pick_quicklaps(1.1)
        if driver_laps.empty:
            return None

        driver_laps = driver_laps.sort_values("LapTime").head(max_laps)
        all_telemetry = []
        for _, lap in driver_laps.iterrows():
            try:
                tel = lap.get_telemetry()
                if tel is None or tel.empty or len(tel) < 50:
                    continue
                tel = tel[["Speed", "Throttle", "Brake", "nGear", "RPM", "X", "Y", "DRS"]].copy()
                dx = tel["X"].diff().fillna(0)
                dy = tel["Y"].diff().fillna(0)
                tel["Distance"] = np.sqrt(dx**2 + dy**2).cumsum()
                tel["Driver"] = driver
                tel["LapNumber"] = int(lap["LapNumber"]) if pd.notna(lap["LapNumber"]) else 0
                tel["Circuit"] = str(session.event["EventName"])
                all_telemetry.append(tel)
            except Exception:
                continue

        if not all_telemetry:
            return None
        result = pd.concat(all_telemetry, ignore_index=True)
        logger.info(f"  {driver}: {len(all_telemetry)} laps, {len(result)} points")
        return result
    except Exception as e:
        logger.warning(f"  Error for {driver}: {e}")
        return None


def extract_fastest_lap_telemetry(session, driver: str) -> Optional[pd.DataFrame]:
    """Extract telemetry for a single driver's fastest lap only."""
    try:
        driver_laps = session.laps.pick_drivers(driver)
        if driver_laps.empty:
            return None
        fastest = driver_laps.pick_fastest()
        if fastest is None:
            return None
        tel = fastest.get_telemetry()
        if tel is None or tel.empty:
            return None
        tel = tel[["Speed", "Throttle", "Brake", "nGear", "RPM", "X", "Y"]].copy()
        dx = tel["X"].diff().fillna(0)
        dy = tel["Y"].diff().fillna(0)
        tel["Distance"] = np.sqrt(dx**2 + dy**2).cumsum()
        tel["Driver"] = driver
        tel["Circuit"] = str(session.event["EventName"])
        return tel
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# Existing: Micro-Segmentation (for ML pipeline)
# ═══════════════════════════════════════════════════════════════════════════════

def segment_telemetry(telemetry: pd.DataFrame, config: SegmentConfig = SegmentConfig()) -> List[Dict]:
    """Split telemetry into fixed-distance micro-segments."""
    segments = []
    step = config.segment_distance_m * (1 - config.overlap_ratio)
    for (driver, circuit, lap_num), lap_data in telemetry.groupby(["Driver", "Circuit", "LapNumber"]):
        max_dist = lap_data["Distance"].max()
        start = 0.0
        seg_id = 0
        while start + config.segment_distance_m <= max_dist:
            end = start + config.segment_distance_m
            mask = (lap_data["Distance"] >= start) & (lap_data["Distance"] < end)
            seg_data = lap_data.loc[mask]
            if len(seg_data) >= config.min_segment_points:
                if seg_data["Speed"].mean() >= config.min_speed_threshold:
                    segments.append({
                        "Speed": seg_data["Speed"].values, "Throttle": seg_data["Throttle"].values,
                        "Brake": seg_data["Brake"].values.astype(float), "nGear": seg_data["nGear"].values,
                        "RPM": seg_data["RPM"].values, "X": seg_data["X"].values, "Y": seg_data["Y"].values,
                        "Driver": driver, "Circuit": circuit, "LapNumber": lap_num,
                        "SegmentId": seg_id, "DistanceStart": start, "DistanceEnd": end,
                    })
                    seg_id += 1
            start += step
    logger.info(f"  Created {len(segments)} micro-segments")
    return segments


def load_all_data(circuits, drivers=TARGET_DRIVERS, max_laps=15):
    """Load telemetry from multiple circuits and segment it."""
    all_segments, all_telemetry = [], []
    for circuit, session_type in circuits:
        try:
            session = load_session(circuit, session_type)
        except ValueError:
            continue
        for driver in drivers:
            tel = extract_driver_telemetry(session, driver, max_laps)
            if tel is not None:
                all_telemetry.append(tel)
                all_segments.extend(segment_telemetry(tel))
    raw_df = pd.concat(all_telemetry, ignore_index=True) if all_telemetry else pd.DataFrame()
    return all_segments, raw_df
