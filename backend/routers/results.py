"""Results API — race finishing positions, points, grid."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from src.data_loader import load_session, load_session_results

router = APIRouter()

class MultiCircuitRequest(BaseModel):
    circuits: List[str]
    session_type: str = "R"

@router.get("/{circuit}")
def get_results(circuit: str, session_type: str = "R"):
    try:
        session = load_session(circuit, session_type)
        results = load_session_results(session)
        if results.empty:
            raise HTTPException(404, f"No results for {circuit}")
        records = results.to_dict(orient="records")
        for r in records:
            for k, v in r.items():
                if isinstance(v, float) and (v != v):
                    r[k] = None
        return {"circuit": circuit, "results": records}
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/multi")
def get_multi_results(req: MultiCircuitRequest):
    all_results = []
    for circuit in req.circuits:
        try:
            session = load_session(circuit, req.session_type)
            results = load_session_results(session)
            if not results.empty:
                records = results.to_dict(orient="records")
                for r in records:
                    for k, v in r.items():
                        if isinstance(v, float) and (v != v):
                            r[k] = None
                all_results.extend(records)
        except Exception:
            continue
    return {"results": all_results, "circuits_loaded": len(set(r.get("Circuit","") for r in all_results))}
