# ML Framework for Early Detection of Chronic Kidney Disease (CKD) Stages

A complete machine learning pipeline for **CKD detection and staging** using CKD-EPI 2021 equations, Grey Wolf Optimizer (GWO) hyperparameter tuning, ensemble classifiers, and SHAP explainability.

---

## 🏗 Project Structure

```
ckd_project/
├── main.py                          # One-command full pipeline
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── src/                             # Core source code
│   ├── generate_synthetic_data.py   # Realistic CKD patient data generator
│   ├── data_preprocessing.py        # Loading, cleaning, scaling
│   ├── eGFR_calculations.py         # CKD-EPI 2021 (SCr, SCysC, Combined)
│   ├── regression_models.py         # Linear Regression + SVR
│   ├── gwo_optimizer.py             # Grey Wolf Optimizer for SVR tuning
│   ├── classification_models.py     # SVM, Decision Tree, Random Forest, XGBoost
│   └── visualization.py            # 11+ publication-quality figure generators
│
├── data/
│   ├── raw/                         # Original dataset (auto-generated if missing)
│   └── processed/                   # Cleaned + eGFR-computed dataset
│
├── models/saved_models/             # Trained model artifacts (.pkl)
│
├── results/
│   ├── figures/                     # All generated plots (PNG)
│   └── metrics/                     # JSON metrics + classification reports
│
└── notebooks/                       # Analysis scripts
    ├── 01_eda.py
    └── 05_shap_analysis.py
```

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the complete pipeline
python main.py
```

That's it! The pipeline will:
1. **Generate 5,000 synthetic patients** (if no data exists in `data/raw/`)
2. **Preprocess** the data (outlier removal, encoding, scaling)
3. **Compute eGFR** using three CKD-EPI 2021 equations
4. **Train regression models** (Linear Regression, SVR)
5. **Optimize SVR** with the Grey Wolf Optimizer
6. **Train classifiers** (SVM, Decision Tree, Random Forest, XGBoost with SMOTE)
7. **Generate 11+ figures** (correlation matrix, ROC curves, SHAP plots, etc.)
8. **Save** all models, metrics, and reports

---

## 📊 Pipeline Overview

```
Raw Data → Preprocessing → eGFR Computation → Feature Engineering
                                                       │
                              ┌─────────────────────────┼────────────────────┐
                              ▼                         ▼                    ▼
                        Regression              GWO Optimization      Classification
                       (LR, SVR)                  (SVR tuning)      (SVM, DT, RF, XGB)
                              │                         │                    │
                              └─────────────────────────┼────────────────────┘
                                                        ▼
                                              Visualization + SHAP
                                                        ▼
                                               Results & Reports
```

---

## 🧬 Key Components

### eGFR Equations (CKD-EPI 2021)
| Equation | Biomarkers | Reference |
|----------|-----------|-----------|
| CKD-EPI SCr | Serum Creatinine, Age, Sex | Inker et al. NEJM 2021 |
| CKD-EPI SCysC | Cystatin C, Age, Sex | Inker et al. NEJM 2021 |
| CKD-EPI Combined | SCr + SCysC, Age, Sex | Inker et al. NEJM 2021 |

### CKD Staging (KDIGO)
| Stage | eGFR Range | Description |
|-------|-----------|-------------|
| 1 | ≥ 90 | Normal or high |
| 2 | 60–89 | Mildly decreased |
| 3 | 30–59 | Moderately decreased |
| 4 | 15–29 | Severely decreased |
| 5 | < 15 | Kidney failure |

### Models Used
- **Regression**: Linear Regression, SVR (RBF), GWO-optimized SVR
- **Classification**: SVM (poly), Decision Tree, Random Forest, XGBoost
- **Balancing**: SMOTE for class imbalance
- **Validation**: 5-fold Stratified Cross-Validation
- **Explainability**: SHAP (TreeExplainer)

---

## 📈 Generated Figures

| Figure | Description | Paper Reference |
|--------|------------|-----------------|
| `correlation_matrix.png` | Pearson correlation heatmap | Figure 3 |
| `egfr_distribution_by_stage.png` | eGFR violin plots by CKD stage | Figure 2, 4, 6 |
| `bland_altman_*.png` | Agreement between eGFR methods | Figure 7 |
| `confusion_matrices.png` | Multi-model confusion matrices | Figure 8 |
| `roc_curves.png` | One-vs-Rest ROC curves | Figure 8 |
| `model_comparison.png` | Metrics comparison bar chart | Table 5 |
| `gwo_convergence.png` | GWO optimization convergence | — |
| `regression_scatter.png` | Predicted vs actual eGFR | — |
| `feature_distributions.png` | Biomarker distributions by stage | — |
| `stage_distribution.png` | CKD stage prevalence | — |
| `shap_summary_bar.png` | SHAP global feature importance | Figure 9 |
| `shap_beeswarm.png` | SHAP beeswarm plot | Figure 10 |
| `shap_waterfall.png` | SHAP waterfall (single prediction) | Figure 11 |

---

## 📁 Output Files

After running `main.py`, you will find:

```
results/
├── figures/                    # 13 PNG plots
├── metrics/
│   ├── regression_metrics.json
│   ├── classification_metrics.json
│   ├── classification_reports.txt
│   ├── gwo_best_params.json
│   └── run_summary.json

models/saved_models/
├── best_classifier_xgboost.pkl
├── svr_gwo_optimized.pkl
├── scaler_regression.pkl
└── scaler_classification.pkl
```

---

## 🛠 Requirements

- Python 3.8+
- See `requirements.txt` for full dependency list

---

## 📚 References

1. Inker, L.A. et al. "New Creatinine- and Cystatin C–Based Equations to Estimate GFR without Race." *NEJM*, 2021.
2. Mirjalili, S. et al. "Grey Wolf Optimizer." *Advances in Engineering Software*, 2014.
3. Lundberg, S.M. & Lee, S.I. "A Unified Approach to Interpreting Model Predictions." *NeurIPS*, 2017 (SHAP).
4. KDIGO 2012 Clinical Practice Guideline for the Evaluation and Management of CKD.
