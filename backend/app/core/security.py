"""
Authentication and security utilities
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import get_settings
from ..db.models import User
from ..db.database import get_db

# workaround for passlib/bcrypt version detection bug
# sometimes `bcrypt` package does not expose __about__ attribute
# which passlib tries to read and logs a trapped error.  Provide
# a minimal stub so the message disappears and the backend loads.
try:
    import bcrypt
    if not hasattr(bcrypt, "__about__"):
        class _About:  # simple object with version attribute
            __version__ = getattr(bcrypt, "__version__", "0")
        bcrypt.__about__ = _About()
except ImportError:
    # bcrypt isn't installed yet; let passlib handle it later
    pass

settings = get_settings()

# Password hashing (passlib context kept for compatibility but not used below)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def _normalize_for_bcrypt(password: str) -> str:
    """Enforce bcrypt's 72‑byte limit by truncating UTF‑8 bytes.

    Bcrypt silently ignores any bytes beyond the first 72, which can lead
    to subtle verification failures and the runtime error observed when a
    caller accidentally passes a longer string.  To keep behavior
    deterministic we explicitly truncate here and apply the same logic for
    both hashing and verification.
    """
    if not isinstance(password, str):
        password = str(password)
    pw_bytes = password.encode("utf-8", errors="ignore")
    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]
        # decode back to str ignoring any partial character at the end
        password = pw_bytes.decode("utf-8", errors="ignore")
    return password


def hash_password(password: str) -> str:
    """Hash a password using the bcrypt library directly.

    We switched away from passlib because some versions of ``bcrypt`` no
    longer expose ``__about__`` and also trigger a bug in passlib's
    backend initialization (see log trace above).  Using the underlying
    library eliminates that dependency and gives us deterministic
    control over the bytes that are fed to the algorithm.
    """
    safe = _normalize_for_bcrypt(password)
    # bcrypt expects ``bytes``.  ``gensalt`` chooses a reasonable cost
    # (default 12) and automatically generates a salt prefix.
    hashed = bcrypt.hashpw(safe.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using ``bcrypt`` directly."""
    safe = _normalize_for_bcrypt(plain_password)
    try:
        return bcrypt.checkpw(safe.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        # invalid hash format
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    # ensure subject is represented as a string (JWT spec prefers string subjects)
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode a JWT token"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        raise credentials_exception
    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    return user

async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify that current user is admin"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_doctor_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify that current user is a doctor"""
    if current_user.role.name not in ["doctor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor access required"
        )
    return current_user

async def get_patient_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify that current user is a patient"""
    if current_user.role.name not in ["patient", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient access required"
        )
    return current_user
