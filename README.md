# CKD Intelligence - Complete Project Setup

A full-stack AI-driven clinical decision support system for Chronic Kidney Disease prediction.

## 🎯 Project Overview

**Frontend**: Next.js + Tailwind CSS + Recharts + Framer Motion  
**Backend**: FastAPI + PostgreSQL (Neon) + ML Models  
**ML**: SVR (eGFR prediction) + XGBoost (CKD staging) + SHAP (explainability)

## 📁 Project Structure

```
Clinical-CKD-Intelligence/
├── frontend/                    # Next.js web application
│   ├── app/                     # Pages and routes (auth, dashboard, consultation, prediction, reports)
│   ├── components/              # React components (ui, charts, voice, layout)
│   ├── lib/                     # Utility libraries (api, auth, utils)
│   ├── hooks/                   # Custom React hooks
│   ├── services/                # API service wrappers
│   ├── store/                   # Client state management
│   ├── types/                   # TypeScript interfaces
│   ├── public/                  # Static assets
│   ├── styles/                  # CSS/Tailwind files
│   ├── package.json
│   └── README.md               # Frontend docs
│
├── backend/                     # FastAPI application
│   ├── app/                     # Main application package
│   │   ├── main.py             # Entry point
│   │   ├── core/               # config, security
│   │   ├── db/                 # database models/schemas
│   │   ├── api/                # routers & dependencies
│   │   ├── services/           # business logic
│   │   ├── ml/                 # ML utilities & loader
│   │   ├── utils/              # helper functions
│   │   └── tests/              # future tests
│   ├── init_db.py              # DB initialization script
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment template
│   ├── README.md               # Backend docs
│   ├── SETUP.md                # Setup guide
│   └── INTEGRATION.md          # Frontend-backend integration
│
├── ckd_project/                # ML model training code
│   ├── src/                    # Source code
│   ├── data/                   # Datasets
│   ├── models/                 # Trained models
│   └── README.md
│
└── README.md                   # This file
```

## 🚀 Quick Start (Development)

### Prerequisites
- Node.js 18+
- Python 3.8+
- PostgreSQL (or Neon cloud account)

### 1. Clone & Setup Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your Neon database URL

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start backend
uvicorn app.main:app --reload --port 8000
```

Backend runs at: **http://localhost:8000**  
API Docs: **http://localhost:8000/docs**

### 2. Configure Frontend

```bash
cd frontend

# Create environment file
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local

# Install dependencies
npm install

# Start frontend
npm run dev
```

Frontend runs at: **http://localhost:3000**

### 3. Test the System

1. Open http://localhost:3000
2. Register as a patient
3. Create patient profile
4. Enter lab values
5. Get AI prediction with SHAP explanation

## 📋 Database Tables

| Table | Purpose |
|-------|---------|
| `users` | User accounts with role-based access |
| `roles` | Patient, Doctor, Admin roles |
| `patient_profiles` | Patient demographics and medical history |
| `lab_results` | Laboratory test values (SCr, CysC, etc.) |
| `consultations` | Voice/text input logs from MediVox |
| `predictions` | AI predictions with eGFR, stage, SHAP values |
| `reports` | Generated clinical reports in PDF |
| `doctor_patients` | Linking doctors to their patients |

## 🔌 Key API Endpoints

### Authentication
```
POST   /api/auth/register        # Register new user
POST   /api/auth/login           # Login
GET    /api/auth/me              # Get current user
```

### Patient
```
POST   /api/patient/profile      # Create profile
GET    /api/patient/profile      # Get profile
POST   /api/patient/lab-results  # Submit lab results
GET    /api/patient/lab-results  # Get lab history
```

### Predictions
```
POST   /api/predict              # Get AI prediction
GET    /api/predict/{id}         # Retrieve previous prediction
```

### Doctor
```
GET    /api/doctor/patients      # List assigned patients
GET    /api/doctor/trends        # Population analytics
```

### Reports
```
GET    /api/reports              # List available patient reports
GET    /api/reports/{id}         # Download specific report PDF
```

## 🧠 ML Pipeline

```
Lab Results (SCr, CysC, BP, age, sex)
           ↓
    Feature Preprocessing
           ↓
    eGFR Prediction (SVR-GWO)
           ↓
    CKD Stage Classification (XGBoost)
           ↓
    Risk Stratification
           ↓
    SHAP Explainability
           ↓
    Clinical Guidance Generation
           ↓
    JSON Response + Storage
