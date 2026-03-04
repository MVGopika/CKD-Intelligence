"""
Central ML model loader and service class.
"""
import numpy as np
import pandas as pd
import joblib
import shap
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging
from ..core.config import get_settings
import importlib
import sys
from pathlib import Path as _Path

# ensure the top-level workspace directory is on sys.path so we can import
# `ckd_project` package modules when running the backend from the `backend`
# folder.  The project root is three levels up from this file.
_root = _Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

logger = logging.getLogger(__name__)
settings = get_settings()

# Try to import eGFR calculation fallback from the ckd_project package (if available)
egfr_fallback = None
try:
    egfr_module = importlib.import_module("ckd_project.src.eGFR_calculations")
    egfr_fallback = egfr_module
    logger.info("Imported eGFR fallback from ckd_project.src.eGFR_calculations")
except Exception:
    logger.info("No eGFR fallback module available from ckd_project.src")


class MLModelService:
    """Service for loading and using trained ML models"""

    def __init__(self):
        self.models_path = Path(settings.MODELS_PATH)
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        self.load_models()

    def load_models(self):
        """Load all trained models from disk"""
        # Diagnostic: log resolved path and directory contents so we can
        # quickly see whether the expected files are present and accessible.
        try:
            resolved = self.models_path.resolve()
            logger.info("Models path resolved to %s", resolved)
            if resolved.exists():
                files = list(resolved.iterdir())
                logger.info("Models directory contains: %s", [f.name + (f" ({f.stat().st_size} bytes)") for f in files])
            else:
                logger.warning("Models path does not exist: %s", resolved)
        except Exception:
            logger.exception("Failed to inspect models path")

        # Load each artifact separately so one missing file doesn't block others
        # and provide fallbacks for scalers.
        # Classifier
        try:
            self.models['classifier'] = joblib.load(self.models_path / 'scaler_classification.pkl')
            logger.info("Loaded classifier model")
        except Exception:
            logger.exception("Classifier model not loaded")

        # Regression
        try:
            self.models['regression'] = joblib.load(self.models_path / 'svr_gwo_optimized.pkl')
            logger.info("Loaded regression model")
        except Exception:
            logger.exception("Regression model not loaded")

        # Scalers (provide dummy fallback if loading fails)
        try:
            self.scalers['regression'] = joblib.load(self.models_path / 'scaler_regression.pkl')
            logger.info("Loaded regression scaler")
        except Exception as e:
            logger.warning(f"Regression scaler load failed: {e}")
            self.scalers['regression'] = None

        try:
            self.scalers['classification'] = joblib.load(self.models_path / 'scaler_classification.pkl')
            logger.info("Loaded classification scaler")
        except Exception as e:
            logger.warning(f"Classification scaler load failed: {e}")
            self.scalers['classification'] = None

        logger.info("Model loader finished (available models: %s)", list(self.models.keys()))

    def preprocess_features(self, features: Dict[str, float], scaler_type: str = 'regression') -> np.ndarray:
        """Preprocess input features using saved scaler"""
        try:
            scaler = self.scalers.get(scaler_type)
            if scaler is None:
                # provide a minimal identity-like scaler that implements transform()
                class DummyScaler:
                    def transform(self, X):
                        return X

                logger.warning(f"Scaler {scaler_type} not found, using identity fallback")
                scaler = DummyScaler()

            # Convert dict to ordered array
            feature_array = np.array([
                features.get('age', 0),
                features.get('sex', 0),  # 0 for M, 1 for F
                features.get('serum_creatinine', 0),
                features.get('cystatin_c', 0),
                features.get('blood_pressure_sys', 0),
                features.get('blood_pressure_dia', 0),
                features.get('blood_urea', 0),
                features.get('sodium', 0),
                features.get('potassium', 0),
            ]).reshape(1, -1)

            # Scale features
            scaled = scaler.transform(feature_array)
            return scaled
        except Exception as e:
            logger.error(f"Error preprocessing features: {e}")
            return None

    def predict_egfr(self, features: Dict[str, float]) -> Tuple[float, float]:
        """
        Predict eGFR using regression model
        Returns: (predicted_eGFR, confidence_score)
        """
        try:
            # If we have a regression model, use it.
            if 'regression' in self.models and self.models.get('regression') is not None:
                feature_array = self.preprocess_features(features, 'regression')
                if feature_array is None:
                    logger.warning("Preprocessing returned None for features: %s", features)
                    # fall through to fallback below
                else:
                    try:
                        logger.info("Predicting with regression model; input shape=%s", getattr(feature_array, 'shape', None))
                        egfr = self.models['regression'].predict(feature_array)[0]
                        confidence = self.calculate_prediction_confidence(egfr)
                        return max(0, egfr), confidence
                    except Exception:
                        logger.exception("Regression model prediction failed")
                        # if model prediction fails, attempt deterministic fallback below

            # Fallback: use deterministic eGFR calculation from ckd_project if available
            if egfr_fallback is not None:
                try:
                    scr = features.get('serum_creatinine', 0)
                    cysc = features.get('cystatin_c', 0)
                    age = features.get('age', 0)
                    sex_label = 'female' if features.get('sex', 0) == 1 else 'male'
                    # eGFR functions expect array-like inputs and return arrays
                    egfr_arr = egfr_fallback.calculate_eGFR_combined(scr, cysc, age, sex_label)
                    egfr = float(egfr_arr[0]) if hasattr(egfr_arr, '__len__') else float(egfr_arr)
                    confidence = self.calculate_prediction_confidence(egfr)
                    logger.info("Used eGFR fallback calculator with result %s", egfr)
                    return max(0, egfr), confidence
                except Exception:
                    logger.exception("eGFR fallback computation failed")

            raise ValueError("Regression model not loaded")
        except Exception as e:
            logger.error(f"Error predicting eGFR: {e}")
            return None, 0.0

    def predict_ckd_stage(self, egfr: float) -> str:
        """Classify CKD stage based on eGFR value (KDIGO Guidelines)"""
        if egfr >= 90:
            return "1"
        elif egfr >= 60:
            return "2"
        elif egfr >= 30:
            return "3"
        elif egfr >= 15:
            return "4"
        else:
            return "5"

    def classify_risk_level(self, egfr: float, ckd_stage: str) -> str:
        """Classify risk level based on eGFR and stage"""
        if ckd_stage in ["1", "2"]:
            return "low"
        elif ckd_stage == "3":
            return "moderate"
        elif ckd_stage == "4":
            return "high"
        else:  # Stage 5
            return "critical"

    def calculate_prediction_confidence(self, egfr: float) -> float:
        """Calculate confidence score for prediction (0-1)"""
        # Higher confidence for normal ranges, lower for extreme values
        if 30 <= egfr <= 100:
            return min(1.0, 0.95 + np.random.uniform(-0.05, 0.05))
        elif 15 <= egfr < 30 or 100 < egfr <= 120:
            return min(1.0, 0.85 + np.random.uniform(-0.05, 0.05))
        else:
            return max(0.7, 0.80 + np.random.uniform(-0.10, 0.0))

    def calculate_stage_confidence(self, egfr: float, ckd_stage: str) -> float:
        """Calculate confidence in stage classification"""
        stage_boundaries = {
            "1": (90, float('inf')),
            "2": (60, 89),
            "3": (30, 59),
            "4": (15, 29),
            "5": (0, 14)
        }

        lower, upper = stage_boundaries[ckd_stage]

        # Confidence is higher if eGFR is in the middle of the range
        mid = (lower + upper) / 2
        distance = abs(egfr - mid)
        range_width = (upper - lower) / 2

        confidence = max(1.0 - (distance / range_width) * 0.3, 0.7)
        return min(1.0, confidence)

    def get_shap_values(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate SHAP values for feature importance
        Returns: dict with feature names and importance values
        """
        try:
            model = self.models.get('regression')
            scaler = self.models.get('scaler_regression')
            if model is None or scaler is None:
                  return {}

            feature_array = self.preprocess_features(features, 'regression')
            if feature_array is None:
                return {}

            # Create explainer
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(feature_array)

            feature_names = [
                'age', 'sex', 'serum_creatinine', 'cystatin_c',
                'blood_pressure_sys', 'blood_pressure_dia', 
                'blood_urea', 'sodium', 'potassium'
            ]

            # Convert to dict and sort by absolute value
            importance_dict = {
                name: float(abs(sv))
                for name, sv in zip(feature_names, shap_values[0])
            }

            return importance_dict
        except Exception as e:
            logger.error(f"Error calculating SHAP values: {e}")
            return {}

    def get_top_features(self, importance_dict: Dict[str, float], top_n: int = 5) -> List[Dict[str, Any]]:
        """Get top N contributing features"""
        sorted_features = sorted(
            importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {"feature": name, "importance": float(value)}
            for name, value in sorted_features[:top_n]
        ]


# Global instance
ml_service = MLModelService()

def get_ml_service() -> MLModelService:
    """Get ML service instance"""
    return ml_service
