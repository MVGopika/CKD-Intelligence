"""
Regression Models Module
========================
Trains Linear Regression and Support Vector Regression models 
to predict eGFR from clinical biomarkers.
Reports RMSE, MAE, MAPE, and R² metrics.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import json
import os


def mean_absolute_percentage_error(y_true, y_pred):
    """Calculate MAPE, avoiding division by zero."""
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def evaluate_regression(y_true, y_pred, model_name="Model"):
    """Compute and print regression metrics."""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)

    metrics = {
        'RMSE': round(rmse, 4),
        'MAE': round(mae, 4),
        'MAPE': round(mape, 2),
        'R2': round(r2, 4),
    }
    print(f"  [{model_name}]  RMSE={metrics['RMSE']:.4f}  MAE={metrics['MAE']:.4f}  "
          f"MAPE={metrics['MAPE']:.2f}%  R²={metrics['R2']:.4f}")
    return metrics


def train_regression_models(X_train, y_train, X_test, y_test, save_dir=None):
    """
    Train LR and SVR models for eGFR prediction.
    
    Parameters
    ----------
    X_train, y_train : training data
    X_test, y_test : testing data
    save_dir : str or None
        If provided, saves metrics JSON to this directory.

    Returns
    -------
    dict : model name → {model, metrics, predictions}
    """
    print("\n" + "="*60)
    print("REGRESSION MODELS — eGFR Prediction")
    print("="*60)

    results = {}

    # ---- 1. Linear Regression ----
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    metrics_lr = evaluate_regression(y_test, y_pred_lr, "Linear Regression")
    results['Linear Regression'] = {
        'model': lr,
        'metrics': metrics_lr,
        'predictions': y_pred_lr,
    }

    # ---- 2. SVR (default RBF kernel) ----
    svr = SVR(kernel='rbf', C=10, epsilon=0.1, gamma='scale')
    svr.fit(X_train, y_train)
    y_pred_svr = svr.predict(X_test)
    metrics_svr = evaluate_regression(y_test, y_pred_svr, "SVR (RBF)")
    results['SVR'] = {
        'model': svr,
        'metrics': metrics_svr,
        'predictions': y_pred_svr,
    }

    # ---- Save metrics ----
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        metrics_out = {name: res['metrics'] for name, res in results.items()}
        with open(os.path.join(save_dir, "regression_metrics.json"), 'w') as f:
            json.dump(metrics_out, f, indent=2)
        print(f"  [SAVED] Regression metrics → {save_dir}/regression_metrics.json")

    return results