```

## 🎨 Frontend Features

- ✅ Modern medical UI with Tailwind CSS
- ✅ Role-based dashboards (patient & doctor)
- ✅ Voice input with Web Speech API
- ✅ Real-time data visualization (Recharts)
- ✅ SHAP feature importance charts
- ✅ Smooth animations (Framer Motion)
- ✅ Accessible components (Headless UI)
- ✅ Dark mode support

## 🔐 Backend Features

- ✅ JWT authentication with role-based access
- ✅ PostgreSQL database with Neon cloud support
- ✅ ML model integration (SVR, XGBoost, SHAP)
- ✅ eGFR prediction with CKD-EPI equations
- ✅ Stage-based clinical guidance
- ✅ RESTful API with auto-documentation
- ✅ Input validation (Pydantic)
- ✅ CORS support for frontend

## 📊 Example Prediction Response

```json
{
  "id": 1,
  "egfr_predicted": 45.2,
  "egfr_confidence": 0.92,
  "ckd_stage": "3",
  "stage_confidence": 0.88,
  "risk_level": "moderate",
  "clinical_guidance": "Moderate kidney damage detected. Close monitoring required.",
  "recommendations": [
    "Consult with a nephrologist",
    "Monitor blood pressure (target: <120/80 mmHg)",
    "Strict sodium restriction (<2g per day)",
    "Restrict protein intake (0.6-0.8g/kg body weight)"
  ],
  "top_contributing_features": [
    {"feature": "serum_creatinine", "importance": 0.45},
    {"feature": "age", "importance": 0.22},
    {"feature": "blood_pressure_sys", "importance": 0.18}
  ],
  "shap_values": {...}
}
```

## 🔑 Demo Credentials (Development)

After running `python init_db.py`, use:

- **Patient**: patient@example.com / patient123
- **Doctor**: doctor@example.com / doctor123

## 📚 Documentation

- [Frontend Setup & Development](./frontend/DEVELOPMENT.md)
- [Frontend Architecture](./frontend/ARCHITECTURE.md)
- [Backend Setup Guide](./backend/SETUP.md)
- [Frontend-Backend Integration](./backend/INTEGRATION.md)
- [Backend Architecture](./backend/README.md)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing with Curl

Health check:
```bash
curl http://localhost:8000/health
```

Register:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass","full_name":"John","role_name":"patient"}'
```

## 🚀 Production Deployment

### Backend Deployment Options
- Railway.app (recommended)
- Render
- Heroku
- DigitalOcean App Platform
- AWS Lambda with API Gateway

### Frontend Deployment Options
- Vercel (recommended)
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

### Database
- Neon PostgreSQL (https://neon.tech)
- AWS RDS
- DigitalOcean Managed Databases

## 🔒 Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Use HTTPS for all endpoints
- [ ] Enable database SSL
- [ ] Configure CORS for production domain only
- [ ] Set strong database passwords
- [ ] Implement rate limiting
- [ ] Enable connection pooling
- [ ] Regular security updates
- [ ] Database backups

## 📈 Performance Optimization

### Backend
- Connection pooling (20-40 connections)
- Model caching in memory
- Database indexes on frequently queried columns
- Query optimization with SQLAlchemy

### Frontend
- Code splitting and lazy loading
- Image optimization with Next.js Image
- CSS-in-JS optimization with Tailwind
- API response caching

## 🐛 Troubleshooting

### Backend Issues

**Module not found**
```bash
pip install -r requirements.txt
```

**Database connection error**
```bash
# Verify CONNECTION_URL
python -c "from database import engine; engine.connect()"
```

**Models not loading**
```bash
# Check MODELS_PATH
ls ../ckd_project/models/saved_models/
```

### Frontend Issues

**Port 3000 in use**
```bash
npm run dev -- -p 3001  # Use different port
```

**API errors**
- Check backend is running
- Verify `NEXT_PUBLIC_API_BASE_URL` is correct
- Check browser console for CORS errors

## 📞 Support

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Next.js Docs](https://nextjs.org/docs)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [Neon Docs](https://neon.tech/docs)

### External Resources
- [KDIGO CKD Guidelines](https://kdigo.org)
- [SHAP Documentation](https://shap.readthedocs.io)
- [eGFR Calculators](https://www.kidney.org)

## 📄 License

CKD Intelligence Copyright (2024-2025). All rights reserved.

## 🎓 Educational Purpose

This project is designed as a clinical decision support tool. It should:
- Always be reviewed by qualified healthcare professionals
- Not replace professional medical judgment
- Be used as an educational and supportive tool only
- Comply with HIPAA and healthcare data regulations

## ✅ Verification Checklist

Before going to production:

- [ ] Both frontend and backend running locally
- [ ] API documentation accessible at /docs
- [ ] Patient registration works
- [ ] Lab data submission works
- [ ] Predictions generate correctly
- [ ] SHAP values display
- [ ] Clinical guidance shows
- [ ] Doctor dashboard works
- [ ] Database backups configured
- [ ] Error handling tested
- [ ] Security settings reviewed
- [ ] CORS configured properly
- [ ] Environment variables set
- [ ] ML models accessible

## 🎯 Next Steps

1. ✅ Setup development environment
2. ✅ Run frontend and backend locally
3. ✅ Test with demo credentials
4. Create additional frontend components
5. Implement additional API endpoints
6. Set up CI/CD pipeline
7. Deploy to production
8. Monitor application health
9. Gather user feedback
10. Iterate and improve

## 📧 Contact & Support

For questions or issues:
1. Check [Frontend README](./frontend/README.md)
2. Check [Backend README](./backend/README.md)
3. Review [Integration Guide](./backend/INTEGRATION.md)
4. Search existing documentation
5. Check GitHub issues

---

**Happy Building! 🎉**

Built with ❤️ for CKD patient care and clinical decision support.
