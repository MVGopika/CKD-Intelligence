"""
Train ML model for CKD prediction using tabular features.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

# Load dataset
df = pd.read_csv('kidney_disease.csv')

# Encode categorical columns
label_encoders = {}
cat_cols = ['rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane']
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

# Target
le_target = LabelEncoder()
df['class'] = le_target.fit_transform(df['class'])
label_encoders['class'] = le_target

# Features and target
X = df.drop('class', axis=1)
y = df['class']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Accuracy: {acc:.4f}")
print(classification_report(y_test, y_pred, target_names=le_target.classes_))

# Save model and encoders
os.makedirs('models', exist_ok=True)
with open('models/rf_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('models/label_encoders.pkl', 'wb') as f:
    pickle.dump(label_encoders, f)

print("Model saved to models/rf_model.pkl")
print("Label encoders saved to models/label_encoders.pkl")
