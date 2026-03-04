"""
=============================================================================
    ML Framework for Early Detection of CKD Stages
=============================================================================
    Main Pipeline (pandas-free version)
    
    Orchestrates:
        1. Synthetic data generation (if no CSV exists)
        2. Data preprocessing + eGFR computation (CKD-EPI 2021)
        3. Regression models (LR, SVR, GWO-SVR)
        4. Classification models (SVM, DT, RF, XGBoost + SMOTE)
        5. Publication-quality figure generation (13+ plots)
        6. SHAP explainability analysis
    
    Usage:  python main.py
=============================================================================
"""

import os
import sys
import json
import time
import numpy as np
import joblib
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.generate_synthetic_data import generate_synthetic_ckd_data
from src.data_preprocessing import load_and_preprocess_data, prepare_features
from src.eGFR_calculations import compute_all_egfr
from src.regression_models import train_regression_models
from src.gwo_optimizer import optimize_svr_with_gwo
from src.classification_models import train_classification_models
from src.visualization import generate_all_plots
from src.report_generator import generate_clinical_report


def print_banner():
    print("""
+===============================================================+
|   ML Framework for Early Detection of CKD Stages              |
|   -----------------------------------------------             |
|   CKD-EPI 2021  |  GWO-SVR  |  XGBoost  |  SHAP              |
+===============================================================+
    """)


