# Frontend-Backend Integration Guide

This guide shows how the Next.js frontend integrates with the FastAPI backend for CKD prediction.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Next.js Frontend                      │
│  ┌──────────────────┬──────────────────┬──────────────────┐ │
│  │  Landing Page    │  Patient Dash    │  Doctor Dash     │ │
│  └──────────────────┴──────────────────┴──────────────────┘ │
│             ↓ (HTTP Requests)                                │
│  ┌──────────────────────────────────────────────────────────┐
│  │         Authentication (JWT Token)                       │
│  │         CORS Headers                                     │
│  └──────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌──────────────────┬──────────────────┬──────────────────┐ │
│  │  Auth Routes     │  Patient Routes  │  Prediction API  │ │
│  └──────────────────┴──────────────────┴──────────────────┘ │
│             ↓                                                │
│  ┌──────────────────────────────────────────────────────────┐
│  │         ML Model Service                                 │
│  │    • eGFR Prediction (SVR)                              │
│  │    • CKD Stage Classification                           │
│  │    • SHAP Values (Feature Importance)                   │
│  │    • Clinical Guidance Generation                       │
│  └──────────────────────────────────────────────────────────┘
│             ↓                                                │
│  ┌──────────────────────────────────────────────────────────┐
│  │      PostgreSQL/Neon Database                            │
│  │    • Users & Roles                                       │
│  │    • Patient Profiles & Lab Results                     │
│  │    • Predictions & Reports                              │
│  └──────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints Used by Frontend

### 1. Authentication Flow

**Register User**
```typescript
// frontend/services/authService.ts
const register = async (email: string, password: string, fullName: string, roleName: string) => {
  const response = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: fullName, role_name: roleName })
  });
  return response.json();
};
```

**Login**
```typescript
const login = async (email: string, password: string) => {
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data.user;
};
```

**Get Current User**
```typescript
const getCurrentUser = async (token: string) => {
  const response = await fetch(`${API_BASE}/api/auth/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

### 2. Patient Profile Management

**Create Profile (after registration)**
```typescript
const createProfile = async (profileData: PatientProfileCreate, token: string) => {
  const response = await fetch(`${API_BASE}/api/patient/profile`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(profileData)
  });
  return response.json();
};
```

Request body:
```json
{
  "date_of_birth": "1975-05-15T00:00:00",
  "sex": "M",
  "height_cm": 180,
  "weight_kg": 85,
  "medical_history": "Hypertension, Type 2 Diabetes",
  "medications": "Lisinopril, Metformin"
}
```

