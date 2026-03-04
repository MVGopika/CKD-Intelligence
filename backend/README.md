# CKD Intelligence Backend

A FastAPI-based AI-driven clinical decision support system for Chronic Kidney Disease prediction, integrated with PostgreSQL (Neon) database and machine learning models.

## 🏗 Architecture Overview

The backend implements a modular, scalable architecture with the following components:

```
User Input → Authentication → Consultation Processing → Data Preprocessing
    ↓           (JWT)            (voice/text)              (normalization)
                                                                    ↓
Report Service ← SHAP Explainability ← ML Models ← Preprocessed Features
    ↓
API Response
```

## 📦 Project Structure

```
backend/
├── app/
│   ├── main.py               # FastAPI application entrypoint
│   ├── core/                 # configuration and security
│   │   ├── config.py
│   │   └── security.py
│   ├── db/                   # database layer
│   │   ├── database.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── api/                  # route definitions and dependencies
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── consultation.py
│   │       ├── prediction.py
│   │       ├── reports.py
│   │       └── doctor.py
│   ├── services/             # business logic wrappers
│   │   ├── auth_service.py
│   │   ├── consultation_service.py
│   │   ├── prediction_service.py
│   │   ├── clinical_service.py
│   │   └── report_service.py
│   ├── ml/                   # ML helpers and model loader
│   │   ├── model_loader.py
│   │   ├── preprocessing.py
│   │   ├── regression_model.py
│   │   ├── classification_model.py
│   │   ├── optimizer_gwo.py
│   │   ├── explainability.py
│   ├── utils/                # utility helpers
│   │   └── helpers.py
│   └── tests/                # future unit tests
├── init_db.py                # database initialization script
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── SETUP.md                  # Setup guide
├── INTEGRATION.md            # Frontend-backend integration guide
└── README.md                 # This file
```

## 🗄 Database Schema

### Tables

**users**
- id, email (unique), hashed_password, full_name, is_active, created_at, role_id

**roles**
- id, name, description

**patient_profiles**
- id, user_id (FK), date_of_birth, sex, height_cm, weight_kg, medical_history, medications, created_at, updated_at

**consultations**
- id, user_id (FK), input_type, raw_input, transcription, structured_data (JSON), created_at

**lab_results**
- id, patient_id (FK), test_date, serum_creatinine, cystatin_c, blood_pressure_sys/dia, blood_urea, sodium, potassium, phosphorus, calcium, albumin, hemoglobin, lab_name, notes, created_at

**predictions**
- id, patient_id (FK), consultation_id (FK), input_features (JSON), egfr_predicted, egfr_confidence, ckd_stage, stage_confidence, risk_level, shap_values (JSON), top_contributing_features (JSON), clinical_guidance, recommendations (JSON), model_version, created_at

**reports**
- id, prediction_id (FK), title, summary, detailed_analysis, recommendations, pdf_path, generated_by_user_id (FK), created_at

**doctor_patients**
- doctor_id (FK), patient_id (FK), assigned_at

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database (or Neon cloud)
- Trained ML models from ckd_project/models/saved_models

### Installation

1. **Clone and navigate to backend**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

### Running Tests

A small smoke test suite is provided under `app/tests` using `pytest` and FastAPI's `TestClient`.

```bash
# ensure virtual environment is active
pip install pytest
pytest app/tests/test_example.py
```

Feel free to add additional tests covering endpoints and services.

   ```bash
   cp .env.example .env
   # Edit .env with your Neon database URL and settings
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Run development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   API will be available at **http://localhost:8000**
   
   Interactive API docs: **http://localhost:8000/docs**

## 🔌 API Endpoints

### Authentication

```
POST   /api/auth/register       # Register new user
POST   /api/auth/login          # Login with email/password
GET    /api/auth/me             # Get current user info
```

### Patient

```
POST   /api/patient/profile     # Create patient profile
GET    /api/patient/profile     # Get patient profile
POST   /api/patient/lab-results # Submit lab results
GET    /api/patient/lab-results # Get patient's lab history
```

### Predictions

```
POST   /api/predict             # Create prediction from lab data
GET    /api/predict/{id}        # Get specific prediction with SHAP values
```

### Doctor

```
GET    /api/doctor/patients     # Get list of assigned patients
GET    /api/doctor/trends       # Get population trends
```

### Health

```
GET    /health                  # Health check
```

## 🔐 Authentication

JWT (JSON Web Token) based authentication:

1. **Register/Login** → Receive access_token
2. **Include in requests**: `Authorization: Bearer {access_token}`
3. **Token expires** after 8 hours (configurable)

Example request:
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiI..." \
     http://localhost:8000/api/patient/profile
```

## 🧠 Machine Learning Integration

### Model Loading

Models are loaded from `ckd_project/models/saved_models/`:

- `best_classifier_xgboost.pkl` – CKD stage classifier
- `svr_gwo_optimized.pkl` – eGFR regression model
- `scaler_regression.pkl` – Feature scaler for regression
- `scaler_classification.pkl` – Feature scaler for classification

### Prediction Pipeline