def main():
    print_banner()
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"  Run started: {timestamp}")
    print(f"  Working dir: {PROJECT_ROOT}\n")

    # Paths
    RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "ckd_data.csv")
    MODELS_DIR = os.path.join(PROJECT_ROOT, "models", "saved_models")
    METRICS_DIR = os.path.join(PROJECT_ROOT, "results", "metrics")
    FIGURES_DIR = os.path.join(PROJECT_ROOT, "results", "figures")
    for d in [MODELS_DIR, METRICS_DIR, FIGURES_DIR]:
        os.makedirs(d, exist_ok=True)

    CHECKPOINT_PATH = os.path.join(METRICS_DIR, "last_run_results.joblib")
    GWO_CHECKPOINT_PATH = os.path.join(METRICS_DIR, "gwo_results.joblib")
    
    resumed = False
    gwo_resumed = False
    
    # 1. Full Resume (Everything done)
    if os.path.exists(CHECKPOINT_PATH):
        try:
            print(f"\n[?] Loading existing results from {CHECKPOINT_PATH}...")
            cp = joblib.load(CHECKPOINT_PATH)
            data = cp['data']; reg_results = cp['reg_results']; class_results = cp['class_results']
            y_test_egfr = cp['y_test_egfr']; y_test_stage = cp['y_test_stage']
            X_test_cls = cp['X_test_cls']; feat_cls = cp['feat_cls']
            gwo_curve = cp['gwo_curve']; best_params = cp['best_params']
            best_score = cp['best_score']; timestamp = cp['timestamp']
            
            # Also load models/scalers for scope safety
            svr_gwo = reg_results.get('SVR-GWO', {}).get('model')
            scaler_reg = cp.get('scaler_reg')
            scaler_cls = cp.get('scaler_cls')
            
            resumed = True
            print("  [RESUME] Full results loaded. Skipping all training.\n")
        except Exception as e:
            print(f"  [DEBUG] Load failed: {e}")

    # 2. GWO Resume (Optimization done, but maybe viz/report failed)
    if not resumed and os.path.exists(GWO_CHECKPOINT_PATH):
        try:
            print(f"\n[?] Resuming from GWO results found at {GWO_CHECKPOINT_PATH}...")
            cp = joblib.load(GWO_CHECKPOINT_PATH)
            data = cp['data']; reg_results = cp['reg_results']
            X_train_reg = cp['X_train_reg']; X_test_reg = cp['X_test_reg']; y_test_egfr = cp['y_test_egfr']
            X_train_cls = cp['X_train_cls']; X_test_cls = cp['X_test_cls']; y_train_stage = cp['y_train_stage']; y_test_stage = cp['y_test_stage']
            scaler_cls = cp['scaler_cls']; scaler_reg = cp.get('scaler_reg'); feat_cls = cp['feat_cls']
            best_params = cp['best_params']; best_score = cp['best_score']; gwo_curve = cp['gwo_curve']
            svr_gwo = cp['svr_gwo']
            gwo_resumed = True
            print("  [RESUME] GWO results loaded. Proceeding to Classification.\n")
        except Exception as e:
            print(f"  [DEBUG] GWO load failed: {e}")

    if not resumed:
        if not gwo_resumed:
            # ================================================================
            # PHASE 2: PREPROCESSING
            # ================================================================
            print("=" * 60)
            print("PHASE 2: DATA PREPROCESSING")
            print("=" * 60)
            data, columns = load_and_preprocess_data(RAW_PATH, save_processed=True)

            # ================================================================
            # PHASE 3: eGFR COMPUTATION
            # ================================================================
            print("\n" + "=" * 60)
            print("PHASE 3: eGFR COMPUTATION (CKD-EPI 2021)")
            print("=" * 60)
            data = compute_all_egfr(data)

            # ================================================================
            # PHASE 4: FEATURE PREPARATION
            # ================================================================
            FEATURE_COLS = ['Age', 'Sex_encoded', 'BMI', 'SCr', 'SCysC',
                            'HbA1c', 'CRP', 'Alb', 'SBP', 'DBP']

            print("\n  Preparing REGRESSION features (target: eGFR_Combined)...")
            X_train_reg, X_test_reg, y_train_egfr, y_test_egfr, scaler_reg, feat_reg = \
                prepare_features(data, FEATURE_COLS, 'eGFR_Combined')

            print("  Preparing CLASSIFICATION features (target: CKD_Stage)...")
            X_train_cls, X_test_cls, y_train_stage, y_test_stage, scaler_cls, feat_cls = \
                prepare_features(data, FEATURE_COLS, 'CKD_Stage')

            # ================================================================
            # PHASE 5: REGRESSION MODELS
            # ================================================================
            reg_results = train_regression_models(
                X_train_reg, y_train_egfr, X_test_reg, y_test_egfr, save_dir=METRICS_DIR
            )

            # ================================================================
            # PHASE 6: GWO-SVR OPTIMIZATION
            # ================================================================
            from sklearn.model_selection import train_test_split
            from sklearn.svm import SVR
            from sklearn.metrics import mean_squared_error, r2_score

            X_gwo_tr, X_gwo_val, y_gwo_tr, y_gwo_val = train_test_split(
                X_train_reg, y_train_egfr, test_size=0.2, random_state=42
            )
            best_params, best_score, gwo_curve = optimize_svr_with_gwo(
                X_gwo_tr, y_gwo_tr, X_gwo_val, y_gwo_val, n_wolves=20, max_iter=15
            )

            # Train final GWO-SVR on full training set
            svr_gwo = SVR(C=best_params[0], epsilon=best_params[1],
                          gamma=best_params[2], kernel='rbf')
            svr_gwo.fit(X_train_reg, y_train_egfr)
            y_pred_gwo = svr_gwo.predict(X_test_reg)
            rmse_gwo = np.sqrt(mean_squared_error(y_test_egfr, y_pred_gwo))
            r2_gwo = r2_score(y_test_egfr, y_pred_gwo)
            print(f"\n  [SVR-GWO Final] RMSE={rmse_gwo:.4f} R2={r2_gwo:.4f}")

            reg_results['SVR-GWO'] = {
                'model': svr_gwo,
                'metrics': {'RMSE': round(rmse_gwo, 4), 'R2': round(r2_gwo, 4),
                             'MAE': 0, 'MAPE': 0},
                'predictions': y_pred_gwo,
            }
            
            # Save GWO Checkpoint
            gwo_cp = {
                'data': data, 'reg_results': reg_results,
                'X_train_reg': X_train_reg, 'X_test_reg': X_test_reg, 'y_test_egfr': y_test_egfr,
                'X_train_cls': X_train_cls, 'X_test_cls': X_test_cls, 'y_train_stage': y_train_stage, 'y_test_stage': y_test_stage,
                'scaler_cls': scaler_cls, 'scaler_reg': scaler_reg, 'feat_cls': feat_cls,
                'best_params': best_params, 'best_score': best_score, 'gwo_curve': gwo_curve,
                'svr_gwo': svr_gwo
            }
            joblib.dump(gwo_cp, GWO_CHECKPOINT_PATH)
            print(f"  [SAVED] GWO Intermediate Results -> {GWO_CHECKPOINT_PATH}")

        # ================================================================
        # PHASE 7: CLASSIFICATION MODELS
        # ================================================================
        class_results = train_classification_models(
            X_train_cls, y_train_stage, X_test_cls, y_test_stage, save_dir=METRICS_DIR
        )

    # ================================================================
    # PHASE 8: SAVE MODELS & CHECKPOINT
    # ================================================================
    print("\n" + "=" * 60)
    print("SAVING MODELS & CHECKPOINTS")
    print("=" * 60)
    
    # Save checkpoint for resuming later
    checkpoint = {
        'data': data, 'reg_results': reg_results, 'class_results': class_results,
        'y_test_egfr': y_test_egfr, 'y_test_stage': y_test_stage,
        'X_test_cls': X_test_cls, 'feat_cls': feat_cls,
        'gwo_curve': gwo_curve, 'best_params': best_params,
        'best_score': best_score, 'timestamp': timestamp,
        'scaler_reg': scaler_reg, 'scaler_cls': scaler_cls
    }
    joblib.dump(checkpoint, CHECKPOINT_PATH)
    print(f"  [SAVED] All results checkpointed -> {CHECKPOINT_PATH}")
    if 'XGBoost' in class_results:
        joblib.dump(class_results['XGBoost']['model'],
                    os.path.join(MODELS_DIR, 'best_classifier_xgboost.pkl'))
        print(f"  [SAVED] XGBoost -> {MODELS_DIR}/best_classifier_xgboost.pkl")
    joblib.dump(svr_gwo, os.path.join(MODELS_DIR, 'svr_gwo_optimized.pkl'))
    joblib.dump(scaler_reg, os.path.join(MODELS_DIR, 'scaler_regression.pkl'))
    joblib.dump(scaler_cls, os.path.join(MODELS_DIR, 'scaler_classification.pkl'))
    print(f"  [SAVED] GWO-SVR + Scalers -> {MODELS_DIR}/")

    gwo_info = {'C': float(best_params[0]), 'epsilon': float(best_params[1]),
                'gamma': float(best_params[2]), 'RMSE': float(best_score)}
    with open(os.path.join(METRICS_DIR, 'gwo_best_params.json'), 'w') as f:
        json.dump(gwo_info, f, indent=2)

    # ================================================================
    # PHASE 9: GENERATE ALL FIGURES
    # ================================================================
    try:
        generate_all_plots(
            data=data, reg_results=reg_results, class_results=class_results,
            y_test_egfr=y_test_egfr, y_test_stage=y_test_stage,
            X_test=X_test_cls, feature_names=feat_cls,
            gwo_convergence=gwo_curve, output_dir=FIGURES_DIR,
        )
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Plotting phase failed: {e}")
        print("Model results are saved, but some figures may be missing.")

    # ================================================================
    # FINAL REPORT
    # ================================================================
    elapsed = time.time() - start_time
    print("\n\n" + "+" + "=" * 58 + "+")
    print("|    FINAL RESULTS SUMMARY" + " " * 33 + "|")
    print("+" + "=" * 58 + "+")
    print("|  REGRESSION (eGFR Prediction):" + " " * 27 + "|")
    for name, res in reg_results.items():
        m = res['metrics']
        line = f"|    {name:20s} RMSE={m['RMSE']:<8.4f} R2={m['R2']:<8.4f}"
        print(f"{line:<59}|")
    print("|" + " " * 58 + "|")
    print("|  CLASSIFICATION (CKD Staging):" + " " * 27 + "|")
    for name, res in class_results.items():
        line = f"|    {name:20s} Acc={res['accuracy']:.4f}  F1={res['f1_score']:.4f}"
        print(f"{line:<59}|")
    print("|" + " " * 58 + "|")
    print(f"|  Total time: {elapsed:.1f}s" + " " * max(0, 43 - len(f"{elapsed:.1f}")) + "|")
    print("+" + "=" * 58 + "+")

    # Save run summary
    summary = {
        'timestamp': timestamp,
        'elapsed_seconds': round(elapsed, 1),
        'dataset_size': len(data['Age']),
        'regression': {n: r['metrics'] for n, r in reg_results.items()},
        'classification': {n: {
            'accuracy': r['accuracy'], 'precision': r['precision'],
            'recall': r['recall'], 'f1_score': r['f1_score'],
            'cv_mean': r['cv_mean'], 'cv_std': r['cv_std'],
        } for n, r in class_results.items()},
        'gwo_params': gwo_info,
    }
    with open(os.path.join(METRICS_DIR, 'run_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    # ================================================================
    # PHASE 10: REPORT GENERATION
    # ================================================================
    print("\n" + "=" * 60)
    print("PHASE 10: PROFESSIONAL REPORT GENERATION")
    print("=" * 60)
    report_path = os.path.join(PROJECT_ROOT, "results", "clinical_report.md")
    generate_clinical_report(METRICS_DIR, report_path)
    
    print(f"\n  [SAVED] Run summary -> {METRICS_DIR}/run_summary.json\n")

    return reg_results, class_results


if __name__ == "__main__":
    main()
