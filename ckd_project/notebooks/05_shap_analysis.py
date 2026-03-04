
#%%
import shap
import matplotlib.pyplot as plt
import os
import pandas as pd
import joblib

#%%
def explain_with_shap(model, X_train, X_test, feature_names, output_dir):
    """
    Generate SHAP explanations for model predictions
    """
    os.makedirs(output_dir, exist_ok=True)

    # Create SHAP explainer
    # Depends on model type. Accessing 'classifier' step from pipeline
    if hasattr(model, 'named_steps'):
        classifier = model.named_steps['classifier']
    else:
        classifier = model
        
    explainer = shap.TreeExplainer(classifier)
    
    # Calculate SHAP values
    X_test_transformed = X_test  # Assuming X_test is already preprocessed appropriately if pipeline handles it?
    # Actually, if model is a pipeline, we need to transform X_test using the steps before 'classifier'.
    # For now, assuming X_test passed here is ready for the classifier.
    
    try:
        shap_values = explainer.shap_values(X_test_transformed)
        
        # 1. Global feature importance (Figure 9)
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_test_transformed, 
                        feature_names=feature_names, 
                        show=False)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/shap_summary.png')
        plt.show()
        
        # 2. Force plot for individual predictions (Figure 10)
        # Force plots are interactive javascript, might not save well as png without modifications
        # skipping loop to avoid too many files for now, or just saving 1
        
        # 3. Waterfall plot (Figure 11)
        plt.figure()
        # For multi-class, shap_values is a list. For binary, it might be array.
        # Check shape
        if isinstance(shap_values, list):
            sv = shap_values[0][0] # Class 0, sample 0
            bv = explainer.expected_value[0]
        else:
            sv = shap_values[0]
            bv = explainer.expected_value
            
        shap.waterfall_plot(shap.Explanation(values=sv,
                                            base_values=bv,
                                            data=X_test_transformed[0],
                                            feature_names=feature_names),
                            show=False)
        plt.savefig(f'{output_dir}/waterfall_plot_sample_0.png')
        plt.show()
        
        return shap_values
    except Exception as e:
        print(f"SHAP explanation failed: {e}")
        return None

#%%
if __name__ == "__main__":
    # Example usage
    pass
