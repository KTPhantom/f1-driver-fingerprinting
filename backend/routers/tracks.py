"""Tracks API — circuit maps, metadata."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, HTTPException
import numpy as np
from src.data_loader import load_session, load_track_map
from config import ALL_CIRCUITS

router = APIRouter()

@router.get("/list")
def list_circuits():
    return {"circuits": [
        {"display": c[0], "name": c[1], "country": c[2], "type": c[3], "distance_km": c[4]}
        for c in ALL_CIRCUITS
    ]}

@router.get("/{circuit}")
def get_track_map(circuit: str, session_type: str = "R"):
    try:
        session = load_session(circuit, session_type)
        track = load_track_map(session)
        if track is None:
            raise HTTPException(404, f"No track map for {circuit}")
        # Handle both numpy arrays and pandas Series
        x = track["X"]
        y = track["Y"]
        speed = track["Speed"]
        x_list = x.tolist() if hasattr(x, 'tolist') else list(x)
        y_list = y.tolist() if hasattr(y, 'tolist') else list(y)
        speed_list = speed.tolist() if hasattr(speed, 'tolist') else list(speed)
        # Replace any NaN/inf with 0
        x_list = [0.0 if (isinstance(v, float) and (np.isnan(v) or np.isinf(v))) else float(v) for v in x_list]
        y_list = [0.0 if (isinstance(v, float) and (np.isnan(v) or np.isinf(v))) else float(v) for v in y_list]
        speed_list = [0.0 if (isinstance(v, float) and (np.isnan(v) or np.isinf(v))) else float(v) for v in speed_list]
        return {
            "circuit": circuit,
            "x": x_list,
            "y": y_list,
            "speed": speed_list,
            "points": len(x_list),
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error loading track: {str(e)}")
