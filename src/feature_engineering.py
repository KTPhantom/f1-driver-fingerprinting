"""
Feature Engineering Module — Behavioral Feature Extraction.

Transforms raw telemetry micro-segments into a fixed-length feature vector
capturing 5 behavioral dimensions: braking, throttle, cornering, gear, speed.

Author: Kshitij Tripathi
"""

import logging
from typing import List, Dict
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _safe(arr, func, default=0.0):
    try:
        if len(arr) == 0: return default
        r = func(arr)
        return float(r) if np.isfinite(r) else default
    except: return default


def extract_braking_features(seg):
    brake, speed = seg["Brake"], seg["Speed"]
    active = brake > 0.1
    onset = np.argmax(active) / max(len(brake),1) if active.any() else 1.0
    dur = np.sum(active) / max(len(brake),1)
    sd = np.diff(speed)
    decel = -sd[active[1:]] if active[1:].any() else np.array([0.0])
    decel = decel[decel > 0] if len(decel[decel>0])>0 else np.array([0.0])
    return {"brake_mean":_safe(brake,np.mean),"brake_max":_safe(brake,np.max),
            "brake_std":_safe(brake,np.std),"brake_onset_pct":float(onset),
            "brake_duration_pct":float(dur),"deceleration_rate_mean":_safe(decel,np.mean),
            "deceleration_rate_max":_safe(decel,np.max)}


def extract_throttle_features(seg):
    t = seg["Throttle"]
    td = np.diff(t); app = td[td>0]
    partial = np.sum((t>20)&(t<80))/max(len(t),1)
    full = np.sum(t>95)/max(len(t),1)
    jerk = np.diff(t,n=2) if len(t)>2 else np.array([0.0])
    smooth = min(1.0/(np.mean(np.abs(jerk))+1e-6), 1000.0)
    return {"throttle_mean":_safe(t,np.mean),"throttle_std":_safe(t,np.std),
            "throttle_max":_safe(t,np.max),"throttle_application_rate":_safe(app,np.mean),
            "partial_throttle_pct":float(partial),"full_throttle_pct":float(full),
            "throttle_smoothness":float(smooth)}


def extract_cornering_features(seg):
    speed, x, y = seg["Speed"], seg["X"], seg["Y"]
    if len(x)>2:
        h = np.arctan2(np.diff(y),np.diff(x))
        hr = np.diff(h); sm = speed[1:-1]/3.6
        lg = np.clip(np.abs(sm*hr)/9.81, 0, 10)
    else: lg = np.array([0.0])
    return {"speed_std":_safe(speed,np.std),"speed_min":_safe(speed,np.min),
            "speed_range":float(np.ptp(speed)) if len(speed)>0 else 0.0,
            "lateral_g_mean":_safe(lg,np.mean),"lateral_g_max":_safe(lg,np.max),
            "lateral_g_std":_safe(lg,np.std)}


def extract_gear_features(seg):
    gear = seg["nGear"].astype(float); speed = seg["Speed"]
    gd = np.diff(gear)
    up_i = np.where(gd>0)[0]; dn_i = np.where(gd<0)[0]
    us = speed[up_i+1] if len(up_i)>0 else np.array([0.0])
    ds = speed[dn_i+1] if len(dn_i)>0 else np.array([0.0])
    return {"gear_mean":_safe(gear,np.mean),"gear_std":_safe(gear,np.std),
            "gear_changes_count":float(len(np.where(gd!=0)[0])),
            "upshift_speed_mean":_safe(us,np.mean),"downshift_speed_mean":_safe(ds,np.mean)}


def extract_speed_features(seg):
    s = seg["Speed"]
    entry = float(s[0]) if len(s)>0 else 0.0
    exit_ = float(s[-1]) if len(s)>0 else 0.0
    return {"speed_mean":_safe(s,np.mean),"speed_max":_safe(s,np.max),
            "entry_speed":entry,"exit_speed":exit_,"speed_delta":exit_-entry}


def extract_features(segment):
    """Extract the complete 30-dim feature vector from a micro-segment."""
    f = {}
    f.update(extract_braking_features(segment))
    f.update(extract_throttle_features(segment))
    f.update(extract_cornering_features(segment))
    f.update(extract_gear_features(segment))
    f.update(extract_speed_features(segment))
    return f


def build_feature_matrix(segments: List[Dict]) -> pd.DataFrame:
    """Build feature matrix from all micro-segments. Returns DataFrame with features + metadata."""
    logger.info(f"Extracting features from {len(segments)} segments...")
    rows = []
    for i, seg in enumerate(segments):
        features = extract_features(seg)
        features["Driver"] = seg["Driver"]
        features["Circuit"] = seg["Circuit"]
        features["LapNumber"] = seg["LapNumber"]
        features["SegmentId"] = seg["SegmentId"]
        rows.append(features)
        if (i+1)%500==0: logger.info(f"  Processed {i+1}/{len(segments)}")
    df = pd.DataFrame(rows)
    nc = df.select_dtypes(include=[np.number]).columns
    df[nc] = df[nc].replace([np.inf,-np.inf], np.nan).fillna(0)
    logger.info(f"  ✓ Feature matrix: {df.shape[0]} segments × {len(nc)} features")
    return df
