import atexit
import json
import platform
import sys
import os
import threading
from typing import Optional

from app.config import SECRET_KEY, get_config
from app.crud.user import update_user
from app.handlers.custom_http_exceptions import create_http_exception_handler
from app.utils.dependences import require_role_router
from fastapi.security import OAuth2PasswordRequestForm

from app.utils.auth_utils import get_current_user, verify_password
from middlewares.current_user_middleware import CurrentUserMiddleware

# Add the directory containing `app` to sys.path
if getattr(sys, 'frozen', False):  # Check if running in PyInstaller bundle
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI,Depends, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext

# import uvicorn
import subprocess
import time
from multiprocessing import Process, freeze_support
import tempfile
import webbrowser
from shutil import which
from app.utils.auth_utils import create_access_token, verify_password

from app.middleware import LanguageMiddleware  # Import the middleware
from app.routers import authentication, management, input_medicine, dispense_medicine, medicines, patients, prescriptions, users, manage_medicine_supply
from app.server import start_server
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import  schemas, crud
from app.models import MedicineType, User
# Create tables in the database
Base.metadata.create_all(bind=engine)
app = FastAPI()



# Dependency function to provide the configuration

# Get the absolute path to the templates directory
if getattr(sys, 'frozen', False):  # Check if running in PyInstaller bundle
    BASE_DIR = sys._MEIPASS  # Temporary directory created by PyInstaller
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
# templates_dir = os.path.join(os.path.dirname(__file__), "templates")
# if not os.path.exists(templates_dir):
#     raise RuntimeError(f"Templates directory '{templates_dir}' does not exist")
if not os.path.exists(TEMPLATE_DIR):
    raise FileNotFoundError(f"Template directory not found: {TEMPLATE_DIR}")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Define the path to the 'static' directory, ensuring it's found no matter where the script is executed from
# static_dir = os.path.join(os.path.dirname(__file__), "static")
STATIC_DIR = os.path.join(BASE_DIR, 'static')
# Check if the directory exists (this is optional but helps for debugging)
# if not os.path.exists(STATIC_DIR):
#     raise RuntimeError(f"Static directory '{STATIC_DIR}' does not exist")
if not os.path.exists(STATIC_DIR):
    raise FileNotFoundError(f"Static directory not found: {STATIC_DIR}")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(LanguageMiddleware)
app.add_middleware(CurrentUserMiddleware)
# Register the custom exception handler
app.add_exception_handler(HTTPException, create_http_exception_handler(templates))
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_translator(request: Request):
    return {"_": request.state._}


    time.sleep(1)  # Simulate a delay in action
@app.get("/", response_class=HTMLResponse)
async def redirect_to_default_language():
    return RedirectResponse(url="/he/login")
@app.get("/{lang}", response_class=HTMLResponse)
async def home(request: Request, 
               lang: str = "he",
               user=Depends(require_role_router(["Pharmacist", "Admin","Technician"]))):
    _ = request.state._
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "_": _,  # Pass the `_` function to the template
        "lang": lang,
        "user":user
    })


# Utility functions
def get_user_by_username(db: Session, username: str):
    try:
        return db.query(User).filter(User.username == username).first()
    except Exception as e:
        print(f"Error querying user: {e}")
        return None


# @app.post("/{lang}/auth")
# def authentication(
#     lang: str,
#     request: Request,
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db),
# ):
#     user = get_user_by_username(db, form_data.username)
#     if not user or not verify_password(form_data.password, user.password):
#         # Render the login template with an error message
#         _ = request.state._
#         return templates.TemplateResponse("login.html", {
#             "request": request,
#             "_": _,  # Pass the `_` function to the template
#             "lang": lang,
#             "error": _("Invalid username or password")
#         })


#     # Generate an access token (if token-based auth is used)
#     access_token = create_access_token(data={"sub": user.username},expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES)

#     # Redirect to home or dashboard on success
#     response = RedirectResponse(url=f"/{lang}", status_code=303)
#     response.set_cookie(key="access_token", value=access_token, httponly=True)
#     return response

