"""
Utility functions for user registration and authentication
"""

import base64
import hashlib
import secrets
from typing import Tuple, Optional, Dict, Any
from PIL import Image
import io
from datetime import datetime, timedelta

try:
    import jwt
except ImportError:
    # Fallback for development
    class MockJWT:
        @staticmethod
        def encode(payload, key, algorithm):
            return "mock_token"

        @staticmethod
        def decode(token, key, algorithms):
            return {"sub": "test@example.com", "user_id": 1}

        class PyJWTError(Exception):
            pass

    jwt = MockJWT()

# JWT settings
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """
    Hash a password using a salt and SHA-256
    """
    # Generate a random salt
    salt = secrets.token_hex(16)
    # Hash the password with the salt
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    # Return salt and hash combined
    return f"{salt}:{password_hash}"

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    try:
        salt, password_hash = hashed_password.split(':')
        # Hash the provided password with the stored salt
        new_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return new_hash == password_hash
    except ValueError:
        return False

def process_profile_image(base64_image: str, filename: str) -> Tuple[bytes, str]:
    """
    Process and validate profile image
    Returns: (image_bytes, content_type)
    """
    # Decode base64 image
    image_data = base64.b64decode(base64_image)

    # Check file size (max 5MB)
    if len(image_data) > 5 * 1024 * 1024:
        raise ValueError("Image size must be less than 5MB")

    # Validate image format and get content type
    try:
        image = Image.open(io.BytesIO(image_data))

        # Check if it's JPEG or PNG
        if image.format not in ['JPEG', 'PNG']:
            raise ValueError("Image must be JPEG or PNG format")

        # Determine content type
        content_type = f"image/{image.format.lower()}"
        if content_type == "image/jpeg":
            content_type = "image/jpeg"

        # Resize image if too large (optional: resize to max 800x800)
        max_size = (800, 800)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert back to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format=image.format)
            image_data = img_buffer.getvalue()

        return image_data, content_type

    except Exception as e:
        raise ValueError(f"Invalid image format: {str(e)}")

def validate_mobile_number(mobile: str) -> bool:
    """
    Validate Bangladesh mobile number format
    Must start with +88 and be exactly 14 digits
    """
    if not mobile.startswith('+88'):
        return False
    if len(mobile) != 14:
        return False
    if not mobile[3:].isdigit():
        return False
    return True

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"

    return True, "Password is valid"

def generate_license_number() -> str:
    """
    Generate a unique license number for doctors
    Format: DOC-YYYYMMDD-XXXXX (where X is random)
    """
    from datetime import datetime
    date_str = datetime.now().strftime("%Y%m%d")
    random_part = secrets.token_hex(3).upper()  # 6 character hex
    return f"DOC-{date_str}-{random_part}"

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add JWT ID for blacklist tracking
    jti = secrets.token_hex(16)
    to_encode.update({"exp": expire, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT access token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def is_token_blacklisted(jti: str, db) -> bool:
    """
    Check if a token is blacklisted
    """
    from models import TokenBlacklist
    blacklisted_token = db.query(TokenBlacklist).filter(TokenBlacklist.token_jti == jti).first()
    return blacklisted_token is not None

def blacklist_token(token: str, user_id: int, db) -> bool:
    """
    Add a token to the blacklist
    """
    try:
        from models import TokenBlacklist
        payload = verify_access_token(token)
        if not payload:
            return False

        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti or not exp:
            return False

        # Convert exp timestamp to datetime
        expires_at = datetime.utcfromtimestamp(exp)

        # Create blacklist entry
        blacklist_entry = TokenBlacklist(
            token_jti=jti,
            user_id=user_id,
            expires_at=expires_at
        )

        db.add(blacklist_entry)
        db.commit()
        return True

    except Exception:
        db.rollback()
        return False

def get_current_user_from_token(token: str, db):
    """
    Get current user from JWT token, checking blacklist
    """
    from models import User

    # Verify token
    payload = verify_access_token(token)
    if not payload:
        return None

    # Check if token is blacklisted
    jti = payload.get("jti")
    if jti and is_token_blacklisted(jti, db):
        return None

    # Get user
    user_id = payload.get("user_id")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user

def cleanup_expired_blacklisted_tokens(db):
    """
    Remove expired tokens from blacklist to keep the table clean
    """
    try:
        from models import TokenBlacklist
        current_time = datetime.utcnow()

        # Delete expired blacklisted tokens
        db.query(TokenBlacklist).filter(
            TokenBlacklist.expires_at < current_time
        ).delete()

        db.commit()
        return True
    except Exception:
        db.rollback()
        return False

# FastAPI dependency function
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    FastAPI dependency to get current authenticated user
    """
    token = credentials.credentials
    user = get_current_user_from_token(token, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def require_admin(current_user = Depends(get_current_user)):
    """
    FastAPI dependency to require admin permissions
    """
    from models import UserType

    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
