"""
SQLAlchemy database models for CKD Intelligence backend
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class Role(Base):
    """User roles (patient, doctor, admin)"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String(255))
    
    users = relationship("User", back_populates="role")

class User(Base):
    """User accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")
    
    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False)
    consultations = relationship("Consultation", back_populates="user")
    doctor_patients = relationship(
        "PatientProfile",
        secondary="doctor_patients",
        back_populates="assigned_doctors"
    )

class PatientProfile(Base):
    """Patient details and medical history"""
    __tablename__ = "patient_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    date_of_birth = Column(DateTime)
    sex = Column(String(10))  # M, F
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    medical_history = Column(Text, nullable=True)
    medications = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="patient_profile")
    lab_results = relationship("LabResult", back_populates="patient")
    predictions = relationship("Prediction", back_populates="patient")
    assigned_doctors = relationship(
        "User",
        secondary="doctor_patients",
        back_populates="doctor_patients"
    )

class Consultation(Base):
    """Consultation records (voice/text input)"""
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    input_type = Column(String(20))  # "voice", "text"
    raw_input = Column(Text)
    transcription = Column(Text, nullable=True)  # For voice inputs
    structured_data = Column(JSON)  # Structured parsed symptoms/data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="consultations")
    prediction = relationship("Prediction", back_populates="consultation", uselist=False)

class LabResult(Base):
    """Laboratory test results"""
    __tablename__ = "lab_results"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), index=True)
    test_date = Column(DateTime, index=True)
    
    # Key biomarkers
    serum_creatinine = Column(Float)  # mg/dL
    cystatin_c = Column(Float, nullable=True)  # mg/L
    blood_pressure_sys = Column(Float, nullable=True)  # mmHg
    blood_pressure_dia = Column(Float, nullable=True)  # mmHg
    
    # Additional biomarkers
    blood_urea = Column(Float, nullable=True)
    sodium = Column(Float, nullable=True)
    potassium = Column(Float, nullable=True)
    phosphorus = Column(Float, nullable=True)
    calcium = Column(Float, nullable=True)
    albumin = Column(Float, nullable=True)
    hemoglobin = Column(Float, nullable=True)
    
    # Metadata
    lab_name = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("PatientProfile", back_populates="lab_results")

class Prediction(Base):
    """ML predictions for CKD"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=True, unique=True)
    
    # Inputs
    input_features = Column(JSON)
    
    # eGFR Predictions
    egfr_predicted = Column(Float)
    egfr_confidence = Column(Float)
    
    # CKD Stage predictions
    ckd_stage = Column(String(10))  # "1", "2", "3", "4", "5"
    stage_confidence = Column(Float)
    
    # Risk assessment
    risk_level = Column(String(50))  # "low", "moderate", "high", "critical"
    
    # SHAP Explainability
    shap_values = Column(JSON)  # JSON array of feature importance
    top_contributing_features = Column(JSON)  # List of top 5 features
    
    # Clinical guidance
    clinical_guidance = Column(Text)
    recommendations = Column(JSON)  # List of stage-based recommendations
    
    # Metadata
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    patient = relationship("PatientProfile", back_populates="predictions")
    consultation = relationship("Consultation", back_populates="prediction")
    report = relationship("Report", back_populates="prediction", uselist=False)

class Report(Base):
    """Generated clinical reports"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), unique=True)
    
    # Report content
    title = Column(String(255))
    summary = Column(Text)
    detailed_analysis = Column(Text)
    recommendations = Column(Text)
    pdf_path = Column(String(255), nullable=True)
    
    # Metadata
    generated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prediction = relationship("Prediction", back_populates="report")

class DoctorPatient(Base):
    """Association table linking doctors to patients"""
    __tablename__ = "doctor_patients"
    
    doctor_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), primary_key=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