# from fastapi.responses import JSONResponse

# @app.post("/{lang}/update_profile", response_class=HTMLResponse)
# async def update_personal_details(
#     request: Request,
#     lang: str = "he",
#     username: str = Form(...),
#     first_name: str = Form(...),
#     last_name: str = Form(...),
#     email: str = Form(...),
#     # password: Optional[str] = Form(None),
#     db: Session = Depends(get_db),
# ):
#     """
#     Update personal details and handle validation errors dynamically for modals.
#     """
#     _ = request.state._  # Translation function
#     user = request.state.user  # Get current user from middleware

#     if not user:
#         return JSONResponse({"success": False, "errors": [_("Not authenticated")]}, status_code=401)

#     errors = []

#     # Check for duplicate email
#     if db.query(User).filter(User.email == email, User.id != user.id).first():
#         errors.append(_("Email already exists"))
#     if db.query(User).filter(User.username == username, User.id != user.id).first():
#         errors.append(_("Username already exists"))
#     print(errors)
#     if errors:
#         return JSONResponse({"success": False, "errors": errors}, status_code=400)

#     # Prepare updated data
#     updated_data = {
#         "username": username,
#         "first_name": first_name,
#         "last_name": last_name,
#         "email": email,
#     }

#     # Only hash and update password if it is provided
#     # if password:
#     #     updated_data["password"] = hash_password(password)

#     # Update the user in the database
#     update_user(db, user.id, updated_data)

#     # Respond with success
#     return JSONResponse({"success": True, "message": _("Profile updated successfully")}, status_code=200)

# @app.post("/{lang}/change_password", response_class=JSONResponse)
# async def change_password(
#     request: Request,
#     lang: str = "he",
#     current_password: str = Form(...),
#     new_password: str = Form(...),
#     confirm_password: str = Form(...),
#     db: Session = Depends(get_db),
# ):
#     """
#     Change the user's password after verifying the current password.
#     """
#     _ = request.state._  # Translation function
#     user = db.query(User).filter(User.id == request.state.user.id).first() 

#     if not user:
#         raise HTTPException(status_code=401, detail=_("Not authenticated"))

#     # Validate current password
#     if not pwd_context.verify(current_password, user.password):
#         return JSONResponse({"success": False, "errors": [_("Current password is incorrect")]}, status_code=400)

#     # Validate new password confirmation
#     if new_password != confirm_password:
#         return JSONResponse({"success": False, "errors": [_("New passwords do not match")]}, status_code=400)

#     # Validate password strength (optional, implement your own logic)
#     if len(new_password) < 8:
#         return JSONResponse({"success": False, "errors": [_("Password must be at least 8 characters long")]}, status_code=400)

#     # Hash the new password
#     hashed_password = pwd_context.hash(new_password)

#     # Update the user's password in the database
#     user.password = hashed_password
#     db.commit()
#     db.refresh(user)

    # Optional: Log the user out or invalidate old tokens
    # This depends on your authentication/token management strategy

    # return JSONResponse({"success": True, "message": _("Password changed successfully")}, status_code=200)
# @app.get("/users/", response_model=list[schemas.UserBase])
# def list_users(db: Session = Depends(get_db)):
#     print("users")
#     u= crud.get_all_users(db)
    
#     print(u)
#     return u


# # Medicine endpoints
# @app.post("/{lang}/medicine/", response_model=schemas.MedicineTypeBase)
# def create_medicine(medicine: schemas.MedicineTypeBase, db: Session = Depends(get_db)):
#     return crud.create_medicine_type(db=db, medicine=medicine)


