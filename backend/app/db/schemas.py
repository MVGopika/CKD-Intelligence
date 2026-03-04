"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

# ============== Auth Schemas ==============
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    role_name: str  # "patient" or "doctor"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    role_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ============== Patient Profile Schemas ==============
class PatientProfileCreate(BaseModel):
    date_of_birth: datetime
    sex: str  # M or F
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    medical_history: Optional[str] = None
    medications: Optional[str] = None

class PatientProfileUpdate(BaseModel):
    date_of_birth: Optional[datetime] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    medical_history: Optional[str] = None
    medications: Optional[str] = None

class PatientProfileResponse(PatientProfileCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============== Lab Result Schemas ==============
class LabResultCreate(BaseModel):
    test_date: datetime
    serum_creatinine: float
    cystatin_c: Optional[float] = None
    blood_pressure_sys: Optional[float] = None
    blood_pressure_dia: Optional[float] = None
    blood_urea: Optional[float] = None
    sodium: Optional[float] = None
    potassium: Optional[float] = None
    phosphorus: Optional[float] = None
    calcium: Optional[float] = None
    albumin: Optional[float] = None
    hemoglobin: Optional[float] = None
    lab_name: Optional[str] = None
    notes: Optional[str] = None

class LabResultResponse(LabResultCreate):
    id: int
    patient_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============== Consultation Structured Data Schema ==============

class KidneyConsultationStructured(BaseModel):
    age: int
    sex: str  # "male" or "female"
    serum_creatinine: float
    systolic_blood_pressure: float
    diastolic_blood_pressure: float
    glycated_hemoglobin: float
    medical_history: Optional[str] = None
    medications: Optional[str] = None
    bmi: float
    crp: float
    cystatin_c: float
    # Optional labs
    blood_urea: Optional[float] = None
    sodium: Optional[float] = None
    potassium: Optional[float] = None
    phosphorus: Optional[float] = None
    calcium: Optional[float] = None
    albumin: Optional[float] = None
    hemoglobin: Optional[float] = None
    test_date: Optional[datetime] = None
    lab_name: Optional[str] = None
    notes: Optional[str] = None
    
class ConsultationCreate(BaseModel):
    input_type: str
    raw_input: str
    transcription: Optional[str] = None
    structured_data: KidneyConsultationStructured
class ConsultationResponse(ConsultationCreate):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============== Prediction Schemas ==============
class PredictionCreate(BaseModel):
    patient_id: int
    consultation_id: Optional[int] = None
    input_features: Dict[str, Any]

class PredictionResponse(BaseModel):
    id: int
    patient_id: int
    consultation_id: Optional[int] = None
    egfr_predicted: float
    egfr_confidence: float
    ckd_stage: str
    stage_confidence: float
    risk_level: str
    clinical_guidance: str
    recommendations: List[str]
    shap_values: Dict[str, Any]
    top_contributing_features: List[Dict[str, Any]]
    model_version: str

    class Config:
        from_attributes = True


# ============== Doctor Schemas ==============
class DoctorPatientResponse(BaseModel):
    id: int
    full_name: str
    date_of_birth: Optional[datetime] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    medical_history: Optional[str] = None
    medications: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # latest prediction details (may be null)
    latest_ckd_stage: Optional[str] = None
    latest_egfr: Optional[float] = None
    latest_test_date: Optional[datetime] = None
    risk_level: Optional[str] = None

    class Config:
        from_attributes = True


class DoctorPatientsListResponse(BaseModel):
    """Wrapper containing a message plus the list of patients returned to a doctor."""
    message: str
    patients: List[DoctorPatientResponse]

    class Config:
        from_attributes = True

# ============== Report Schemas ==============
class ReportResponse(BaseModel):
    id: int
    prediction_id: int
    title: str
    summary: str
    detailed_analysis: str
    recommendations: str
    pdf_path: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============== Doctor Dashboard Schemas ==============
class PatientListItem(BaseModel):
    id: int
    full_name: str
    latest_ckd_stage: Optional[str] = None
    latest_egfr: Optional[float] = None
    latest_test_date: Optional[datetime] = None
    risk_level: Optional[str] = None

class PatientTrendData(BaseModel):
    date: datetime
    egfr: float
    ckd_stage: str
    test_type: str  # "lab_result", "prediction"

class PatientTrendResponse(BaseModel):
    patient_id: int
    full_name: str
    trends: List[PatientTrendData]
    current_stage: str
    current_egfr: float

# ============== Error Schemas ==============
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationError(BaseModel):
    field: str
    message: str
