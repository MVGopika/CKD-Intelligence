"""
Visualization Module (Pure Matplotlib)
========================================
No seaborn/pandas dependency. All plots use matplotlib only.
Generates 11+ publication-quality figures.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.preprocessing import label_binarize
import os
import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'figure.dpi': 150, 'savefig.dpi': 150, 'font.size': 11,
    'axes.titlesize': 13, 'axes.labelsize': 11,
    'figure.figsize': (10, 7), 'savefig.bbox': 'tight',
    'font.family': 'sans-serif',
})

STAGE_COLORS = {1: '#2ecc71', 2: '#3498db', 3: '#f39c12', 4: '#e74c3c', 5: '#8e44ad'}


def save_fig(fig, path, name):
    os.makedirs(path, exist_ok=True)
    filepath = os.path.join(path, name)
    fig.savefig(filepath)
    plt.close(fig)
    print(f"    [PLOT] Saved -> {filepath}")


# 1. CORRELATION HEATMAP
def plot_correlation_matrix(data, output_dir):
    cols = ['SCr', 'SCysC', 'Age', 'BMI', 'HbA1c', 'SBP', 'DBP', 'CRP', 'Alb']
    available = [c for c in cols if c in data]
    matrix = np.column_stack([data[c].astype(float) for c in available])
    corr = np.corrcoef(matrix, rowvar=False)
    n = len(available)

    fig, ax = plt.subplots(figsize=(10, 8))
    # Mask upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    masked_corr = np.ma.array(corr, mask=mask)

    cmap = plt.cm.RdBu_r
    im = ax.imshow(masked_corr, cmap=cmap, vmin=-1, vmax=1, aspect='equal')
    plt.colorbar(im, ax=ax, label='Pearson Correlation', shrink=0.8)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(available, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(available, fontsize=9)

    # Annotate
    for i in range(n):
        for j in range(n):
            if not mask[i, j]:
                ax.text(j, i, f'{corr[i, j]:.2f}', ha='center', va='center',
                        fontsize=8, color='white' if abs(corr[i, j]) > 0.6 else 'black')

    ax.set_title('Correlation Matrix of Clinical Biomarkers', fontweight='bold', pad=15)
    save_fig(fig, output_dir, 'correlation_matrix.png')


# 2. eGFR DISTRIBUTION BY STAGE
def plot_egfr_distributions(data, output_dir):
    egfr_cols = ['eGFR_SCr', 'eGFR_SCysC', 'eGFR_Combined']
    titles = ['CKD-EPI SCr', 'CKD-EPI SCysC', 'CKD-EPI Combined']
    available = [(c, t) for c, t in zip(egfr_cols, titles) if c in data]
    if not available:
        return

    stage_col = 'CKD_Stage' if 'CKD_Stage' in data else 'CKD_Stage_true'
    stages = data[stage_col].astype(int)
    unique_stages = sorted(np.unique(stages))

    fig, axes = plt.subplots(1, len(available), figsize=(6 * len(available), 6))
    if len(available) == 1:
        axes = [axes]

    for idx, (col, title) in enumerate(available):
        vals = data[col].astype(float)
        box_data = [vals[stages == s] for s in unique_stages]
        bp = axes[idx].boxplot(box_data, patch_artist=True,
                                labels=[str(s) for s in unique_stages],
                                widths=0.6, showfliers=True,
                                flierprops={'markersize': 2, 'alpha': 0.3})
        for patch, stage in zip(bp['boxes'], unique_stages):
            patch.set_facecolor(STAGE_COLORS.get(stage, '#999'))
            patch.set_alpha(0.7)
        axes[idx].set_title(title, fontweight='bold')
        axes[idx].set_xlabel('CKD Stage')
        axes[idx].set_ylabel('eGFR (mL/min/1.73m\u00B2)')
        # Stage boundary lines
        for y, c in [(90, '#27ae60'), (60, '#f39c12'), (30, '#e74c3c'), (15, '#8e44ad')]:
            axes[idx].axhline(y=y, color=c, linestyle='--', alpha=0.5, linewidth=0.8)
        axes[idx].grid(True, axis='y', alpha=0.2)

    fig.suptitle('eGFR Distribution by CKD Stage', fontweight='bold', fontsize=14, y=1.02)
    plt.tight_layout()
    save_fig(fig, output_dir, 'egfr_distribution_by_stage.png')


# 3. BLAND-ALTMAN PLOT
def plot_bland_altman(method1, method2, title, output_dir, filename='bland_altman.png'):
    mean_vals = (method1 + method2) / 2
    diff_vals = method1 - method2
    mean_diff = np.mean(diff_vals)
    std_diff = np.std(diff_vals)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(mean_vals, diff_vals, alpha=0.25, s=10, color='#3498db', edgecolors='none')
    ax.axhline(mean_diff, color='#e74c3c', linestyle='-', linewidth=1.5,
               label=f'Mean: {mean_diff:.2f}')
    ax.axhline(mean_diff + 1.96*std_diff, color='#7f8c8d', linestyle='--', linewidth=1,
               label=f'+1.96SD: {mean_diff+1.96*std_diff:.2f}')
    ax.axhline(mean_diff - 1.96*std_diff, color='#7f8c8d', linestyle='--', linewidth=1,
               label=f'-1.96SD: {mean_diff-1.96*std_diff:.2f}')
    ax.set_xlabel('Mean of Two Methods (mL/min/1.73m\u00B2)')
    ax.set_ylabel('Difference (Method 1 - Method 2)')
    ax.set_title(f'Bland-Altman: {title}', fontweight='bold')
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(True, alpha=0.3)
    save_fig(fig, output_dir, filename)


# 4. CONFUSION MATRICES
def plot_confusion_matrices(results, y_test, output_dir, classes=None):
    if classes is None:
        classes = sorted(np.unique(y_test))
    n_models = len(results)
    fig, axes = plt.subplots(1, n_models, figsize=(5 * n_models, 4.5))
    if n_models == 1:
        axes = [axes]

    for idx, (name, res) in enumerate(results.items()):
        cm = confusion_matrix(y_test, res['predictions'], labels=classes)
        im = axes[idx].imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.colorbar(im, ax=axes[idx], shrink=0.8)
        axes[idx].set(xticks=range(len(classes)), yticks=range(len(classes)),
                      xticklabels=classes, yticklabels=classes)
        axes[idx].set_xlabel('Predicted')
        axes[idx].set_ylabel('True')
        axes[idx].set_title(f'{name}\nAcc={res["accuracy"]:.3f} F1={res["f1_score"]:.3f}',
                            fontweight='bold', fontsize=10)
        # Annotate
        thresh = cm.max() / 2
        for i in range(len(classes)):
            for j in range(len(classes)):
                axes[idx].text(j, i, format(cm[i, j], 'd'), ha='center', va='center',
                               color='white' if cm[i, j] > thresh else 'black', fontsize=9)

    fig.suptitle('Confusion Matrices - CKD Stage Classification', fontweight='bold', y=1.02)
    plt.tight_layout()
    save_fig(fig, output_dir, 'confusion_matrices.png')


# 5. ROC CURVES
def plot_roc_curves(results, X_test, y_test, output_dir, classes=None):
    if classes is None:
        # Collect ALL class labels seen in test + predictions to avoid binarize mismatch
        all_labels = list(np.unique(y_test))
        for res in results.values():
            preds = res.get('predictions', [])
            if len(preds):
                for lbl in np.unique(preds):
                    if lbl not in all_labels:
                        all_labels.append(lbl)
        classes = sorted(all_labels)

    try:
        y_test_bin = label_binarize(y_test, classes=classes)
    except Exception as e:
        print(f"    [WARN] ROC binarize failed: {e}")
        return

    colors_roc = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#8e44ad']

    fig, axes = plt.subplots(1, len(results), figsize=(6 * len(results), 5))
    if len(results) == 1:
        axes = [axes]

    for idx, (name, res) in enumerate(results.items()):
        model = res['model']
        try:
            y_score = model.predict_proba(X_test)
            # Align score columns to our full class list
            n_score_classes = y_score.shape[1]
            for i, cls in enumerate(classes):
                if i >= n_score_classes:
                    break
                if y_test_bin.shape[1] <= i:
                    break
                fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_score[:, i])
                roc_auc = auc(fpr, tpr)
                axes[idx].plot(fpr, tpr, linewidth=1.5,
                               color=colors_roc[i % len(colors_roc)],
                               label=f'Stage {cls} (AUC={roc_auc:.3f})')
            axes[idx].plot([0, 1], [0, 1], 'k--', alpha=0.4, linewidth=0.8)
            axes[idx].set_xlabel('False Positive Rate')
            axes[idx].set_ylabel('True Positive Rate')
            axes[idx].set_title(f'{name}', fontweight='bold')
            axes[idx].legend(fontsize=8, loc='lower right')
            axes[idx].grid(True, alpha=0.3)
        except Exception as e:
            print(f"    [WARN] ROC for {name}: {e}")
            axes[idx].text(0.5, 0.5, 'ROC unavailable', ha='center', va='center')
            axes[idx].set_title(f'{name}', fontweight='bold')

    fig.suptitle('ROC Curves - One-vs-Rest per CKD Stage', fontweight='bold', y=1.02)
    plt.tight_layout()
    save_fig(fig, output_dir, 'roc_curves.png')


# 6. GWO CONVERGENCE CURVE
def plot_gwo_convergence(convergence_curve, output_dir):
    fig, ax = plt.subplots(figsize=(8, 5))
    iters = range(1, len(convergence_curve) + 1)
    ax.plot(iters, convergence_curve, 'o-', color='#2c3e50', linewidth=2,
            markersize=6, markerfacecolor='#e74c3c', markeredgecolor='#2c3e50')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Best RMSE')
    ax.set_title('GWO Convergence Curve - SVR Optimization', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.fill_between(iters, convergence_curve, alpha=0.08, color='#3498db')
    save_fig(fig, output_dir, 'gwo_convergence.png')


# 7. MODEL COMPARISON BAR CHART
def plot_model_comparison(results, output_dir):
    metrics_list = ['accuracy', 'precision', 'recall', 'f1_score']
    model_names = list(results.keys())
    x = np.arange(len(model_names))
    width = 0.18
    colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, (metric, color) in enumerate(zip(metrics_list, colors)):
        vals = [results[m][metric] for m in model_names]
        bars = ax.bar(x + i * width, vals, width,
                      label=metric.replace('_', ' ').title(),
                      color=color, alpha=0.85, edgecolor='white', linewidth=0.5)
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f'{h:.3f}', xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', fontsize=7.5)

    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(model_names, fontsize=10)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel('Score')
    ax.set_title('Classification Model Comparison', fontweight='bold')
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, axis='y', alpha=0.3)
    save_fig(fig, output_dir, 'model_comparison.png')


# 8. FEATURE DISTRIBUTIONS
def plot_feature_distributions(data, output_dir):
    features = ['SCr', 'SCysC', 'Age', 'BMI', 'HbA1c', 'SBP', 'Alb', 'CRP']
    available = [f for f in features if f in data]
    stage_col = 'CKD_Stage' if 'CKD_Stage' in data else 'CKD_Stage_true'
    stages = data[stage_col].astype(int)
    unique_stages = sorted(np.unique(stages))

    n_cols = 4
    n_rows = (len(available) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3.5*n_rows))
    axes = axes.flatten()

    for idx, feat in enumerate(available):
        vals = data[feat].astype(float)
        box_data = [vals[stages == s] for s in unique_stages]
        bp = axes[idx].boxplot(box_data, patch_artist=True,
                                labels=[str(s) for s in unique_stages],
                                widths=0.5, showfliers=False)
        for patch, stage in zip(bp['boxes'], unique_stages):
            patch.set_facecolor(STAGE_COLORS.get(stage, '#999'))
            patch.set_alpha(0.7)
        axes[idx].set_title(feat, fontweight='bold', fontsize=10)
        axes[idx].grid(True, axis='y', alpha=0.2)

    for idx in range(len(available), len(axes)):
        axes[idx].set_visible(False)

    fig.suptitle('Feature Distributions by CKD Stage', fontweight='bold', fontsize=14, y=1.01)
    plt.tight_layout()
    save_fig(fig, output_dir, 'feature_distributions.png')


# 9. REGRESSION SCATTER
def plot_regression_results(reg_results, y_test, output_dir):
    fig, axes = plt.subplots(1, len(reg_results), figsize=(6*len(reg_results), 5))
    if len(reg_results) == 1:
        axes = [axes]

    for idx, (name, res) in enumerate(reg_results.items()):
        y_pred = res['predictions']
        axes[idx].scatter(y_test, y_pred, alpha=0.25, s=10, color='#3498db', edgecolors='none')
        mn, mx = min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())
        axes[idx].plot([mn, mx], [mn, mx], 'r--', linewidth=1.5, label='Perfect fit')
        m = res['metrics']
        axes[idx].set_xlabel('Actual eGFR')
        axes[idx].set_ylabel('Predicted eGFR')
        axes[idx].set_title(f'{name}\nRMSE={m["RMSE"]:.2f} R\u00B2={m["R2"]:.4f}',
                            fontweight='bold', fontsize=10)
        axes[idx].legend(fontsize=9)
        axes[idx].grid(True, alpha=0.3)

    fig.suptitle('Regression: Predicted vs Actual eGFR', fontweight='bold', y=1.02)
    plt.tight_layout()
    save_fig(fig, output_dir, 'regression_scatter.png')


# 10. STAGE DISTRIBUTION PIE
def plot_stage_distribution(data, output_dir):
    stage_col = 'CKD_Stage' if 'CKD_Stage' in data else 'CKD_Stage_true'
    stages = data[stage_col].astype(int)
    unique_stages, counts = np.unique(stages, return_counts=True)

    fig, ax = plt.subplots(figsize=(7, 7))
    colors = [STAGE_COLORS.get(s, '#999') for s in unique_stages]
    labels = [f'Stage {s}\n(n={c})' for s, c in zip(unique_stages, counts)]
    wedges, texts, autotexts = ax.pie(counts, labels=labels, colors=colors,
                                       autopct='%1.1f%%', startangle=90,
                                       textprops={'fontsize': 10},
                                       wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
    for t in autotexts:
        t.set_fontweight('bold')
    ax.set_title('CKD Stage Distribution', fontweight='bold', fontsize=14)
    save_fig(fig, output_dir, 'stage_distribution.png')


# 11. SHAP ANALYSIS (lazy import — may fail if pandas DLL is blocked)
def plot_shap_analysis(model, X_test, feature_names, output_dir):
    """Try SHAP analysis. Gracefully skips if shap/pandas can't load."""
    try:
        import shap
        if hasattr(model, 'named_steps'):
            classifier = model.named_steps['classifier']
        else:
            classifier = model

        print("    Computing SHAP values...")
        explainer = shap.TreeExplainer(classifier)
        shap_values = explainer.shap_values(X_test)

        # Manual bar plot of mean |SHAP| values per feature
        if isinstance(shap_values, list):
            # Multi-class: average across classes
            mean_shap = np.mean([np.mean(np.abs(sv), axis=0) for sv in shap_values], axis=0)
        else:
            mean_shap = np.mean(np.abs(shap_values), axis=0)

        # Sort by importance
        sorted_idx = np.argsort(mean_shap)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(sorted_idx)), mean_shap[sorted_idx], color='#3498db', alpha=0.8)
        ax.set_yticks(range(len(sorted_idx)))
        ax.set_yticklabels([feature_names[i] for i in sorted_idx], fontsize=10)
        ax.set_xlabel('Mean |SHAP Value|')
        ax.set_title('SHAP Feature Importance (Global)', fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)
        save_fig(fig, output_dir, 'shap_feature_importance.png')

        return shap_values
    except Exception as e:
        print(f"    [WARN] SHAP analysis skipped (pandas DLL blocked by system policy): {e}")
        
        # Create a manual feature importance plot using model's built-in importance
        try:
            if hasattr(model, 'named_steps'):
                classifier = model.named_steps['classifier']
            else:
                classifier = model
            if hasattr(classifier, 'feature_importances_'):
                importances = classifier.feature_importances_
                sorted_idx = np.argsort(importances)
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.barh(range(len(sorted_idx)), importances[sorted_idx], color='#e74c3c', alpha=0.8)
                ax.set_yticks(range(len(sorted_idx)))
                ax.set_yticklabels([feature_names[i] for i in sorted_idx], fontsize=10)
                ax.set_xlabel('Feature Importance')
                ax.set_title('XGBoost Feature Importance (Built-in)', fontweight='bold')
                ax.grid(True, axis='x', alpha=0.3)
                save_fig(fig, output_dir, 'xgboost_feature_importance.png')
            else:
                print(f"    [WARN] No feature_importances_ available on model.")
        except Exception as e2:
            print(f"    [WARN] Feature importance fallback also failed: {e2}")
        return None


