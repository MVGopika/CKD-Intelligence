from fastapi import Depends
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..core.security import get_current_user, get_doctor_user, get_patient_user

# re-export dependencies for convenience

DbSession = Depends(get_db)
get_db_session = get_db

get_current_user_dep = Depends(get_current_user)
get_doctor_user_dep = Depends(get_doctor_user)
get_patient_user_dep = Depends(get_patient_user)
