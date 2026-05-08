"""ML Pipeline API — run clustering, get fingerprints."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import numpy as np

from src.data_loader import load_all_data
from src.feature_engineering import build_feature_matrix
from src.clustering import ClusteringPipeline
from src.fingerprint import DriverFingerprinter
from config import TRAIN_CIRCUITS, TEST_CIRCUITS, TARGET_DRIVERS

router = APIRouter()

# In-memory pipeline state
_state: Dict[str, Any] = {"status": "idle", "results": None, "error": None}

class MLRequest(BaseModel):
    train_circuits: Optional[List[List[str]]] = None
    test_circuits: Optional[List[List[str]]] = None
    drivers: Optional[List[str]] = None
    max_laps: int = 10

def _run_pipeline(req: MLRequest):
    global _state
    _state = {"status": "running", "results": None, "error": None}
    try:
        train_c = [tuple(c) for c in (req.train_circuits or TRAIN_CIRCUITS)]
        test_c = [tuple(c) for c in (req.test_circuits or TEST_CIRCUITS)]
        drivers = req.drivers or TARGET_DRIVERS

        train_seg, train_raw = load_all_data(train_c, drivers, req.max_laps)
        test_seg, test_raw = load_all_data(test_c, drivers, req.max_laps)
        if not train_seg:
            _state = {"status": "error", "results": None, "error": "No training data"}
            return

        train_feat = build_feature_matrix(train_seg)
        test_feat = build_feature_matrix(test_seg) if test_seg else None

        pipe = ClusteringPipeline()
        train_cl = pipe.fit(train_feat)
        metrics = pipe.evaluate(train_cl)

        # Build results
        umap_data = []
        for _, row in train_cl.iterrows():
            umap_data.append({
                "x": float(row.get("UMAP_1", 0)), "y": float(row.get("UMAP_2", 0)),
                "driver": row.get("Driver", ""), "circuit": row.get("Circuit", ""),
                "cluster": int(row.get("Cluster", -1)),
            })

        cross_track = {}
        profiles = {}
        if test_feat is not None and not test_feat.empty:
            test_cl = pipe.transform_new(test_feat)
            fp = DriverFingerprinter()
            fp.fit(train_cl)
            knn_res = fp.evaluate(test_cl, "knn")
            cross_track = {
                "overall_accuracy": knn_res["overall_accuracy"],
                "random_baseline": knn_res["random_baseline"],
                "per_driver_accuracy": knn_res["per_driver_accuracy"],
                "confusion_matrix": knn_res["confusion_matrix"].tolist(),
                "driver_labels": knn_res["driver_labels"],
            }
            prof_df = fp.get_all_profiles(train_cl)
            profiles = prof_df.to_dict(orient="index")

        # Feature importance (F-statistic)
        feature_imp = {}
        numeric_cols = [c for c in train_cl.columns if c not in (
            "Driver","Circuit","LapNumber","SegmentId",
            "UMAP_1","UMAP_2","UMAP_3D_1","UMAP_3D_2","UMAP_3D_3","Cluster","Cluster_Prob")]
        for col in numeric_cols:
            groups = [g[col].values for _, g in train_cl.groupby("Driver")]
            groups = [g for g in groups if len(g) > 1]
            if len(groups) < 2:
                continue
            gm = train_cl[col].mean()
            b = sum(len(g) * (g.mean() - gm) ** 2 for g in groups) / (len(groups) - 1)
            w = sum(g.var() * (len(g) - 1) for g in groups) / (sum(len(g) for g in groups) - len(groups))
            feature_imp[col] = round(float(b / (w + 1e-10)), 2)

        _state = {
            "status": "complete",
            "error": None,
            "results": {
                "umap_points": umap_data,
                "cluster_metrics": {
                    "n_clusters": int(metrics["n_clusters"]),
                    "silhouette": round(float(metrics["silhouette"]), 4),
                    "ari": round(float(metrics["ari"]), 4),
                    "nmi": round(float(metrics["nmi"]), 4),
                    "noise_pct": round(float(metrics["noise_pct"]), 1),
                },
                "cross_track": cross_track,
                "profiles": profiles,
                "feature_importance": dict(sorted(feature_imp.items(), key=lambda x: x[1], reverse=True)[:20]),
                "train_segments": len(train_cl),
                "drivers_analyzed": list(train_cl["Driver"].unique()),
            }
        }
    except Exception as e:
        _state = {"status": "error", "results": None, "error": str(e)}

@router.post("/run")
def run_ml(req: MLRequest, bg: BackgroundTasks):
    if _state["status"] == "running":
        raise HTTPException(409, "Pipeline already running")
    bg.add_task(_run_pipeline, req)
    return {"status": "started"}

@router.get("/status")
def ml_status():
    return {"status": _state["status"], "error": _state.get("error")}

@router.get("/results")
def ml_results():
    if _state["status"] != "complete":
        raise HTTPException(400, f"Pipeline status: {_state['status']}")
    return _state["results"]
