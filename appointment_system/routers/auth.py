from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas import UserCreate, User as UserSchema
from user_service import UserService
from auth_utils import verify_password, create_access_token, blacklist_token, get_current_user_from_token
from pydantic import BaseModel
from typing import Optional
import base64
from models import UserType

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    message: str
    user: UserSchema

class LogoutResponse(BaseModel):
    message: str
    success: bool

# Security scheme for bearer token
security = HTTPBearer()

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency to get the current authenticated user
    This checks if the token is valid and not blacklisted
    """
    try:
        token = credentials.credentials
        current_user = get_current_user_from_token(token, db)

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return current_user

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/login", response_model=LoginResponse)
async def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """User login endpoint"""
    try:
        # Get user by email
        user = UserService.get_user_by_email(db, login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Create access token
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            message="Login successful",
            user=UserSchema.model_validate(user)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error: {str(e)}"
        )

@router.post("/logout", response_model=LogoutResponse)
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """User logout endpoint"""
    try:
        token = credentials.credentials

        # Get current user from token
        current_user = get_current_user_from_token(token, db)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        # Blacklist the token
        success = blacklist_token(token, current_user.id, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to logout"
            )

        return LogoutResponse(
            message="Successfully logged out",
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@router.post("/refresh")
async def refresh_token():
    """Refresh authentication token"""
    # TODO: Implement token refresh logic
    pass

@router.post("/signup", response_model=UserSchema)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = UserService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/signup-with-file", response_model=UserSchema)
async def register_user_with_file(
    full_name: str = Form(...),
    email: str = Form(...),
    mobile_number: str = Form(...),
    password: str = Form(...),
    user_type: UserType = Form(...),
    division_id: str = Form(...),  # Accept as string, convert later
    district_id: str = Form(...),   # Accept as string, convert later
    thana_id: str = Form(...),      # Accept as string, convert later
    profile_image: Optional[UploadFile] = File(None),
    # Doctor profile fields (optional)
    license_number: Optional[str] = Form(None),
    experience_years: Optional[str] = Form(None),  # Accept as string, convert later
    consultation_fee: Optional[str] = Form(None),  # Accept as string, convert later
    db: Session = Depends(get_db)
):
    try:
        # Convert string values to appropriate types
        try:
            division_id_int = int(division_id)
            district_id_int = int(district_id)
            thana_id_int = int(thana_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid location IDs. Please select valid division, district, and thana."
            )

        # Prepare profile image data if uploaded
        profile_image_base64 = None
        profile_image_filename = None

        if profile_image:
            # Validate file type
            if profile_image.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Profile image must be JPEG or PNG format"
                )

            # Read and encode image
            image_content = await profile_image.read()
            profile_image_base64 = base64.b64encode(image_content).decode()
            profile_image_filename = profile_image.filename

        # Prepare doctor profile if user is a doctor
        doctor_profile = None
        if user_type == UserType.DOCTOR:
            if not all([license_number, experience_years, consultation_fee]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Doctor profile fields (license_number, experience_years, consultation_fee) are required for doctor registration"
                )

            # Convert doctor-specific string values to appropriate types
            try:
                experience_years_int = int(experience_years)
                consultation_fee_float = float(consultation_fee)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid doctor profile data. Experience years must be a number, consultation fee must be a valid amount."
                )

            from schemas import DoctorProfileCreate
            doctor_profile = DoctorProfileCreate(
                license_number=license_number,
                experience_years=experience_years_int,
                consultation_fee=consultation_fee_float
            )

        # Create UserCreate object
        user_data = UserCreate(
            full_name=full_name,
            email=email,
            mobile_number=mobile_number,
            password=password,
            user_type=user_type,
            division_id=division_id_int,
            district_id=district_id_int,
            thana_id=thana_id_int,
            profile_image_base64=profile_image_base64,
            profile_image_filename=profile_image_filename,
            doctor_profile=doctor_profile
        )

        user = UserService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.get("/dashboard", response_model=UserSchema)
async def get_dashboard_data(
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard data"""
    try:
        # Fetch user data from the database
        user = UserService.get_user_by_id(db, current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserSchema.model_validate(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard data: {str(e)}"
        )

@router.get("/dashboard-with-notifications")
async def get_dashboard_with_notifications(
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard data including recent notifications"""
    try:
        from notification_service import NotificationService

        # Fetch user data from the database
        user = UserService.get_user_by_id(db, current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Get recent notifications (last 5 unread ones)
        notifications = NotificationService.get_user_notifications(
            db=db,
            user_id=current_user.id,
            skip=0,
            limit=5,
            unread_only=True
        )

        # Get unread notification count
        unread_count = NotificationService.get_unread_count(db=db, user_id=current_user.id)

        return {
            "user": UserSchema.model_validate(user),
            "notifications": notifications,
            "unread_count": unread_count
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard data: {str(e)}"
        )

@router.get("/appointments_count")
async def get_appointments_count(
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of appointments for the current user"""
    try:
        from appointment_service import AppointmentService

        if current_user.user_type != "PATIENT":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only patients can view appointment count"
            )

        count = AppointmentService.get_appointments_count(db=db, user_id=current_user.id)
        return {"appointments_count": count}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching appointments count: {str(e)}"
        )