**Get Profile**
```typescript
const getProfile = async (token: string) => {
  const response = await fetch(`${API_BASE}/api/patient/profile`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

### 3. Lab Data Input & Storage

**Submit Lab Results**
```typescript
const submitLabResults = async (labData: LabResultCreate, token: string) => {
  const response = await fetch(`${API_BASE}/api/patient/lab-results`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(labData)
  });
  return response.json();
};
```

Lab data from form:
```typescript
const labData = {
  test_date: new Date().toISOString(),
  serum_creatinine: 1.5,      // mg/dL
  cystatin_c: 1.2,             // mg/L
  blood_pressure_sys: 140,      // mmHg
  blood_pressure_dia: 90,       // mmHg
  blood_urea: 28,               // mg/dL
  sodium: 139,                  // mEq/L
  potassium: 4.2,               // mEq/L
  phosphorus: 3.5,              // mg/dL
  calcium: 9.2,                 // mg/dL
  albumin: 4.0,                 // g/dL
  lab_name: "Quest Diagnostics"
};
```

**Get Lab History**
```typescript
const getLabResults = async (token: string) => {
  const response = await fetch(`${API_BASE}/api/patient/lab-results`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

### 4. AI Prediction

**Get Prediction**
```typescript
const getPrediction = async (labData: LabResultCreate, token: string) => {
  const response = await fetch(`${API_BASE}/api/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(labData)
  });
  return response.json();
};
```

Response from backend:
```json
{
  "id": 1,
  "patient_id": 1,
  "egfr_predicted": 45.2,
  "egfr_confidence": 0.92,
  "ckd_stage": "3",
  "stage_confidence": 0.88,
  "risk_level": "moderate",
  "clinical_guidance": "Moderate kidney damage detected. Close monitoring...",
  "recommendations": [
    "Consult with a nephrologist",
    "Monitor blood pressure (target: <120/80 mmHg)",
    "Strict sodium restriction (<2g per day)",
    "Restrict protein intake (0.6-0.8g/kg body weight)"
  ],
  "top_contributing_features": [
    { "feature": "serum_creatinine", "importance": 0.45 },
    { "feature": "age", "importance": 0.22 },
    { "feature": "blood_pressure_sys", "importance": 0.18 }
  ],
  "shap_values": {
    "serum_creatinine": 0.45,
    "age": 0.22,
    "blood_pressure_sys": 0.18
  },
  "created_at": "2024-02-28T10:30:00"
}
```

**Retrieve Previous Prediction**
```typescript
const getPredictionById = async (predictionId: number, token: string) => {
  const response = await fetch(`${API_BASE}/api/predict/${predictionId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

### 5. Doctor Features

**Get Patient List**
```typescript
const getAssignedPatients = async (token: string) => {
  const response = await fetch(`${API_BASE}/api/doctor/patients`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

Response:
```json
[
  {
    "id": 1,
    "full_name": "John Doe",
    "latest_ckd_stage": "3",
    "latest_egfr": 45.2,
    "latest_test_date": "2024-02-28T10:30:00",
    "risk_level": "moderate"
  }
]
```

## Frontend Service Layer

Create these service modules in frontend:

### `services/api.ts`
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const apiClient = {
  async request(url: string, options: RequestInit = {}) {
    const token = localStorage.getItem('access_token');
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API Error');
    }
    
    return response.json();
  },
  
  get(url: string) {
    return this.request(url);
  },
  
  post(url: string, data: any) {
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
```

### `services/authService.ts`
```typescript
import { apiClient } from './api';

export const authService = {
  register: (email: string, password: string, fullName: string, roleName: string) =>
    apiClient.post('/api/auth/register', {
      email,
      password,
      full_name: fullName,
      role_name: roleName,
    }),
  
  login: (email: string, password: string) =>
    apiClient.post('/api/auth/login', { email, password }),
  
  getCurrentUser: () =>
    apiClient.get('/api/auth/me'),
};
```

### `services/patientService.ts`
```typescript
import { apiClient } from './api';

export const patientService = {
  getProfile: () =>
    apiClient.get('/api/patient/profile'),
  
  createProfile: (data: any) =>
    apiClient.post('/api/patient/profile', data),
  
  submitLabResults: (data: any) =>
    apiClient.post('/api/patient/lab-results', data),
  
  getLabHistory: () =>
    apiClient.get('/api/patient/lab-results'),
  
  getPrediction: (labData: any) =>
    apiClient.post('/api/predict', labData),
  
  getPredictionById: (id: number) =>
    apiClient.get(`/api/predict/${id}`),
};
```

## Data Flow Example: Complete Workflow

### 1. User Registration
```
Frontend (Register Form)
  ↓ user data
Backend (POST /api/auth/register)
  ↓ create user in DB
  ↓ hash password
  ↓ create JWT token
Error: duplicate email
  ↓ return token + user info
Frontend (Store token in localStorage)
  ↓ redirect to profile creation
```

### 2. Profile Creation
```
Frontend (Profile Form)
  ↓ DOB, sex, height, weight, medications
Backend (POST /api/patient/profile)
  ↓ validate input
  ↓ create PatientProfile record
  ↓ return profile data
Frontend (Store profile, show lab entry form)
```

### 3. Lab Data Input & Prediction
```
Frontend (Clinical Data Input Form)
  ↓ biomarker values (SCr, CysC, BP, etc.)
Backend (POST /api/predict)
  ↓ get patient profile
  ↓ prepare features
  ↓ load ML models
  ├─ Predict eGFR (SVR regression)
  ├─ Classify CKD stage (XGBoost)
  ├─ Calculate confidence scores
  ├─ Compute SHAP feature importance
  ├─ Generate clinical guidance
  └─ store Prediction record in DB
  ↓ return prediction with SHAP values
Frontend (Display results)
  ├─ eGFR chart (Recharts)
  ├─ Stage badge (color-coded)
  ├─ SHAP bar chart (feature importance)
  ├─ Clinical recommendations
  └─ Download report button
```

## Environment Configuration

### Frontend `.env.local`
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Backend `.env`
```env
DATABASE_URL=postgresql://user:pass@host/ckd_intelligence
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=["http://localhost:3000"]
MODELS_PATH=../ckd_project/models/saved_models
```

## Testing the Integration

### 1. Start Both Services
```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 2. Test Registration
- Open http://localhost:3000
- Click "Register"
- Fill form (email, password, name, role="patient")
- Click "Create account"
- Check browser console for token

### 3. Test Lab Input
- Create patient profile
- Enter lab values
- Click "Get Prediction"
- See results with SHAP chart

### 4. Test Doctor Dashboard
- Register as doctor
- Add patients to your list
- View patient analytics

## Error Handling

### Common Frontend Errors

**401 Unauthorized**
```typescript
if (error.response?.status === 401) {
  // Token expired or invalid
  localStorage.removeItem('access_token');
  window.location.href = '/login';
}
```

**CORS Error**
```
Access to XMLHttpRequest ... has been blocked by CORS policy
```
Solution: Update `ALLOWED_ORIGINS` in backend `.env`

**Network Error**
```typescript
try {
  const result = await apiClient.post('/api/predict', data);
} catch (error) {
  console.error('API Error:', error.message);
  // Show user-friendly error message
}
```

## Production Considerations

### Deployment Steps

1. **Backend**
   - Deploy to Railway/Vercel/Heroku
   - Set production `DATABASE_URL`
   - Set strong `SECRET_KEY`
   - Update `ALLOWED_ORIGINS` to frontend domain

2. **Frontend**
   - Deploy to Vercel
   - Set `NEXT_PUBLIC_API_BASE_URL` to production backend URL
   - Ensure HTTPS for tokens

3. **Database**
   - Use Neon PostgreSQL
   - Enable SSL
   - Set up backups
   - Monitor query performance

## Next Steps

1. ✅ Backend APIs implemented
2. ✅ Frontend-backend connectivity defined
3. Implement frontend service layer
4. Create frontend pages and components
5. End-to-end testing
6. Deployment to production

## References

- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [JWT Authentication](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [API Best Practices](https://restfulapi.net/)
