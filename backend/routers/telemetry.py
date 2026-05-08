"""Telemetry API — raw speed/throttle/brake data for driver laps."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, HTTPException
from src.data_loader import load_session, extract_fastest_lap_telemetry, extract_driver_telemetry

router = APIRouter()

@router.get("/{circuit}/{driver}")
def get_telemetry(circuit: str, driver: str, session_type: str = "R", max_laps: int = 8):
    """Get telemetry data for a driver at a circuit."""
    try:
        session = load_session(circuit, session_type)
        # Try fastest lap first
        tel = extract_fastest_lap_telemetry(session, driver)
        if tel is None or tel.empty:
            tel = extract_driver_telemetry(session, driver, max_laps)
        if tel is None or tel.empty:
            raise HTTPException(404, f"No telemetry for {driver} at {circuit}")
        return {
            "driver": driver, "circuit": circuit,
            "distance": tel["Distance"].tolist(),
            "speed": tel["Speed"].tolist(),
            "throttle": tel["Throttle"].tolist(),
            "brake": tel["Brake"].astype(float).tolist(),
            "gear": tel["nGear"].tolist(),
            "points": len(tel),
        }
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/{circuit}")
def get_multi_driver_telemetry(circuit: str, drivers: str = "", session_type: str = "R"):
    """Get telemetry for multiple drivers (comma-separated)."""
    driver_list = [d.strip() for d in drivers.split(",") if d.strip()]
    if not driver_list:
        raise HTTPException(400, "Provide drivers as comma-separated list")
    try:
        session = load_session(circuit, session_type)
        result = {}
        for d in driver_list[:6]:
            tel = extract_fastest_lap_telemetry(session, d)
            if tel is not None and not tel.empty:
                result[d] = {
                    "distance": tel["Distance"].tolist(),
                    "speed": tel["Speed"].tolist(),
                    "throttle": tel["Throttle"].tolist(),
                    "brake": tel["Brake"].astype(float).tolist(),
                }
        return {"circuit": circuit, "drivers": result}
    except Exception as e:
        raise HTTPException(500, str(e))
