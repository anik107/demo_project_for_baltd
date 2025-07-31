from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, joinedload
import models
from auth_utils import get_current_user_from_token
from database import SessionLocal, get_db
from schemas import User as UserSchema
from user_service import UserService
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/doctors",
    tags=["doctors"]
)

templates = Jinja2Templates(directory="templates")

def get_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """Get user from cookie token"""
    token = request.cookies.get("access_token") or request.cookies.get("admin_token")

    if not token:
        return None

    try:
        user = get_current_user_from_token(token, db)
        return user
    except:
        return None

def get_user_from_bearer_token(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Get user from Bearer token"""
    if not authorization:
        return None

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None

        user = get_current_user_from_token(token, db)
        return user
    except:
        return None
def get_authenticated_user(request: Request, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Get user from either cookie or bearer token"""
    # Try bearer token first
    user = get_user_from_bearer_token(authorization, db)
    if user:
        return user

    # Fallback to cookie
    user = get_user_from_cookie(request, db)
    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )

@router.get("/list", response_class=HTMLResponse)
async def get_all_doctors(
    request: Request,
    db: Session = Depends(get_db)
):
    """View all doctors"""
    doctors = db.query(models.DoctorProfile).options(
        joinedload(models.DoctorProfile.user),
        joinedload(models.DoctorProfile.available_timeslots)
    ).all()

    return templates.TemplateResponse("doctors_list.html", {
        "request": request,
        "doctors": doctors
    })

@router.get("/count_doctors", response_model=int)
async def count_doctors(db: Session = Depends(get_db),
                        current_user: UserSchema = Depends(get_authenticated_user)):
    """Count all doctors"""
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized to count doctors")
    doctors_record = UserService.get_doctors(db)
    return len(doctors_record)