from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import models, schemas
from app.services import auth_service
from app.core.security import create_access_token, verify_password
from app.api.deps import get_db_session, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.TokenResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db_session)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    # bcrypt has a 72‑byte limit; reject overly long cleartext passwords
    if len(user.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password too long (maximum 72 bytes)"
        )
    # role creation is handled inside service
    created = auth_service.register_user(
        db, user.email, user.password, user.full_name, user.role_name
    )
    if not created:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )
    access_token = create_access_token(data={"sub": created.id})
    return { 
            "message": "User registered successfully ✅",
            "access_token": access_token, 
            "token_type": "bearer", 
            "user": schemas.UserResponse.from_orm(created)}

@router.post("/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db_session)):
    if len(credentials.password.encode("utf-8")) > 72:
        # don't even attempt authentication; never store or compare this long
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    user = auth_service.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    access_token = create_access_token(data={"sub": user.id})
    return {"message": "Login successful 🎉",
            "access_token": access_token, "token_type": "bearer", "user": schemas.UserResponse.from_orm(user)}

@router.get("/me", response_model=schemas.UserResponse)
def me(current_user: models.User = Depends(get_current_user)):
    return schemas.UserResponse.from_orm(current_user)
