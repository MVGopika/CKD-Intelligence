"""SHAP explainability helpers"""

def compute_shap(model, data):
    import shap
    explainer = shap.TreeExplainer(model)
    return explainer.shap_values(data)
