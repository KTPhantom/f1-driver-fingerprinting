"""
Clustering Module — UMAP + HDBSCAN Pipeline.

Implements the unsupervised learning core: dimensionality reduction via UMAP
followed by density-based clustering via HDBSCAN. Provides both clustering
and visualization embeddings.

Author: Kshitij Tripathi
"""

import logging
from typing import Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    silhouette_score, adjusted_rand_score, normalized_mutual_info_score
)
import umap
import hdbscan

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import UMAPConfig, HDBSCANConfig, ALL_FEATURES

logger = logging.getLogger(__name__)


class ClusteringPipeline:
    """
    End-to-end UMAP + HDBSCAN clustering pipeline.
    
    Handles feature scaling, dimensionality reduction, and density-based
    clustering. Produces both high-dimensional embeddings for clustering
    and 2D/3D embeddings for visualization.
    """

    def __init__(
        self,
        umap_config: UMAPConfig = UMAPConfig(),
        hdbscan_config: HDBSCANConfig = HDBSCANConfig(),
    ):
        self.umap_config = umap_config
        self.hdbscan_config = hdbscan_config
        self.scaler = StandardScaler()
        self.umap_cluster = None
        self.umap_viz_2d = None
        self.umap_viz_3d = None
        self.clusterer = None
        self._is_fitted = False

    def _get_feature_cols(self, df: pd.DataFrame):
        """Get numeric feature columns, filtering to known features if possible."""
        available = [f for f in ALL_FEATURES if f in df.columns]
        if len(available) >= 10:
            return available
        return [c for c in df.select_dtypes(include=[np.number]).columns
                if c not in ("LapNumber", "SegmentId")]

    def fit(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit the full pipeline: scale → UMAP → HDBSCAN.

        Args:
            feature_df: DataFrame from build_feature_matrix().

        Returns:
            DataFrame augmented with UMAP coordinates and cluster labels.
        """
        feature_cols = self._get_feature_cols(feature_df)
        logger.info(f"Fitting pipeline on {len(feature_df)} samples, {len(feature_cols)} features")

        # 1. Scale features
        X = self.scaler.fit_transform(feature_df[feature_cols].values)
        logger.info("  ✓ Features scaled (StandardScaler)")

        # 2. UMAP for clustering (high-dim)
        cfg = self.umap_config
        self.umap_cluster = umap.UMAP(
            n_components=cfg.n_components_cluster,
            n_neighbors=cfg.n_neighbors_cluster,
            min_dist=cfg.min_dist_cluster,
            metric=cfg.metric_cluster,
            random_state=cfg.random_state,
        )
        X_cluster = self.umap_cluster.fit_transform(X)
        logger.info(f"  ✓ UMAP clustering embedding: {X_cluster.shape}")

        # 3. UMAP for 2D visualization
        self.umap_viz_2d = umap.UMAP(
            n_components=cfg.n_components_viz,
            n_neighbors=cfg.n_neighbors_viz,
            min_dist=cfg.min_dist_viz,
            metric=cfg.metric_viz,
            random_state=cfg.random_state,
        )
        X_2d = self.umap_viz_2d.fit_transform(X)

        # 4. UMAP for 3D visualization
        self.umap_viz_3d = umap.UMAP(
            n_components=cfg.n_components_3d,
            n_neighbors=cfg.n_neighbors_3d,
            min_dist=cfg.min_dist_3d,
            metric=cfg.metric_viz,
            random_state=cfg.random_state,
        )
        X_3d = self.umap_viz_3d.fit_transform(X)
        logger.info(f"  ✓ UMAP viz embeddings: 2D{X_2d.shape}, 3D{X_3d.shape}")

        # 5. HDBSCAN clustering
        hcfg = self.hdbscan_config
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=hcfg.min_cluster_size,
            min_samples=hcfg.min_samples,
            cluster_selection_epsilon=hcfg.cluster_selection_epsilon,
            cluster_selection_method=hcfg.cluster_selection_method,
            prediction_data=hcfg.prediction_data,
        )
        cluster_labels = self.clusterer.fit_predict(X_cluster)
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        n_noise = np.sum(cluster_labels == -1)
        logger.info(f"  ✓ HDBSCAN: {n_clusters} clusters, {n_noise} noise points")

        # 6. Augment DataFrame
        result = feature_df.copy()
        result["UMAP_1"] = X_2d[:, 0]
        result["UMAP_2"] = X_2d[:, 1]
        result["UMAP_3D_1"] = X_3d[:, 0]
        result["UMAP_3D_2"] = X_3d[:, 1]
        result["UMAP_3D_3"] = X_3d[:, 2]
        result["Cluster"] = cluster_labels
        result["Cluster_Prob"] = self.clusterer.probabilities_

        self._is_fitted = True
        return result

    def evaluate(self, result_df: pd.DataFrame) -> dict:
        """
        Evaluate clustering quality against ground-truth driver labels.

        Returns dict with Silhouette, ARI, NMI scores.
        """
        mask = result_df["Cluster"] != -1
        if mask.sum() < 10:
            return {"silhouette": 0, "ari": 0, "nmi": 0, "n_clusters": 0, "noise_pct": 100}

        X_viz = result_df.loc[mask, ["UMAP_1", "UMAP_2"]].values
        clusters = result_df.loc[mask, "Cluster"].values
        drivers = result_df.loc[mask, "Driver"].values

        sil = silhouette_score(X_viz, clusters) if len(set(clusters)) > 1 else 0
        ari = adjusted_rand_score(drivers, clusters)
        nmi = normalized_mutual_info_score(drivers, clusters)

        n_clusters = len(set(clusters))
        noise_pct = (result_df["Cluster"] == -1).mean() * 100

        metrics = {
            "silhouette": round(sil, 4),
            "ari": round(ari, 4),
            "nmi": round(nmi, 4),
            "n_clusters": n_clusters,
            "noise_pct": round(noise_pct, 2),
        }
        logger.info(f"  Metrics: {metrics}")
        return metrics

    def transform_new(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """Transform new data through the fitted pipeline (for cross-track validation)."""
        if not self._is_fitted:
            raise RuntimeError("Pipeline not fitted. Call fit() first.")

        feature_cols = self._get_feature_cols(feature_df)
        X = self.scaler.transform(feature_df[feature_cols].values)

        X_2d = self.umap_viz_2d.transform(X)
        X_3d = self.umap_viz_3d.transform(X)
        X_cluster = self.umap_cluster.transform(X)

        labels, strengths = hdbscan.approximate_predict(self.clusterer, X_cluster)

        result = feature_df.copy()
        result["UMAP_1"] = X_2d[:, 0]
        result["UMAP_2"] = X_2d[:, 1]
        result["UMAP_3D_1"] = X_3d[:, 0]
        result["UMAP_3D_2"] = X_3d[:, 1]
        result["UMAP_3D_3"] = X_3d[:, 2]
        result["Cluster"] = labels
        result["Cluster_Prob"] = strengths
        return result
