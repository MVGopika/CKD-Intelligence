"""Feature preprocessing utilities"""
import numpy as np

# placeholder functions; actual scaling performed by scaler objects in model_loader

def normalize_features(features: dict) -> np.ndarray:
    arr = np.array(list(features.values())).reshape(1, -1)
    return arr