# MASTER FUNCTION
def generate_all_plots(data, reg_results, class_results, y_test_egfr, y_test_stage,
                       X_test, feature_names, gwo_convergence, output_dir):
    print("\n" + "="*60)
    print("GENERATING PUBLICATION-QUALITY FIGURES")
    print("="*60)
    os.makedirs(output_dir, exist_ok=True)

    print("\n  [1/9] Correlation matrix...")
    plot_correlation_matrix(data, output_dir)

    print("  [2/9] eGFR distributions...")
    plot_egfr_distributions(data, output_dir)

    print("  [3/9] Bland-Altman plots...")
    if 'eGFR_SCr' in data and 'eGFR_Combined' in data:
        plot_bland_altman(data['eGFR_SCr'], data['eGFR_Combined'],
                          'CKD-EPI SCr vs Combined', output_dir, 'bland_altman_scr_combined.png')
    if 'eGFR_SCysC' in data and 'eGFR_Combined' in data:
        plot_bland_altman(data['eGFR_SCysC'], data['eGFR_Combined'],
                          'CKD-EPI SCysC vs Combined', output_dir, 'bland_altman_cysc_combined.png')

    print("  [4/9] Feature distributions...")
    plot_feature_distributions(data, output_dir)

    print("  [5/9] Stage distribution...")
    plot_stage_distribution(data, output_dir)

    print("  [6/9] Regression scatter plots...")
    if reg_results:
        plot_regression_results(reg_results, y_test_egfr, output_dir)

    print("  [7/9] GWO convergence...")
    if gwo_convergence:
        plot_gwo_convergence(gwo_convergence, output_dir)

    print("  [8/9] Confusion matrices & ROC curves...")
    # Calculate global classes for consistency across all classification plots
    all_labels = list(np.unique(y_test_stage))
    if class_results:
        for res in class_results.values():
            preds = res.get('predictions', [])
            if len(preds):
                for lbl in np.unique(preds):
                    if lbl not in all_labels:
                        all_labels.append(lbl)
    global_classes = sorted(all_labels)

    if class_results:
        try:
            plot_confusion_matrices(class_results, y_test_stage, output_dir, classes=global_classes)
        except Exception as e: print(f"    [WARN] Confusion matrix plot failed: {e}")
        
        try:
            plot_roc_curves(class_results, X_test, y_test_stage, output_dir, classes=global_classes)
        except Exception as e: print(f"    [WARN] ROC curve plot failed: {e}")
        
        try:
            plot_model_comparison(class_results, output_dir)
        except Exception as e: print(f"    [WARN] Model comparison plot failed: {e}")

    print("  [9/9] SHAP / Feature importance analysis...")
    if class_results and 'XGBoost' in class_results:
        plot_shap_analysis(class_results['XGBoost']['model'], X_test, feature_names, output_dir)

    print(f"\n  All figures saved to: {output_dir}/")
