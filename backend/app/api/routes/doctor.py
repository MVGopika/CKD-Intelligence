from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import models, schemas
from app.api.deps import get_db_session, get_doctor_user

router = APIRouter(prefix="/api/doctor", tags=["Doctor"])

@router.get("/patients", response_model=schemas.DoctorPatientsListResponse)
def get_assigned_patients(
    current_user: models.User = Depends(get_doctor_user),
    db: Session = Depends(get_db_session),
):
    # start with any explicit doctor-->patient links
    patients = current_user.doctor_patients or []

    # if there are no assigned patients, fall back to all profiles in the
    # database (useful when doctors haven't been linked yet or for testing)
    if not patients:
        patients = db.query(models.PatientProfile).all()

    patient_list = []
    for patient in patients:
        # include demographic/medical fields from profile
        latest_pred = (
            db.query(models.Prediction)
            .filter(models.Prediction.patient_id == patient.id)
            .order_by(models.Prediction.created_at.desc())
            .first()
        )

        patient_data = {
            "id": patient.id,
            "full_name": patient.user.full_name,
            "date_of_birth": patient.date_of_birth,
            "sex": patient.sex,
            "height_cm": patient.height_cm,
            "weight_kg": patient.weight_kg,
            "medical_history": patient.medical_history,
            "medications": patient.medications,
            "created_at": patient.created_at,
            "updated_at": patient.updated_at,
        }

        if latest_pred:
            patient_data.update({
                "latest_ckd_stage": latest_pred.ckd_stage,
                "latest_egfr": latest_pred.egfr_predicted,
                "latest_test_date": latest_pred.created_at,
                "risk_level": latest_pred.risk_level,
            })
        else:
            # ensure keys exist even if no prediction
            patient_data.update(
                {
                    "latest_ckd_stage": None,
                    "latest_egfr": None,
                    "latest_test_date": None,
                    "risk_level": None,
                }
            )

        patient_list.append(patient_data)

    # include a helpful message in the response body
    return {"message": "assigned patients fetched", "patients": patient_list}
