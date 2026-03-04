"""Business logic for authentication and user management"""
from sqlalchemy.orm import Session
from ..db import models
from ..core import security


def register_user(db: Session, email: str, password: str, full_name: str, role_name: str):
    # check existing
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        return None
    # ensure role exists
    role = db.query(models.Role).filter(models.Role.name == role_name).first()
    if not role:
        role = models.Role(name=role_name, description=f"{role_name.capitalize()} role")
        db.add(role)
        db.flush()
    user = models.User(
        email=email,
        hashed_password=security.hash_password(password),
        full_name=full_name,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not security.verify_password(password, user.hashed_password):
        return None
    return user
