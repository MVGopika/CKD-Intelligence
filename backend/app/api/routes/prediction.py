from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db import models, schemas
from app.api.deps import get_db_session, get_patient_user
from app.services import prediction_service
from app.services.clinical_service import ClinicalGuidanceService

router = APIRouter(prefix="/api/predict", tags=["Prediction"])

@router.post("", response_model=schemas.PredictionResponse)
def create_prediction(
    lab_data: schemas.LabResultCreate,
    current_user: models.User = Depends(get_patient_user),
    db: Session = Depends(get_db_session),
):
    patient = db.query(models.PatientProfile).filter(
        models.PatientProfile.user_id == current_user.id
    ).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    features = {
        'age': (datetime.now() - patient.date_of_birth).days // 365,
        'sex': 0 if patient.sex == 'M' else 1,
        'serum_creatinine': lab_data.serum_creatinine,
        'cystatin_c': lab_data.cystatin_c or 0,
        'blood_pressure_sys': lab_data.blood_pressure_sys or 0,
        'blood_pressure_dia': lab_data.blood_pressure_dia or 0,
        'blood_urea': lab_data.blood_urea or 0,
        'sodium': lab_data.sodium or 0,
        'potassium': lab_data.potassium or 0,
    }

    # run ML pipeline
    pred_dict, risk_level = prediction_service.generate_prediction(features)

    guidance = ClinicalGuidanceService.get_stage_guidance(pred_dict['ckd_stage'], pred_dict['egfr_predicted'])

    prediction = models.Prediction(
        patient_id=patient.id,
        input_features=features,
        egfr_predicted=pred_dict['egfr_predicted'],
        egfr_confidence=pred_dict['egfr_confidence'],
        ckd_stage=pred_dict['ckd_stage'],
        stage_confidence=pred_dict['stage_confidence'],
        risk_level=pred_dict['risk_level'],
        shap_values=pred_dict['shap_values'],
        top_contributing_features=pred_dict['top_contributing_features'],
        clinical_guidance=guidance['clinical_guidance'],
        recommendations=guidance['recommendations'],
        model_version="1.0",
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    # 🔥 AUTO REPORT GENERATION
    from app.services.report_service import generate_report
    generate_report(db, prediction)
    return schemas.PredictionResponse.from_orm(prediction)

@router.get("/{prediction_id}", response_model=schemas.PredictionResponse)
def get_prediction(
    prediction_id: int,
    current_user: models.User = Depends(get_patient_user),
    db: Session = Depends(get_db_session),
):
    patient = db.query(models.PatientProfile).filter(
        models.PatientProfile.user_id == current_user.id
    ).first()
    prediction = db.query(models.Prediction).filter(
        models.Prediction.id == prediction_id,
        models.Prediction.patient_id == patient.id,
    ).first()
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )
    return schemas.PredictionResponse.from_orm(prediction)
