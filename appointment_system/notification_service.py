from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List
from models import Notification, User
from schemas import NotificationCreate, NotificationResponse, Notification as NotificationSchema
from fastapi import HTTPException

class NotificationService:

    @staticmethod
    def create_notification(db: Session, appointment_data: NotificationCreate) -> NotificationSchema:
        """Create a notification if appointment is exactly 1 day away and no unread notification exists."""
        try:
            user_id = appointment_data.patient_id
            appointment_date = appointment_data.appointment_date

            # Step 1: Verify user exists
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Step 2: Check existing notification
            existing_notification = db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            ).first()

            if existing_notification:
                created_at_date = existing_notification.created_at.date()
                # Compare with appointment_date
                if (appointment_date - created_at_date).days == 1:
                    existing_notification.is_read = True
                    db.commit()
                    db.refresh(existing_notification)
                return NotificationSchema.from_orm(existing_notification)

            # Step 3: Create new notification
            db_notification = Notification(user_id=user_id)
            db.add(db_notification)
            db.commit()
            db.refresh(db_notification)

            # Step 4: Auto mark is_read if appointment_date - created_at == 1 day
            if (appointment_date - db_notification.created_at.date()).days == 1:
                db_notification.is_read = True
                db.commit()
                db.refresh(db_notification)

            return NotificationSchema.from_orm(db_notification)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        read_only: bool = True
    ) -> List[NotificationResponse]:
        """Get notifications for a specific user"""
        try:
            query = db.query(Notification).join(User).filter(Notification.user_id == user_id)

            if read_only:
                query = query.filter(Notification.is_read == True)

            notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()

            # Convert to response format with user information
            notification_responses = []
            for notification in notifications:
                response = NotificationResponse(
                    id=notification.id,
                    user_id=notification.user_id,
                    is_read=notification.is_read,
                    created_at=notification.created_at.isoformat(),
                    user_name=notification.user.full_name,
                    user_email=notification.user.email
                )
                notification_responses.append(response)

            return notification_responses

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")


    @staticmethod
    def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
        """Delete a notification"""
        try:
            notification = db.query(Notification).filter(
                and_(Notification.id == notification_id, Notification.user_id == user_id)
            ).first()

            if not notification:
                raise HTTPException(status_code=404, detail="Notification not found")

            db.delete(notification)
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting notification: {str(e)}")

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """Get count of unread notifications for a user"""
        try:
            count = db.query(Notification).filter(
                and_(Notification.user_id == user_id, Notification.is_read == False)
            ).count()
            return count

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error counting notifications: {str(e)}")
