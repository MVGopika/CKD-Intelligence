"""
Consultation API - Handles structured kidney consultations,
lab creation, ML prediction, and database storage.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db import models, schemas
from app.api.deps import get_db_session, get_patient_user
from app.services import consultation_service
from app.services import prediction_service
from app.services.clinical_service import ClinicalGuidanceService

router = APIRouter(prefix="/api/consultation", tags=["Consultation"])


# ============================================================
# CREATE CONSULTATION
# ============================================================

@router.post("", response_model=schemas.ConsultationResponse)
def create_consultation(
    consultation: schemas.ConsultationCreate,
    current_user: models.User = Depends(get_patient_user),
    db: Session = Depends(get_db_session),
):
    """
    Create a new consultation:
    - Store consultation
    - Create lab result
    - Run ML prediction
    - Store prediction
    """

    # ==============================
    # 1️⃣ Save Consultation
    # ==============================
    new_consultation = models.Consultation(
        user_id=current_user.id,
        input_type=consultation.input_type,
        raw_input=consultation.raw_input,
        transcription=consultation.transcription,
        structured_data=consultation.structured_data.dict(),
    )

    db.add(new_consultation)
    db.commit()
    db.refresh(new_consultation)

    # ==============================
    # 2️⃣ Get Patient Profile
    # ==============================
    patient = db.query(models.PatientProfile).filter(
        models.PatientProfile.user_id == current_user.id
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    structured = consultation.structured_data

    # ==============================
    # 3️⃣ Update Patient History
    # ==============================
    patient.medical_history = structured.medical_history
    patient.medications = structured.medications
    db.commit()

    # ==============================
    # 4️⃣ Create Lab Result
    # ==============================
    lab_result = models.LabResult(
        patient_id=patient.id,
        test_date=structured.test_date or datetime.utcnow(),
        serum_creatinine=structured.serum_creatinine,
        cystatin_c=None,
        blood_pressure_sys=structured.systolic_blood_pressure,
        blood_pressure_dia=structured.diastolic_blood_pressure,
        blood_urea=structured.blood_urea,
        sodium=structured.sodium,
        potassium=structured.potassium,
        phosphorus=structured.phosphorus,
        calcium=structured.calcium,
        albumin=structured.albumin,
        hemoglobin=structured.hemoglobin,
        lab_name=structured.lab_name,
        notes=structured.notes,
    )

    db.add(lab_result)
    db.commit()
    db.refresh(lab_result)

    # ==============================
    # 5️⃣ Prepare ML Features
    # ==============================
    features = {
        "age": structured.age,
        "sex": 0 if structured.sex.lower() == "male" else 1,
        "serum_creatinine": structured.serum_creatinine,
        "cystatin_c": 0,
        "blood_pressure_sys": structured.systolic_blood_pressure,
        "blood_pressure_dia": structured.diastolic_blood_pressure,
        "blood_urea": structured.blood_urea or 0,
        "sodium": structured.sodium or 0,
        "potassium": structured.potassium or 0,
    }

    # ==============================
    # 6️⃣ Run ML Prediction
    # ==============================
    pred_dict, risk_level = prediction_service.generate_prediction(features)

    guidance = ClinicalGuidanceService.get_stage_guidance(
        pred_dict["ckd_stage"],
        pred_dict["egfr_predicted"],
    )

    # ==============================
    # 7️⃣ Save Prediction
    # ==============================
    prediction = models.Prediction(
        patient_id=patient.id,
        consultation_id=new_consultation.id,
        input_features=features,
        egfr_predicted=pred_dict["egfr_predicted"],
        egfr_confidence=pred_dict["egfr_confidence"],
        ckd_stage=pred_dict["ckd_stage"],
        stage_confidence=pred_dict["stage_confidence"],
        risk_level=pred_dict["risk_level"],
        shap_values=pred_dict["shap_values"],
        top_contributing_features=pred_dict["top_contributing_features"],
        clinical_guidance=guidance["clinical_guidance"],
        recommendations=guidance["recommendations"],
        model_version="1.0",
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return schemas.ConsultationResponse.from_orm(new_consultation)


# ============================================================
# LIST CONSULTATIONS
# ============================================================

@router.get("", response_model=List[schemas.ConsultationResponse])
def list_consultations(
    current_user: models.User = Depends(get_patient_user),
    db: Session = Depends(get_db_session),
):
    consultations = db.query(models.Consultation).filter(
        models.Consultation.user_id == current_user.id
    ).order_by(models.Consultation.created_at.desc()).all()

    return consultations