# Backend Setup & Deployment Guide

## Prerequisites

Before starting, ensure you have:
- Python 3.8+
- PostgreSQL 12+ (or Neon cloud database account)
- Git
- Trained ML models from `ckd_project/models/saved_models/`

## Step 1: Environment Setup

### 1.1 Create Virtual Environment

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Database Configuration

### Option A: Neon Cloud Database (Recommended)

1. **Create Neon Account**
   - Go to https://console.neon.tech
   - Sign up for free account
   - Create a new project

2. **Get Connection String**
   - Copy your PostgreSQL connection string
   - Format: `postgresql://user:password@host/database`

3. **Configure .env**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add:
   ```env
   DATABASE_URL=postgresql://user:password@host/ckd_intelligence
   SECRET_KEY=your-very-secret-key-change-this
   ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]
   MODELS_PATH=../ckd_project/models/saved_models
   ```

### Option B: Local PostgreSQL

1. **Install PostgreSQL**
   ```bash
   # Windows: Download from https://www.postgresql.org/download/windows/
   # macOS: brew install postgresql
   # Linux: sudo apt-get install postgresql
   ```

2. **Create Database**
   ```bash
   createdb ckd_intelligence
   ```

3. **Configure .env**
   ```env
   DATABASE_URL=postgresql://localhost/ckd_intelligence
   ```

## Step 3: Initialize Database

```bash
# Create tables and seed initial data
python init_db.py
```

Output should show:
```
✓ Database tables created
✓ Roles initialized
✓ Demo users created

Demo Credentials:
  Patient: patient@example.com / patient123
  Doctor:  doctor@example.com / doctor123
```

## Step 4: Run Backend Server

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with different port
uvicorn app.main:app --reload --port 5000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Access Backend

- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc (Alternative Docs)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Step 5: Connect Frontend to Backend

### Update Frontend Configuration

In `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Verify Connection

The frontend should now be able to communicate with the backend.

## 🔍 Testing the Backend

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123",
    "full_name": "Test User",
    "role_name": "patient"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "testuser@example.com",
    "full_name": "Test User",
    "is_active": true
  }
}
```

### 3. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "patient123"
  }'
```

### 4. Test Protected Endpoint
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📊 Data Flow

```
Frontend (Next.js)
    ↓ (HTTP POST)
[User enters lab data]
    ↓
Backend (FastAPI)
    ↓
[Validate & store in PostgreSQL]
    ↓
[Load ML models]
    ↓
[Predict eGFR using SVR]
    ↓
[Classify CKD stage]
    ↓
[Calculate SHAP values]
    ↓
[Generate clinical guidance]
    ↓
[Return JSON response]
    ↓
Frontend
    ↓
[Display results with visualizations]
```

## 🔧 Common Issues & Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "ERROR: relationship() argument is not of type class"
**Solution**: Ensure SQLAlchemy is correctly installed
```bash
pip install --upgrade sqlalchemy
```

### Issue: "psycopg2: connection refused"
**Solution**: Check DATABASE_URL in .env
```bash
# Test connection
python
>>> from database import engine
>>> engine.connect()
```

### Issue: Models not found "No module named 'main'"
**Solution**: Run from backend directory
```bash
cd backend  # Make sure you're in the backend folder
uvicorn main:app --reload
```

### Issue: "CORS error in frontend"
**Solution**: Update ALLOWED_ORIGINS in .env
```env
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

## 📈 Monitoring & Logging

### Check Server Logs

Look for these successful logs:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO:     ML models loaded successfully
```

If you see warnings about models, ensure `MODELS_PATH` is correct and models exist:
```bash
ls ../ckd_project/models/saved_models/
```

Should show:
- `best_classifier_xgboost.pkl`
- `svr_gwo_optimized.pkl`
- `scaler_regression.pkl`
- `scaler_classification.pkl`

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL=postgresql://user:pass@db/ckd
ENV SECRET_KEY=production-secret-key

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ckd-backend .
docker run -p 8000:8000 --env-file .env ckd-backend
```

### Deploy to Cloud

#### Railway.app
1. Connect GitHub repo
2. Add environment variables
3. Railway auto-detects FastAPI and deploys

#### Render
1. Create new Web Service
2. Connect GitHub
3. Set Python runtime
4. Add environment variables

#### Heroku
```bash
heroku login
heroku create ckd-intelligence-api
git push heroku main
heroku config:set DATABASE_URL=...
```

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Set `ALLOWED_ORIGINS` to your domain only
- [ ] Use HTTPS in production
- [ ] Enable database SSL
- [ ] Set strong database password
- [ ] Implement rate limiting
- [ ] Enable CORS only for trusted origins
- [ ] Rotate SECRET_KEY periodically
- [ ] Use environment variables for all secrets

## 📋 Project Structure Recap

```
backend/
├── main.py              # FastAPI app & routes
├── models.py            # Database models
├── schemas.py           # Request/response schemas
├── database.py          # DB connection
├── config.py            # Settings
├── auth.py              # JWT & security
├── ml_service.py        # ML predictions
├── clinical_service.py  # Clinical guidance
├── init_db.py           # Database initialization
├── requirements.txt     # Dependencies
├── .env.example         # Env template
└── README.md            # Documentation
```

## 🎓 Next Steps

1. ✅ Backend running
2. ✅ Frontend configured
3. Next: Create API integration service in frontend
4. Test full workflow (register → input data → get prediction)
5. Deploy to staging/production

## 📞 Support Resources

- FastAPI Docs: https://fastapi.tiangolo.com
- Neon Docs: https://neon.tech/docs
- PostgreSQL Docs: https://www.postgresql.org/docs
- Python Docs: https://docs.python.org/3

## ✅ Verification Checklist

Before saying "backend is ready":

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list | grep fastapi`)
- [ ] `.env` file created and configured
- [ ] Database connected (`python -c "from database import engine; engine.connect()"`)
- [ ] Tables created (`python init_db.py`)
- [ ] Server starts without errors (`uvicorn app.main:app --reload`)
- [ ] API docs accessible (http://localhost:8000/docs)
- [ ] Health check passes
- [ ] Frontend `.env.local` updated
- [ ] CORS configured for frontend origin
