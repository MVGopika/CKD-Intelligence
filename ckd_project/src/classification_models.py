"""
Classification Models Module
==============================
Trains and evaluates multiple classifiers for CKD stage prediction:
    - Support Vector Machine (SVM) with polynomial kernel
    - Decision Tree (entropy)
    - Random Forest (entropy)
    - XGBoost

Uses SMOTE for class imbalance handling and 5-fold Stratified Cross-Validation.
"""

import numpy as np
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, classification_report, confusion_matrix)
from sklearn.model_selection import StratifiedKFold
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import json
import os


def get_model_configs():
    """Return dictionary of model name → sklearn estimator."""
    return {
        'SVM': SVC(
            kernel='poly', C=1, gamma='scale', degree=3,
            probability=True, random_state=42
        ),
        'Decision Tree': DecisionTreeClassifier(
            criterion='entropy', max_depth=20,
            min_samples_split=5, min_samples_leaf=4,
            random_state=42
        ),
        'Random Forest': RandomForestClassifier(
            criterion='entropy', n_estimators=200,
            max_depth=20, min_samples_split=5,
            n_jobs=-1, random_state=42
        ),
        'XGBoost': XGBClassifier(
            n_estimators=300, max_depth=15,
            learning_rate=0.1, subsample=0.8,
            colsample_bytree=0.9, gamma=0.2,
            eval_metric='mlogloss', random_state=42
        ),
    }


def train_classification_models(X_train, y_train, X_test, y_test, save_dir=None):
    """
    Train and evaluate multiple classifiers for CKD staging.
    
    Parameters
    ----------
    X_train, y_train : training data (numpy arrays)
    X_test, y_test : test data
    save_dir : str or None
        If provided, saves metrics and classification reports.

    Returns
    -------
    dict : model name → {model, accuracy, precision, recall, f1_score, 
                          cv_mean, cv_std, predictions, confusion_matrix}
    """
    print("\n" + "="*60)
    print("CLASSIFICATION MODELS — CKD Stage Prediction")
    print("="*60)

    models = get_model_configs()
    results = {}
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for name, model in models.items():
        print(f"\n  Training {name}...")

        # Determine SMOTE neighbors based on minority class size
        unique, counts = np.unique(y_train, return_counts=True)
        min_samples = np.min(counts)
        k_neigh = min(3, max(1, min_samples - 1))
        
        # Build pipeline: SMOTE → Classifier
        pipeline = ImbPipeline([
            ('smote', SMOTE(random_state=42, k_neighbors=k_neigh)),
            ('classifier', model)
        ])

        # ---- 5-Fold Cross Validation on Training Set ----
        cv_scores = []
        try:
            for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
                X_tr, X_val = X_train[train_idx], X_train[val_idx]
                y_tr, y_val = y_train[train_idx], y_train[val_idx]

                pipeline.fit(X_tr, y_tr)
                y_pred_val = pipeline.predict(X_val)
                fold_f1 = f1_score(y_val, y_pred_val, average='weighted', zero_division=0)
                cv_scores.append(fold_f1)
        except Exception as e:
            print(f"    [WARN] CV failed for {name}: {e}")
            cv_scores = [0.0]

        # ---- Final Training on Full Training Set ----
        try:
            pipeline.fit(X_train, y_train)
        except Exception as e:
            print(f"    [ERROR] Final training failed for {name}: {e}")
            continue

        # ---- Test Set Evaluation ----
        y_pred = pipeline.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        cm = confusion_matrix(y_test, y_pred)
        report = classification_report(y_test, y_pred, zero_division=0)

        results[name] = {
            'model': pipeline,
            'accuracy': round(acc, 4),
            'precision': round(prec, 4),
            'recall': round(rec, 4),
            'f1_score': round(f1, 4),
            'cv_mean': round(np.mean(cv_scores), 4),
            'cv_std': round(np.std(cv_scores), 4),
            'predictions': y_pred,
            'confusion_matrix': cm,
            'classification_report': report,
        }

        print(f"    CV F1 = {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}")
        print(f"    Test → Acc={acc:.4f}  Prec={prec:.4f}  Rec={rec:.4f}  F1={f1:.4f}")

    # ---- Save metrics ----
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        metrics_out = {}
        for name, res in results.items():
            metrics_out[name] = {
                'accuracy': res['accuracy'],
                'precision': res['precision'],
                'recall': res['recall'],
                'f1_score': res['f1_score'],
                'cv_mean': res['cv_mean'],
                'cv_std': res['cv_std'],
            }
        with open(os.path.join(save_dir, "classification_metrics.json"), 'w') as f:
            json.dump(metrics_out, f, indent=2)

        # Save classification reports
        with open(os.path.join(save_dir, "classification_reports.txt"), 'w') as f:
            for name, res in results.items():
                f.write(f"\n{'='*50}\n{name}\n{'='*50}\n")
                f.write(res['classification_report'])
                f.write("\n")
        print(f"\n  [SAVED] Classification metrics → {save_dir}/")

    return results
