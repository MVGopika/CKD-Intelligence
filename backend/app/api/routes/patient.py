from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import models, schemas
from app.api.deps import get_db_session, get_patient_user

router = APIRouter(prefix="/api/patient", tags=["Patient"])


@router.post("/profile", response_model=schemas.PatientProfileResponse)
def create_profile(
    payload: schemas.PatientProfileCreate,
    current_user: models.User = Depends(get_patient_user),
    db: Session = Depends(get_db_session),
):
    # prevent duplicate profiles
    existing = db.query(models.PatientProfile).filter(models.PatientProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists")
    profile = models.PatientProfile(
        user_id=current_user.id,
        date_of_birth=payload.date_of_birth,
        sex=payload.sex,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg,
        medical_history=payload.medical_history,
        medications=payload.medications,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return schemas.PatientProfileResponse.from_orm(profile)


@router.get("/profile", response_model=schemas.PatientProfileResponse)
def get_profile(
    current_user: models.User = Depends(get_patient_user),
    db: Session = Depends(get_db_session),
):
    profile = db.query(models.PatientProfile).filter(models.PatientProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return schemas.PatientProfileResponse.from_orm(profile)


@router.post("/lab-results", response_model=schemas.LabResultResponse)
def add_lab_result(
    payload: schemas.LabResultCreate,
    current_user: models.User = Depends(get_patient_user),
    db: Session = Depends(get_db_session),
):
    profile = db.query(models.PatientProfile).filter(models.PatientProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    lr = models.LabResult(
        patient_id=profile.id,
        test_date=payload.test_date,
        serum_creatinine=payload.serum_creatinine,
        cystatin_c=payload.cystatin_c,
        blood_pressure_sys=payload.blood_pressure_sys,
        blood_pressure_dia=payload.blood_pressure_dia,
        blood_urea=payload.blood_urea,
        sodium=payload.sodium,
        potassium=payload.potassium,
        phosphorus=payload.phosphorus,
        calcium=payload.calcium,
        albumin=payload.albumin,
        hemoglobin=payload.hemoglobin,
        lab_name=payload.lab_name,
        notes=payload.notes,
    )
    db.add(lr)
    db.commit()
    db.refresh(lr)
    return schemas.LabResultResponse.from_orm(lr)


@router.get("/lab-results", response_model=list[schemas.LabResultResponse])
def get_lab_results(
    current_user: models.User = Depends(get_patient_user),
    db: Session = Depends(get_db_session),
):
    profile = db.query(models.PatientProfile).filter(models.PatientProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    results = db.query(models.LabResult).filter(models.LabResult.patient_id == profile.id).order_by(models.LabResult.test_date.desc()).all()
    return [schemas.LabResultResponse.from_orm(r) for r in results]
