from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas import UserCreate, User as UserSchema
from user_service import UserService
from auth_utils import verify_password, create_access_token, blacklist_token, get_current_user_from_token
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
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

        # Convert user to schema
        user_schema = UserSchema.model_validate(user)

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_schema
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
    """
    Register a new user with the following requirements:
    - Full Name (required)
    - Email (unique, required)
    - Mobile Number (must start with +88, exactly 14 digits)
    - Password (minimum 8 characters, 1 uppercase, 1 digit, 1 special character)
    - User Type (Patient, Doctor, Admin)
    - Address (Division, District, Thana - hierarchical validation)
    - Profile Image (optional, max 5MB, JPEG/PNG only)
    - For Doctors: License Number, Experience Years, Consultation Fee, Available timeslots
    """
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