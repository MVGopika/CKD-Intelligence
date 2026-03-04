# Kidney Disease Prediction System

## Overview
A full-stack web application for Chronic Kidney Disease (CKD) prediction using:
- **Features-based prediction**: Random Forest ML model on 24 clinical features
- **Image-based prediction**: CNN deep learning model on CT scan images

## Project Structure
```
kidney_disease_prediction/
├── app.py                  # Main Flask application
├── train_model.py          # Train Random Forest on tabular data
├── train_cnn.py            # Train CNN on kidney images
├── kidney_disease.csv      # Synthetic CKD dataset (400 records)
├── requirements.txt        # Python dependencies
├── models/
│   ├── rf_model.pkl        # Trained Random Forest model
│   ├── label_encoders.pkl  # Feature encoders
│   ├── class_labels.json   # CNN class labels
│   └── cnn_kidney_model.h5 # CNN model (after training)
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── predicta2.html
│   ├── features_based.html
│   ├── features_result.html
│   ├── image_based.html
│   └── image_result.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── uploads/
└── dataset/
    └── generate_dataset.py
```

## Quick Setup

### 1. Install Dependencies
```bash
pip install flask numpy pandas scikit-learn Pillow
pip install tensorflow  # For CNN image predictions
```

### 2. Train Models
```bash
# Generate dataset and train RF model
python train_model.py

# Train CNN model (requires TensorFlow)
python train_cnn.py
```

### 3. Run Application
```bash
python app.py
```
Visit: http://127.0.0.1:5000

## Login Credentials
| Username | Password  |
|----------|-----------|
| admin    | admin123  |
| doctor   | doctor123 |
| user     | user123   |

## Features-Based Input
Enter 24 space-separated values in this order:
```
age bp sg al su rbc pc pcc ba bgr bu sc sod pot hemo pcv wc rc htn dm cad appet pe ane
```

### Example Input (CKD Patient):
```
48 80 1.020 3 0 abnormal abnormal present notpresent 400 100 7.5 130 4.0 9.0 28 6000 3.0 yes yes no poor yes yes
```

### Example Input (Normal):
```
48 80 1.020 0 0 normal normal notpresent notpresent 121 36 1.2 137 4.4 15.4 44 7800 5.2 no no no good no no
```

### Feature Descriptions
| # | Feature | Description | Range/Values |
|---|---------|-------------|--------------|
| 1 | age | Age of patient | 2-90 years |
| 2 | bp | Blood Pressure | mm/Hg |
| 3 | sg | Specific Gravity | 1.005-1.025 |
| 4 | al | Albumin | 0-5 |
| 5 | su | Sugar | 0-5 |
| 6 | rbc | Red Blood Cells | normal/abnormal |
| 7 | pc | Pus Cells | normal/abnormal |
| 8 | pcc | Pus Cell Clumps | present/notpresent |
| 9 | ba | Bacteria | present/notpresent |
| 10 | bgr | Blood Glucose Random | mg/dL |
| 11 | bu | Blood Urea | mg/dL |
| 12 | sc | Serum Creatinine | mg/dL |
| 13 | sod | Sodium | mEq/L |
| 14 | pot | Potassium | mEq/L |
| 15 | hemo | Hemoglobin | g |
| 16 | pcv | Packed Cell Volume | % |
| 17 | wc | White Blood Cell Count | cells/cumm |
| 18 | rc | Red Blood Cell Count | millions/cumm |
| 19 | htn | Hypertension | yes/no |
| 20 | dm | Diabetes Mellitus | yes/no |
| 21 | cad | Coronary Artery Disease | yes/no |
| 22 | appet | Appetite | good/poor |
| 23 | pe | Pedal Edema | yes/no |
| 24 | ane | Anemia | yes/no |

## Image-Based Prediction
- Upload kidney CT scan images (JPG/PNG)
- Model classifies into: **Normal, Cyst, Tumor, Stone**
- For production: train CNN with CT Kidney Dataset from Kaggle
  - URL: https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone

## Tech Stack
- **Backend**: Python, Flask
- **ML Models**: Random Forest (tabular), CNN/TensorFlow (images)
- **Frontend**: HTML5, CSS3, Bootstrap 5, Jinja2
- **Data**: UCI CKD-inspired synthetic dataset

## Model Performance
- Random Forest: ~88% accuracy on test set
- CNN: Depends on training data (use real CT scan dataset for best results)
