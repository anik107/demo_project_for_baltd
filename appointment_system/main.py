from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routers import auth, users, locations, general, doctors, appointments, admin, notifications
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import SessionLocal, engine
from location_utils import seed_location_data

app = FastAPI(
    title="Appointment System API",
    description="A comprehensive appointment system for patients and doctors",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create tables
models.Base.metadata.create_all(bind=engine)

from pathlib import Path

# Get the directory of this file for proper path resolution
BASE_DIR = Path(__file__).parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Include routers with /api prefix for API endpoints
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(doctors.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")

# Include admin router without prefix for admin panel
app.include_router(admin.router)

# Include general router without prefix for serving HTML pages
app.include_router(general.router)

# Add a route to manually trigger reminder notifications (for testing/admin use)
@app.post("/api/admin/send-reminders")
async def trigger_reminder_notifications():
    """Manually trigger sending of reminder notifications"""
    from task_scheduler import TaskScheduler

    db = SessionLocal()
    try:
        reminders_sent = TaskScheduler.send_daily_appointment_reminders(db)
        return {"message": f"Successfully sent {reminders_sent} reminder notifications"}
    except Exception as e:
        return {"error": f"Failed to send reminders: {str(e)}"}
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """Initialize database with location data on startup"""
    db = SessionLocal()
    try:
        seed_location_data(db)
    except Exception as e:
        print(f"Error during startup: {e}")
    finally:
        db.close()
