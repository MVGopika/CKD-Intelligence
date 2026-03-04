"""
Synthetic CKD Data Generator
=============================
Generates realistic synthetic patient data for CKD detection & staging.
Uses only numpy + csv (no pandas dependency).
"""

import numpy as np
import csv
import os


def generate_synthetic_ckd_data(n_samples=5000, random_state=42, output_path=None):
    """
    Generate a synthetic CKD dataset with realistic clinical distributions.
    Returns a dict of {column_name: numpy_array} and a list of column names.
    """
    rng = np.random.RandomState(random_state)

    # Stage distribution (mimic real-world prevalence)
    stage_probs = [0.30, 0.30, 0.25, 0.10, 0.05]
    stages = rng.choice([1, 2, 3, 4, 5], size=n_samples, p=stage_probs)

    # eGFR ranges per stage
    egfr_ranges = {1: (90, 140), 2: (60, 89), 3: (30, 59), 4: (15, 29), 5: (3, 14)}
    egfr_values = np.zeros(n_samples)
    for stage in range(1, 6):
        mask = stages == stage
        low, high = egfr_ranges[stage]
        egfr_values[mask] = rng.uniform(low, high, size=mask.sum())

    # Demographics
    age = np.clip(rng.normal(58, 15, n_samples), 18, 95).astype(int)
    for stage in [3, 4, 5]:
        mask = stages == stage
        age[mask] = np.clip(rng.normal(65 + stage * 2, 10, mask.sum()), 30, 95).astype(int)

    sex_codes = rng.choice([0, 1], size=n_samples, p=[0.52, 0.48])  # 0=male, 1=female
    sex_labels = np.where(sex_codes == 1, 'female', 'male')

    # Derive SCr from eGFR using inverse CKD-EPI SCr equation
    kappa = np.where(sex_codes == 1, 0.7, 0.9)
    sex_coeff_scr = np.where(sex_codes == 1, 1.012, 1.0)
    base_scr = egfr_values / (142 * sex_coeff_scr * (0.9938 ** age))
    scr = kappa * (1 / base_scr) ** (1 / 1.200)
    scr = np.maximum(0.3, scr + rng.normal(0, 0.05, n_samples))

    # Derive SCysC from eGFR using inverse CKD-EPI SCysC equation
    sex_coeff_cysc = np.where(sex_codes == 1, 0.932, 1.0)
    base_cysc = egfr_values / (133 * sex_coeff_cysc * (0.996 ** age))
    scysc = 0.8 * (1 / base_cysc) ** (1 / 1.328)
    scysc = np.maximum(0.3, scysc + rng.normal(0, 0.03, n_samples))

    # BMI
    bmi = np.clip(rng.normal(27, 5, n_samples), 16, 50)
    for stage in [4, 5]:
        mask = stages == stage
        bmi[mask] = np.clip(rng.normal(25, 6, mask.sum()), 16, 50)

    # Blood Pressure
    sbp_base = {1: 120, 2: 128, 3: 138, 4: 148, 5: 155}
    dbp_base = {1: 78, 2: 82, 3: 85, 4: 88, 5: 90}
    sbp = np.zeros(n_samples)
    dbp = np.zeros(n_samples)
    for stage in range(1, 6):
        mask = stages == stage
        sbp[mask] = np.clip(rng.normal(sbp_base[stage], 12, mask.sum()), 90, 200)
        dbp[mask] = np.clip(rng.normal(dbp_base[stage], 8, mask.sum()), 50, 120)

    # HbA1c
    hba1c_base = {1: 5.4, 2: 5.7, 3: 6.2, 4: 6.8, 5: 7.2}
    hba1c = np.zeros(n_samples)
    for stage in range(1, 6):
        mask = stages == stage
        hba1c[mask] = np.clip(rng.normal(hba1c_base[stage], 0.8, mask.sum()), 4.0, 12.0)

    # Albumin
    alb_base = {1: 4.2, 2: 4.0, 3: 3.7, 4: 3.3, 5: 2.8}
    alb = np.zeros(n_samples)
    for stage in range(1, 6):
        mask = stages == stage
        alb[mask] = np.clip(rng.normal(alb_base[stage], 0.4, mask.sum()), 1.5, 5.5)

    # CRP
    crp_base = {1: 1.5, 2: 2.5, 3: 4.0, 4: 7.0, 5: 12.0}
    crp = np.zeros(n_samples)
    for stage in range(1, 6):
        mask = stages == stage
        crp[mask] = np.clip(rng.exponential(crp_base[stage], mask.sum()), 0.1, 50.0)

    # Build data dict
    columns = ['Age', 'Sex', 'Sex_encoded', 'BMI', 'SCr', 'SCysC',
               'SBP', 'DBP', 'HbA1c', 'Alb', 'CRP', 'eGFR_true', 'CKD_Stage_true']
    data = {
        'Age': age,
        'Sex': sex_labels,
        'Sex_encoded': sex_codes,
        'BMI': np.round(bmi, 1),
        'SCr': np.round(scr, 3),
        'SCysC': np.round(scysc, 3),
        'SBP': np.round(sbp, 0).astype(int),
        'DBP': np.round(dbp, 0).astype(int),
        'HbA1c': np.round(hba1c, 1),
        'Alb': np.round(alb, 2),
        'CRP': np.round(crp, 2),
        'eGFR_true': np.round(egfr_values, 2),
        'CKD_Stage_true': stages,
    }

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for i in range(n_samples):
                writer.writerow([data[col][i] for col in columns])
        print(f"[INFO] Saved {n_samples} synthetic records -> {output_path}")
        unique, counts = np.unique(stages, return_counts=True)
        for s, c in zip(unique, counts):
            print(f"  Stage {s}: {c} ({c/n_samples*100:.1f}%)")

    return data, columns


if __name__ == "__main__":
    generate_synthetic_ckd_data(
        n_samples=5000, random_state=42, output_path="data/raw/ckd_data.csv"
    )