# @app.get("/{lang}/medicines", response_model=list[schemas.MedicineTypeBase])
# def list_medicines(db: Session = Depends(get_db)):
#     print("medicines")
#     m= crud.get_all_medicine_types(db)
#     print(m)
#     return m
# Include routers
authentication.templates = templates  # Pass templates to the router
app.include_router(authentication.router, tags=["Authentication"])
management.templates=templates
app.include_router(management.router , prefix="/{lang}/management", tags=["management"], dependencies=[Depends(require_role_router(["Admin"]))])
# Include the input_medicine router
input_medicine.templates = templates
app.include_router(input_medicine.router, prefix="/{lang}/input_medicine", tags=["input_medicine"], dependencies=[Depends(require_role_router(["Admin","Pharmacist"]))])
dispense_medicine.templates = templates
app.include_router(dispense_medicine.router, prefix="/{lang}/dispense_medicine", tags=["dispense_medicine"], dependencies=[Depends(require_role_router(["Admin", "Technician"]))])
medicines.templates=templates
app.include_router(medicines.router, prefix="/{lang}/management/medicines", tags=["Medicines"], dependencies=[Depends(require_role_router(["Admin"]))])
users.templates=templates
app.include_router(users.router, prefix="/{lang}/management/users", tags=["Users"], dependencies=[Depends(require_role_router(["Admin"]))])
patients.templates=templates
app.include_router(patients.router, prefix="/{lang}/management/patients", tags=["Patients"], dependencies=[Depends(require_role_router(["Admin"]))])
prescriptions.templates=templates
app.include_router(prescriptions.router, prefix="/{lang}/management/prescriptions", tags=["Prescriptions"])
manage_medicine_supply.templates=templates
app.include_router(manage_medicine_supply.router, prefix="/{lang}/supply", tags=["Supply"])

server_process = None
chrome_process = None

def cleanup():
    """Clean up resources on exit."""
    print("clean up")
    global server_process, chrome_process
    if server_process and server_process.is_alive():
        server_process.terminate()
        print("Server process terminated.")
    if chrome_process:
        chrome_process.terminate()
        print("Chrome process terminated.")

# Register cleanup
# atexit.register(cleanup)

# def monitor_chrome(chrome_proc):
#     """Monitor Chrome process and trigger cleanup on termination."""
#     while chrome_proc.poll() is None:  # While Chrome is running
#         time.sleep(1)  # Check every second
#     print("Chrome closed. Running cleanup...")
#     cleanup()

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()

    # from multiprocessing import Process

    def open_chrome():
        """Open Chrome/Chromium or fallback to default browser (cross-platform)."""
        url = "http://127.0.0.1:8000"  # Your server URL
        system_os = platform.system()  # Detect the operating system

        # Paths to check for Chrome/Chromium
        chrome_paths = []

        if system_os == "Windows":
            # Windows-specific paths
            chrome_paths = [
                which("chrome"),
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
            ]
        elif system_os == "Linux":
            # Linux-specific paths (Raspberry Pi/Ubuntu)
            chrome_paths = [
                which("chromium-browser"),  # Raspberry Pi
                which("chromium"),
                which("google-chrome"),  # Standard Chrome on Linux
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "/usr/bin/google-chrome"
            ]
        else:
            print(f"Unsupported OS: {system_os}")
            return None

        # Find the first valid Chrome/Chromium path
        chrome_path = next((path for path in chrome_paths if path and os.path.exists(path)), None)

        if chrome_path:
            print(f"Found Chrome/Chromium at: {chrome_path}")
            # Open in app mode or fullscreen mode
            return subprocess.Popen([
                chrome_path,
                "--app=http://127.0.0.1:8000",  # Opens in app mode
                "--start-fullscreen"           # Fullscreen mode
            ])
        else:
            # Fallback to the default browser if Chrome/Chromium is not found
            print("Chrome/Chromium not found. Opening in default browser...")
            webbrowser.open(url)
            return None
        
    # Start the FastAPI server in a separate process
    server_process = Process(target=start_server)
    server_process.start()

    # Wait for the server to initialize
    time.sleep(2)

    # Launch Chrome pointing to the FastAPI server
    chrome_process = open_chrome()
    print(chrome_process)
    
    input("Server started. Press Enter to terminate...")
    # Keep the server running
    server_process.join()
    # if chrome_process:
    #     chrome_monitor_thread = threading.Thread(target=monitor_chrome, args=(chrome_process,))
    #     chrome_monitor_thread.daemon = True  # Ensure thread exits with the program
    #     chrome_monitor_thread.start()
    
    