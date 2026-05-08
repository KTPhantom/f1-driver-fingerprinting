"""Laps API — lap times, sector times, tire data."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, HTTPException
import math
from src.data_loader import load_session, load_lap_data

router = APIRouter()

def clean_records(records):
    """Replace NaN/inf with None for JSON serialization."""
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                r[k] = None
    return records

@router.get("/{circuit}")
def get_laps(circuit: str, session_type: str = "R"):
    try:
        session = load_session(circuit, session_type)
        laps = load_lap_data(session)
        if laps.empty:
            raise HTTPException(404, f"No lap data for {circuit}")
        records = clean_records(laps.to_dict(orient="records"))
        return {"circuit": circuit, "laps": records, "count": len(records)}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error loading laps: {str(e)}")

@router.get("/{circuit}/{driver}")
def get_driver_laps(circuit: str, driver: str, session_type: str = "R"):
    try:
        session = load_session(circuit, session_type)
        laps = load_lap_data(session, drivers=[driver])
        if laps.empty:
            raise HTTPException(404, f"No laps for {driver} at {circuit}")
        records = clean_records(laps.to_dict(orient="records"))
        return {"circuit": circuit, "driver": driver, "laps": records}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error loading laps: {str(e)}")
