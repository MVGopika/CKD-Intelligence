
#%%
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import pandas as pd
import os

#%%
def perform_eda(df):
    # Ensure output directory exists
    os.makedirs('../results/figures', exist_ok=True)

    # 1. Descriptive statistics
    print(df.describe())
    
    # 2. Correlation matrix (Figure 3 from paper)
    plt.figure(figsize=(12, 10))
    # Check if columns exist before selecting
    cols = ['SCr', 'SCysC', 'Age', 'BMI', 'HbA1c', 'SBP', 'DBP', 'CRP', 'Alb']
    existing_cols = [c for c in cols if c in df.columns]
    
    correlation_matrix = df[existing_cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='RdBu_r', 
                center=0, vmin=-1, vmax=1)
    plt.title('Correlation Matrix of Clinical Variables')
    plt.tight_layout()
    plt.savefig('../results/figures/correlation_matrix.png')
    plt.show()
    
    # 3. eGFR distribution by stage (Figure 2 & 4)
    # Check if necessary columns exist
    if all(col in df.columns for col in ['eGFR_SCr', 'eGFR_SCysC', 'eGFR_Combined', 'CKD_Stage']):
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for i, (egfr_col, title) in enumerate(zip(
            ['eGFR_SCr', 'eGFR_SCysC', 'eGFR_Combined'],
            ['CKD-EPI SCr', 'CKD-EPI SCysC', 'CKD-EPI Combined']
        )):
            df.boxplot(column=egfr_col, by='CKD_Stage', ax=axes[i])
            axes[i].set_title(title)
            axes[i].set_ylabel('eGFR (mL/min/1.73m²)')
        
        plt.tight_layout()
        plt.savefig('../results/figures/egfr_by_stage.png')
        plt.show()
    else:
        print("Skipping eGFR plots: computed eGFR columns missing")
    
    # 4. Bland-Altman plots (Figure 7)
    # plot_bland_altman(df['eGFR_SCr'], df['eGFR_Combined'], 'CKD-EPI SCr vs Combined')
    # Note: plot_bland_altman is not defined in the text, so commenting out.

#%%
if __name__ == "__main__":
    # Example usage if data exists
    if os.path.exists('../data/processed/ckd_data_processed.csv'):
        df = pd.read_csv('../data/processed/ckd_data_processed.csv')
        perform_eda(df)
    else:
        print("Data not found. Please run main.py first to generate processed data or load raw data.")
