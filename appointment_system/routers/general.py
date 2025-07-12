from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter(
    tags=["general"]
)

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Serve the home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Serve the signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Serve the dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/appointments", response_class=HTMLResponse)
async def appointments_page(request: Request):
    """Serve the appointments page"""
    return templates.TemplateResponse("appointments.html", {"request": request})

@router.get("/debug-token", response_class=HTMLResponse)
async def debug_token_page(request: Request):
    """Serve the token debug page"""
    return templates.TemplateResponse("debug_token.html", {"request": request})

@router.get("/login-test", response_class=HTMLResponse)
async def login_test_page(request: Request):
    """Serve the login test page"""
    return templates.TemplateResponse("login_test.html", {"request": request})

@router.get("/test-availability")
async def test_availability_page(request: Request):
    """Serve the test availability page"""
    return templates.TemplateResponse("test_availability.html", {"request": request})
