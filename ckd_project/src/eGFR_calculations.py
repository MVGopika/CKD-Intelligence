"""
eGFR Calculation Module (No Pandas)
====================================
Implements the three CKD-EPI 2021 equations for estimating GFR.
All functions work with numpy arrays.
"""

import numpy as np


def calculate_eGFR_scr(scr, age, sex_labels):
    """CKD-EPI 2021 Creatinine equation."""
    scr = np.asarray(scr, dtype=float)
    age = np.asarray(age, dtype=float)
    if isinstance(sex_labels, str):
        is_female = np.array([sex_labels == 'female'])
    else:
        is_female = np.array([s == 'female' for s in sex_labels])

    kappa = np.where(is_female, 0.7, 0.9)
    alpha = np.where(is_female, -0.241, -0.302)
    sex_coeff = np.where(is_female, 1.012, 1.0)

    scr_k = scr / kappa
    min_part = np.minimum(scr_k, 1.0) ** alpha
    max_part = np.maximum(scr_k, 1.0) ** (-1.200)
    egfr = 142.0 * min_part * max_part * (0.9938 ** age) * sex_coeff
    return np.round(egfr, 2)


def calculate_eGFR_cysc(cysc, age, sex_labels):
    """CKD-EPI 2021 Cystatin C equation."""
    cysc = np.asarray(cysc, dtype=float)
    age = np.asarray(age, dtype=float)
    if isinstance(sex_labels, str):
        is_female = np.array([sex_labels == 'female'])
    else:
        is_female = np.array([s == 'female' for s in sex_labels])

    sex_coeff = np.where(is_female, 0.932, 1.0)
    cysc_08 = cysc / 0.8
    min_part = np.minimum(cysc_08, 1.0) ** (-0.499)
    max_part = np.maximum(cysc_08, 1.0) ** (-1.328)
    egfr = 133.0 * min_part * max_part * (0.996 ** age) * sex_coeff
    return np.round(egfr, 2)


def calculate_eGFR_combined(scr, cysc, age, sex_labels):
    """CKD-EPI 2021 Combined Creatinine-Cystatin C equation."""
    scr = np.asarray(scr, dtype=float)
    cysc = np.asarray(cysc, dtype=float)
    age = np.asarray(age, dtype=float)
    if isinstance(sex_labels, str):
        is_female = np.array([sex_labels == 'female'])
    else:
        is_female = np.array([s == 'female' for s in sex_labels])

    kappa = np.where(is_female, 0.7, 0.9)
    beta = np.where(is_female, -0.219, -0.144)
    sex_coeff = np.where(is_female, 0.963, 1.0)

    scr_k = scr / kappa
    min_scr = np.minimum(scr_k, 1.0) ** beta
    max_scr = np.maximum(scr_k, 1.0) ** (-0.544)
    cysc_08 = cysc / 0.8
    min_cysc = np.minimum(cysc_08, 1.0) ** (-0.323)
    max_cysc = np.maximum(cysc_08, 1.0) ** (-0.778)
    egfr = 135.0 * min_scr * max_scr * min_cysc * max_cysc * (0.9961 ** age) * sex_coeff
    return np.round(egfr, 2)


def assign_ckd_stage(egfr):
    """Assign KDIGO CKD stage based on eGFR (vectorized)."""
    egfr = np.asarray(egfr, dtype=float)
    conditions = [egfr >= 90, egfr >= 60, egfr >= 30, egfr >= 15]
    choices = [1, 2, 3, 4]
    return np.select(conditions, choices, default=5).astype(int)


def compute_all_egfr(data):
    """
    Compute all three eGFR values and CKD stage for a data dict.
    Adds eGFR_SCr, eGFR_SCysC, eGFR_Combined, CKD_Stage to data.
    """
    data['eGFR_SCr'] = calculate_eGFR_scr(data['SCr'], data['Age'], data['Sex'])
    data['eGFR_SCysC'] = calculate_eGFR_cysc(data['SCysC'], data['Age'], data['Sex'])
    data['eGFR_Combined'] = calculate_eGFR_combined(
        data['SCr'], data['SCysC'], data['Age'], data['Sex']
    )
    data['CKD_Stage'] = assign_ckd_stage(data['eGFR_Combined'])

    n = len(data['CKD_Stage'])
    unique, counts = np.unique(data['CKD_Stage'], return_counts=True)
    print(f"[eGFR] Computed 3 eGFR variants + CKD staging for {n} patients")
    for s, c in zip(unique, counts):
        print(f"  Stage {s}: {c} ({c/n*100:.1f}%)")
    return data
