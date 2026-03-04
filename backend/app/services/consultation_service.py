"""Business logic for consultations"""
from sqlalchemy.orm import Session
from ..db import models


def create_consultation(db: Session, user_id: int, data: dict):
    consult = models.Consultation(user_id=user_id, **data)
    db.add(consult)
    db.commit()
    db.refresh(consult)
    return consult


def list_consultations(db: Session, user_id: int):
    return db.query(models.Consultation).filter(models.Consultation.user_id == user_id).all()
