from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from notification_service import NotificationService
from schemas import NotificationResponse, User
from auth_utils import get_current_user
from typing import List

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

@router.get("", response_model=List[NotificationResponse])
async def get_user_notifications(
    skip: int = 0,
    limit: int = 20,
    read_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for the current user"""
    try:
        notifications = NotificationService.get_user_notifications(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            read_only=read_only
        )
        return notifications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching notifications: {str(e)}"
        )

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications for the current user"""
    try:
        count = NotificationService.get_unread_count(db=db, user_id=current_user.id)
        return {"unread_count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching notification count: {str(e)}"
        )

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read"""
    try:
        notification = NotificationService.mark_as_read(
            db=db,
            notification_id=notification_id,
            user_id=current_user.id
        )
        return {"message": "Notification marked as read", "notification": notification}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating notification: {str(e)}"
        )

@router.put("/mark-all-read")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the current user"""
    try:
        updated_count = NotificationService.mark_all_as_read(
            db=db,
            user_id=current_user.id
        )
        return {"message": f"Marked {updated_count} notifications as read"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating notifications: {str(e)}"
        )

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific notification"""
    try:
        success = NotificationService.delete_notification(
            db=db,
            notification_id=notification_id,
            user_id=current_user.id
        )
        if success:
            return {"message": "Notification deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting notification: {str(e)}"
        )
