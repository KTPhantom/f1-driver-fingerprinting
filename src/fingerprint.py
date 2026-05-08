"""
Fingerprint Module — Driver Identification & Cross-Track Validation.

Creates centroid-based driver fingerprints from UMAP embeddings and
validates whether a driver can be identified on tracks never seen
during training — the core transferability test.

Author: Kshitij Tripathi
"""

import logging
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score
)

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DRIVER_FULL_NAMES

logger = logging.getLogger(__name__)


class DriverFingerprinter:
    """
    Builds and validates driver fingerprints using UMAP embeddings.

    Two identification methods:
    1. Centroid-based: Mean embedding per driver → nearest centroid classification
    2. KNN-based: k-Nearest Neighbors on UMAP embeddings

    The key test is cross-track transferability: train on circuits A,B,C
    and test on held-out circuits D,E.
    """

    def __init__(self, n_neighbors: int = 7):
        self.n_neighbors = n_neighbors
        self.centroids: Dict[str, np.ndarray] = {}
        self.knn = KNeighborsClassifier(n_neighbors=n_neighbors, weights="distance")
        self._feature_cols = ["UMAP_1", "UMAP_2"]
        self._is_fitted = False

    def fit(self, train_df: pd.DataFrame):
        """
        Build driver fingerprints from training data.

        Args:
            train_df: Clustered DataFrame with UMAP coords and Driver labels.
        """
        logger.info(f"Building fingerprints from {len(train_df)} training segments")
        X = train_df[self._feature_cols].values
        y = train_df["Driver"].values

        # Centroid fingerprints
        for driver in np.unique(y):
            mask = y == driver
            self.centroids[driver] = X[mask].mean(axis=0)
            logger.info(f"  {driver}: centroid at [{self.centroids[driver][0]:.2f}, {self.centroids[driver][1]:.2f}] ({mask.sum()} segments)")

        # KNN model
        self.knn.fit(X, y)
        self._is_fitted = True
        logger.info(f"  ✓ Fingerprints built for {len(self.centroids)} drivers")

    def predict_centroid(self, test_df: pd.DataFrame) -> np.ndarray:
        """Predict drivers using nearest-centroid classification."""
        X = test_df[self._feature_cols].values
        centroid_keys = list(self.centroids.keys())
        centroid_matrix = np.array([self.centroids[k] for k in centroid_keys])

        # Distance from each point to each centroid
        predictions = []
        for point in X:
            dists = np.linalg.norm(centroid_matrix - point, axis=1)
            predictions.append(centroid_keys[np.argmin(dists)])
        return np.array(predictions)

    def predict_knn(self, test_df: pd.DataFrame) -> np.ndarray:
        """Predict drivers using KNN on UMAP embeddings."""
        X = test_df[self._feature_cols].values
        return self.knn.predict(X)

    def evaluate(
        self, test_df: pd.DataFrame, method: str = "knn"
    ) -> Dict:
        """
        Evaluate cross-track driver identification.

        Args:
            test_df: Test DataFrame with UMAP coords and true Driver labels.
            method: 'knn' or 'centroid'.

        Returns:
            Dict with accuracy, per-driver metrics, confusion matrix.
        """
        if not self._is_fitted:
            raise RuntimeError("Call fit() first.")

        y_true = test_df["Driver"].values
        y_pred = self.predict_knn(test_df) if method == "knn" else self.predict_centroid(test_df)

        acc = accuracy_score(y_true, y_pred)
        report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=sorted(set(y_true)))

        # Per-driver accuracy
        driver_acc = {}
        for driver in np.unique(y_true):
            mask = y_true == driver
            driver_acc[driver] = float(np.mean(y_pred[mask] == driver))

        results = {
            "overall_accuracy": round(acc, 4),
            "method": method,
            "classification_report": report,
            "confusion_matrix": cm,
            "driver_labels": sorted(set(y_true)),
            "per_driver_accuracy": driver_acc,
            "n_test_samples": len(test_df),
            "random_baseline": round(1.0 / len(np.unique(y_true)), 4),
        }

        logger.info(f"  Cross-track accuracy ({method}): {acc:.1%}")
        logger.info(f"  Random baseline: {results['random_baseline']:.1%}")
        logger.info(f"  Lift over random: {acc / results['random_baseline']:.1f}x")
        return results

    def get_driver_profile(self, feature_df: pd.DataFrame, driver: str) -> Dict:
        """
        Compute a driver's behavioral profile (mean feature values).

        Used for radar chart visualization.
        """
        mask = feature_df["Driver"] == driver
        if mask.sum() == 0:
            return {}

        driver_data = feature_df.loc[mask]
        numeric_cols = [c for c in driver_data.select_dtypes(include=[np.number]).columns
                       if c not in ("LapNumber","SegmentId","UMAP_1","UMAP_2",
                                   "UMAP_3D_1","UMAP_3D_2","UMAP_3D_3","Cluster","Cluster_Prob")]

        profile = {}
        for col in numeric_cols:
            profile[col] = float(driver_data[col].mean())
        return profile

    def get_all_profiles(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """Get behavioral profiles for all drivers as a DataFrame."""
        profiles = {}
        for driver in feature_df["Driver"].unique():
            profiles[driver] = self.get_driver_profile(feature_df, driver)
        return pd.DataFrame(profiles).T
