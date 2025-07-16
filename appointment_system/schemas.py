from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
from datetime import datetime, date, time
import re
from models import UserType, AppointmentStatus

class DivisionBase(BaseModel):
    name: str

class DivisionCreate(DivisionBase):
    pass

class Division(DivisionBase):
    id: int

    class Config:
        from_attributes = True

class DistrictBase(BaseModel):
    name: str
    division_id: int

class DistrictCreate(DistrictBase):
    pass

class District(DistrictBase):
    id: int

    class Config:
        from_attributes = True

class ThanaBase(BaseModel):
    name: str
    district_id: int

class ThanaCreate(ThanaBase):
    pass

class Thana(ThanaBase):
    id: int

    class Config:
        from_attributes = True

class DoctorTimeslotBase(BaseModel):
    start_time: str = Field(..., description="Format: HH:MM (e.g., 10:00)")
    end_time: str = Field(..., description="Format: HH:MM (e.g., 11:00)")
    is_available: bool = True

    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v):
        if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError('Time must be in HH:MM format (e.g., 10:00)')
        return v

class DoctorTimeslotCreate(DoctorTimeslotBase):
    pass

class DoctorTimeslot(DoctorTimeslotBase):
    id: int

    class Config:
        from_attributes = True

class DoctorProfileBase(BaseModel):
    license_number: str
    experience_years: int = Field(..., ge=0, description="Experience in years")
    consultation_fee: float = Field(..., ge=0, description="Consultation fee")

class DoctorProfileCreate(DoctorProfileBase):
    available_timeslots: List[DoctorTimeslotCreate] = []

class DoctorProfile(DoctorProfileBase):
    id: int
    user_id: int
    available_timeslots: List[DoctorTimeslot] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    mobile_number: str
    user_type: UserType
    division_id: int
    district_id: int
    thana_id: int

    @field_validator('mobile_number')
    @classmethod
    def validate_mobile_number(cls, v):
        # Must start with +88 and be exactly 14 digits
        if not v.startswith('+88'):
            raise ValueError('Mobile number must start with +88')
        if len(v) != 14:
            raise ValueError('Mobile number must be exactly 14 digits including +88')
        if not v[3:].isdigit():
            raise ValueError('Mobile number must contain only digits after +88')
        return v

class UserCreate(UserBase):
    password: str
    profile_image_base64: Optional[str] = None
    profile_image_filename: Optional[str] = None
    doctor_profile: Optional[DoctorProfileCreate] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('profile_image_base64')
    @classmethod
    def validate_profile_image(cls, v):
        if v is not None:
            # Basic base64 validation and size check
            import base64
            try:
                image_data = base64.b64decode(v)
                # Check if image is less than 5MB
                if len(image_data) > 5 * 1024 * 1024:
                    raise ValueError('Profile image must be less than 5MB')
            except Exception:
                raise ValueError('Invalid base64 image data')
        return v

    @field_validator('profile_image_filename')
    @classmethod
    def validate_image_filename(cls, v):
        if v is not None:
            allowed_extensions = ['.jpg', '.jpeg', '.png']
            if not any(v.lower().endswith(ext) for ext in allowed_extensions):
                raise ValueError('Profile image must be JPEG or PNG format')
        return v

class User(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    doctor_profile: Optional[DoctorProfile] = None
    division: Optional[Division] = None
    district: Optional[District] = None
    thana: Optional[Thana] = None
    profile_image_filename: Optional[str] = None
    profile_image_content_type: Optional[str] = None

    @property
    def profile_image_url(self) -> Optional[str]:
        """Get the URL for the profile image"""
        if self.profile_image_filename:
            return f"/static/profiles/{self.profile_image_filename}"
        return None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None
    division_id: Optional[int] = None
    district_id: Optional[int] = None
    thana_id: Optional[int] = None
    profile_image_base64: Optional[str] = None
    profile_image_filename: Optional[str] = None

    @field_validator('mobile_number')
    @classmethod
    def validate_mobile_number(cls, v):
        if v is not None:
            if not v.startswith('+88'):
                raise ValueError('Mobile number must start with +88')
            if len(v) != 14:
                raise ValueError('Mobile number must be exactly 14 digits including +88')
            if not v[3:].isdigit():
                raise ValueError('Mobile number must contain only digits after +88')
        return v

# Appointment Schemas
class AppointmentBase(BaseModel):
    doctor_id: int
    appointment_date: date
    appointment_time: time
    notes: Optional[str] = Field(None, max_length=1000, description="Optional symptoms or notes")

    @field_validator('appointment_date')
    @classmethod
    def validate_appointment_date(cls, v):
        from datetime import date
        if v < date.today():
            raise ValueError('Appointment date cannot be in the past')
        return v

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[AppointmentStatus] = None

    @field_validator('appointment_date')
    @classmethod
    def validate_appointment_date(cls, v):
        if v is not None:
            from datetime import date
            if v < date.today():
                raise ValueError('Appointment date cannot be in the past')
        return v

class Appointment(AppointmentBase):
    id: int
    patient_id: int
    status: AppointmentStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Include related data
    patient: Optional['User'] = None
    doctor: Optional['DoctorProfile'] = None

    class Config:
        from_attributes = True

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    notes: Optional[str] = None
    status: AppointmentStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Patient and doctor information
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None
    patient_mobile: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_license: Optional[str] = None
    consultation_fee: Optional[float] = None

    class Config:
        from_attributes = True

# Notification Schemas
class NotificationBase(BaseModel):
    pass

class NotificationCreate(NotificationBase):
    user_id: int = Field(..., description="ID of the user to receive the notification")

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: bool = False
    created_at: Optional[datetime] = None

    # Include related user data
    user: Optional['User'] = None

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    is_read: bool
    created_at: Optional[datetime] = None

    # User information
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True
