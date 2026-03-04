"""
Quick test: verify the ROC + plot fix works with synthetic dummy data
before running the full 10-minute GWO pipeline again.
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.visualization import plot_roc_curves, plot_confusion_matrices, plot_model_comparison
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

np.random.seed(42)
# Simulate 5-class problem where test set may miss some classes
X = np.random.randn(300, 5)
y = np.random.choice([1,2,3,4,5], size=300, p=[0.30,0.30,0.25,0.10,0.05])
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)

pipeline = ImbPipeline([
    ('smote', SMOTE(random_state=42, k_neighbors=3)),
    ('classifier', RandomForestClassifier(n_estimators=10, random_state=42))
])
pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)

results = {'RandomForest': {
    'model': pipeline,
    'predictions': y_pred,
    'accuracy': 0.95, 'precision': 0.95, 'recall': 0.95, 'f1_score': 0.95,
    'cv_mean': 0.94, 'cv_std': 0.01,
    'confusion_matrix': None,
}}

os.makedirs('results/figures', exist_ok=True)
print("Testing ROC curves...")
plot_roc_curves(results, X_test, y_test, 'results/figures')
print("Testing confusion matrices...")
plot_confusion_matrices(results, y_test, 'results/figures')
print("Testing model comparison...")
plot_model_comparison(results, 'results/figures')
print("\n✓ ALL VISUALIZATION TESTS PASSED!")