1. **Preprocess** input features (scaling, normalization)
2. **Predict eGFR** using SVR regression
3. **Classify CKD stage** (1-5) based on eGFR thresholds
4. **Calculate confidence** scores
5. **Compute SHAP values** for explainability
6. **Generate clinical guidance** based on stage

### SHAP Explainability

Each prediction includes:
- Feature importance values
- Top 5 contributing features
- Confidence in predictions

## 🏥 Clinical Guidance

Automatic stage-based recommendations:

- **Stage 1**: Normal kidney function, preventive care
- **Stage 2**: Mild decline, regular monitoring
- **Stage 3**: Moderate decline, nephrologist consultation
- **Stage 4**: Severe decline, prepare for dialysis
- **Stage 5**: Kidney failure, immediate intervention required

Guidance includes:
- Clinical assessment
- Personalized recommendations
- Follow-up intervals
- Lifestyle modifications
- Medications & precautions

## 🗄 Database Setup (Neon)

### Create Neon Account

1. Go to https://console.neon.tech
2. Create new project
3. Copy connection string

### Configure Backend

Update `.env`:
```env
DATABASE_URL=postgresql://user:password@host/database_name
```

### Verify Connection

```bash
python
>>> from database import engine
>>> connection = engine.connect()
>>> print("Connected!")
>>> connection.close()
```

## 📊 Example API Workflow

### 1. Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe",
    "role_name": "patient"
  }'
```
Response: Returns `access_token`

### 2. Create Patient Profile
```bash
curl -X POST http://localhost:8000/api/patient/profile \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "date_of_birth": "1975-05-15T00:00:00",
    "sex": "M",
    "height_cm": 180,
    "weight_kg": 85,
    "medications": "Lisinopril, Atorvastatin"
  }'
```

### 3. Submit Lab Results
```bash
curl -X POST http://localhost:8000/api/patient/lab-results \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "test_date": "2024-02-28T10:00:00",
    "serum_creatinine": 1.5,
    "cystatin_c": 1.2,
    "blood_pressure_sys": 140,
    "blood_pressure_dia": 90,
    "blood_urea": 28,
    "sodium": 139,
    "potassium": 4.2
  }'
```

### 4. Get Prediction
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "test_date": "2024-02-28T10:00:00",
    "serum_creatinine": 1.5,
    "cystatin_c": 1.2,
    "blood_pressure_sys": 140,
    "blood_pressure_dia": 90
  }'
```

Response includes:
- `egfr_predicted`: eGFR value
- `ckd_stage`: 1-5
- `risk_level`: low/moderate/high/critical
- `top_contributing_features`: SHAP feature importance
- `clinical_guidance`: Stage-based recommendations

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Test Endpoints with Postman

Import the collection from `postman_collection.json` (if provided).

### Health Check

```bash
curl http://localhost:8000/health
```

## 🛠 Development

### Add New Endpoint

1. Create router:
   ```python
   from fastapi import APIRouter
   
   myrouter = APIRouter(prefix="/api/myfeature", tags=["MyFeature"])
   
   @myrouter.get("/endpoint")
   async def my_endpoint(db: Session = Depends(get_db)):
       return {"message": "Hello"}
   
   app.include_router(myrouter)
   ```

2. Restart server

### Connect Frontend

Update `.env.local` in frontend:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Or in production:
```env
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
```

## 📚 Key Files

### Models Integration
- Models are loaded in `ml_service.py`
- Predictions computed in `MLModelService.predict_egfr()`
- SHAP values calculated in `MLModelService.get_shap_values()`

### Clinical Logic
- Stage-based guidance in `clinical_service.py`
- eGFR stage classification: KDIGO guidelines
- Risk stratification based on stage and confidence

### Database
- SQLAlchemy ORM models in `models.py`
- Pydantic validation schemas in `schemas.py`

## ⚙ Configuration

Key environment variables:

```env
DATABASE_URL          # PostgreSQL/Neon connection
SECRET_KEY            # JWT secret (change in production!)
ALGORITHM             # HS256 (SHA-256)
ACCESS_TOKEN_EXPIRE   # Token expiration in minutes
ALLOWED_ORIGINS       # CORS allowed domains
MODELS_PATH           # Path to trained ML models
```

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Vercel/Railway

1. Push to GitHub
2. Connect repo to deployment platform
3. Set environment variables
4. Deploy

### Local Production Build

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔒 Security Considerations

- ✅ JWT authentication with expiration
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (RBAC)
- ✅ CORS configuration
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Input validation (Pydantic)

In production:
- [ ] Use HTTPS only
- [ ] Rotate SECRET_KEY regularly
- [ ] Set secure CORS origins
- [ ] Enable database SSL
- [ ] Rate limiting
- [ ] API key rotation

## 📖 References

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org)
- [Neon PostgreSQL](https://neon.tech)
- [SHAP Documentation](https://shap.readthedocs.io)
- [KDIGO CKD Guidelines](https://kdigo.org)

## 🤝 Support

For issues or questions:
1. Check API docs: http://localhost:8000/docs
2. Review error messages in terminal
3. Check `.env` configuration
4. Verify database connection

## 📄 License

See repository root for license details.
