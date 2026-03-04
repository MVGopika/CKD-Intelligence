"""
Data Preprocessing Module (No Pandas)
======================================
Uses numpy + csv for data loading and preprocessing.
"""

import numpy as np
import csv
import os
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


def load_csv_to_dict(filepath):
    """Load a CSV file into a dict of {column: numpy_array}."""
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        data = {col: [] for col in columns}
        for row in reader:
            for col in columns:
                data[col].append(row[col])

    # Convert to numpy arrays with appropriate types
    numeric_cols = ['Age', 'BMI', 'SCr', 'SCysC', 'SBP', 'DBP',
                    'HbA1c', 'Alb', 'CRP', 'Sex_encoded',
                    'eGFR_true', 'CKD_Stage_true',
                    'eGFR_SCr', 'eGFR_SCysC', 'eGFR_Combined', 'CKD_Stage']
    for col in columns:
        if col in numeric_cols or col not in ['Sex']:
            try:
                data[col] = np.array(data[col], dtype=float)
            except ValueError:
                data[col] = np.array(data[col])
        else:
            data[col] = np.array(data[col])

    return data, columns


def save_dict_to_csv(data, columns, filepath):
    """Save a dict of arrays to CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    n = len(data[columns[0]])
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for i in range(n):
            writer.writerow([data[col][i] for col in columns])


def load_and_preprocess_data(filepath, save_processed=True):
    """
    Load raw CKD data, clean it, encode categoricals.
    Returns data dict and column names.
    """
    print(f"[PREPROCESS] Loading data from {filepath}...")
    data, columns = load_csv_to_dict(filepath)
    n_samples = len(data[columns[0]])
    print(f"[PREPROCESS] Raw shape: {n_samples} samples x {len(columns)} features")

    # Encode Sex if not already encoded
    if 'Sex' in columns and 'Sex_encoded' not in columns:
        sex_encoded = np.array([1 if s == 'female' else 0 for s in data['Sex']], dtype=float)
        data['Sex_encoded'] = sex_encoded
        columns = list(columns) + ['Sex_encoded']
        print("[PREPROCESS] Encoded Sex -> Sex_encoded (female=1, male=0)")

    # Save processed data
    if save_processed:
        out_dir = os.path.join(os.path.dirname(os.path.dirname(filepath)), "processed")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "ckd_data_processed.csv")
        save_dict_to_csv(data, columns, out_path)
        print(f"[PREPROCESS] Saved processed data -> {out_path}")

    return data, columns


def prepare_features(data, feature_cols, target_col, test_size=0.3, random_state=42):
    """
    Build feature matrix X and target y, split, and scale.
    Returns X_train, X_test, y_train, y_test, scaler, used_feature_names.
    """
    available = [c for c in feature_cols if c in data]
    missing = [c for c in feature_cols if c not in data]
    if missing:
        print(f"[PREPROCESS] Warning - missing features: {missing}")

    X = np.column_stack([data[c] for c in available])
    y = data[target_col].astype(int) if target_col.endswith('Stage') else data[target_col].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state,
        stratify=y if target_col.endswith('Stage') else None
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    print(f"[PREPROCESS] Train: {X_train.shape[0]} | Test: {X_test.shape[0]} | Features: {len(available)}")
    return X_train, X_test, y_train, y_test, scaler, available
