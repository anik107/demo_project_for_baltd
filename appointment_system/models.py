from database import Base
from sqlalchemy import Column, Integer, String, Enum, Float, Boolean, ForeignKey, DateTime, Text, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

class UserType(str, enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"

class AppointmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class Division(Base):
    __tablename__ = 'divisions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    # Relationship
    districts = relationship("District", back_populates="division")

class District(Base):
    __tablename__ = 'districts'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    division_id = Column(Integer, ForeignKey('divisions.id'), nullable=False)

    # Relationships
    division = relationship("Division", back_populates="districts")
    thanas = relationship("Thana", back_populates="district")

class Thana(Base):
    __tablename__ = 'thanas'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    district_id = Column(Integer, ForeignKey('districts.id'), nullable=False)

    # Relationship
    district = relationship("District", back_populates="thanas")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mobile_number = Column(String, unique=True, index=True, nullable=False)  # Must start with +88, exactly 14 digits
    hashed_password = Column(String, nullable=False)  # Min 8 chars, 1 uppercase, 1 digit, 1 special char
    user_type = Column(Enum(UserType), nullable=False)

    # Address fields
    division_id = Column(Integer, ForeignKey('divisions.id'), nullable=False)
    district_id = Column(Integer, ForeignKey('districts.id'), nullable=False)
    thana_id = Column(Integer, ForeignKey('thanas.id'), nullable=False)

    # Profile image
    profile_image_filename = Column(String, nullable=True)
    profile_image_content_type = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    division = relationship("Division")
    district = relationship("District")
    thana = relationship("Thana")

    # Doctor specific relationship
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)

class DoctorProfile(Base):
    __tablename__ = 'doctor_profiles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    license_number = Column(String, unique=True, nullable=False)
    experience_years = Column(Integer, nullable=False)
    consultation_fee = Column(Float, nullable=False)

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    available_timeslots = relationship("DoctorTimeslot", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")

class DoctorTimeslot(Base):
    __tablename__ = 'doctor_timeslots'

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey('doctor_profiles.id'), nullable=False)
    start_time = Column(String, nullable=False)  # Format: "10:00"
    end_time = Column(String, nullable=False)    # Format: "11:00"
    is_available = Column(Boolean, default=True)

    # Relationship
    doctor = relationship("DoctorProfile", back_populates="available_timeslots")

class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctor_profiles.id'), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    notes = Column(Text, nullable=True)  # Optional symptoms/notes
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    doctor = relationship("DoctorProfile", foreign_keys=[doctor_id])

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    user = relationship("User")

class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    id = Column(Integer, primary_key=True, index=True)
    token_jti = Column(String, unique=True, nullable=False, index=True)  # JWT ID claim
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)  # When the token would naturally expire

    # Relationship
    user = relationship("User")