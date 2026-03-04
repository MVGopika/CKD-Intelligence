"""
Generate a synthetic CKD dataset similar to UCI CKD dataset.
Features: age, bp, sg, al, su, rbc, pc, pcc, ba, bgr, bu, sc, sod, pot, hemo, pcv, wc, rc, htn, dm, cad, appet, pe, ane, class
"""
import pandas as pd
import numpy as np

np.random.seed(42)
n = 400

data = {
    'age': np.random.randint(2, 90, n),
    'bp': np.random.choice([60,70,80,90,100,110,120,130,140,150,160,170,180], n),
    'sg': np.random.choice([1.005,1.010,1.015,1.020,1.025], n),
    'al': np.random.choice([0,1,2,3,4,5], n),
    'su': np.random.choice([0,1,2,3,4,5], n),
    'rbc': np.random.choice(['normal','abnormal'], n),
    'pc': np.random.choice(['normal','abnormal'], n),
    'pcc': np.random.choice(['present','notpresent'], n),
    'ba': np.random.choice(['present','notpresent'], n),
    'bgr': np.random.randint(70, 490, n),
    'bu': np.random.randint(10, 300, n),
    'sc': np.round(np.random.uniform(0.4, 15.0, n), 1),
    'sod': np.random.randint(100, 165, n),
    'pot': np.round(np.random.uniform(2.5, 47.0, n), 1),
    'hemo': np.round(np.random.uniform(3.1, 17.8, n), 1),
    'pcv': np.random.randint(9, 54, n),
    'wc': np.random.randint(3800, 26400, n),
    'rc': np.round(np.random.uniform(2.1, 8.0, n), 1),
    'htn': np.random.choice(['yes','no'], n),
    'dm': np.random.choice(['yes','no'], n),
    'cad': np.random.choice(['yes','no'], n),
    'appet': np.random.choice(['good','poor'], n),
    'pe': np.random.choice(['yes','no'], n),
    'ane': np.random.choice(['yes','no'], n),
}

# Create class based on some rules
classes = []
for i in range(n):
    score = 0
    if data['al'][i] > 2: score += 2
    if data['hemo'][i] < 10: score += 2
    if data['sc'][i] > 5: score += 2
    if data['htn'][i] == 'yes': score += 1
    if data['dm'][i] == 'yes': score += 1
    if data['bgr'][i] > 200: score += 1
    if data['bu'][i] > 100: score += 1
    if score >= 4:
        classes.append('ckd')
    else:
        classes.append('notckd')

data['class'] = classes
df = pd.DataFrame(data)
df.to_csv('kidney_disease.csv', index=False)
print("Dataset created:", df['class'].value_counts().to_dict())
print(df.head())
