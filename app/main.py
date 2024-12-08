import sys
import os

from app.handlers.custom_http_exceptions import create_http_exception_handler
from app.utils.dependences import require_role_router
from fastapi.security import OAuth2PasswordRequestForm

from app.utils.auth_utils import get_current_user, verify_password

# Add the directory containing `app` to sys.path
if getattr(sys, 'frozen', False):  # Check if running in PyInstaller bundle
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI,Depends, HTTPException, Request
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
from app.routers import management, input_medicine, dispense_medicine, medicines, patients, prescriptions, users
from app.server import start_server
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import  schemas, crud
from app.models import MedicineType, User
# Create tables in the database
Base.metadata.create_all(bind=engine)
app = FastAPI()
# Get the absolute path to the templates directory
if getattr(sys, 'frozen', False):  # Check if running in PyInstaller bundle
    BASE_DIR = sys._MEIPASS  # Temporary directory created by PyInstaller
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
# templates_dir = os.path.join(os.path.dirname(__file__), "templates")
# if not os.path.exists(templates_dir):
#     raise RuntimeError(f"Templates directory '{templates_dir}' does not exist")

templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Define the path to the 'static' directory, ensuring it's found no matter where the script is executed from
# static_dir = os.path.join(os.path.dirname(__file__), "static")
STATIC_DIR = os.path.join(BASE_DIR, 'static')
# Check if the directory exists (this is optional but helps for debugging)
# if not os.path.exists(STATIC_DIR):
#     raise RuntimeError(f"Static directory '{STATIC_DIR}' does not exist")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
# Add the language middleware
app.add_middleware(LanguageMiddleware)
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
async def home(request: Request, lang: str = "he",user=Depends(require_role_router(["Pharmacist", "Admin","Technician"]))):
    _ = request.state._
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "_": _,  # Pass the `_` function to the template
        "lang": lang,
        "user":user
    })
@app.get("/{lang}/login", response_class=HTMLResponse)
async def login(request: Request, lang: str = "he"):
    _ = request.state._
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "_": _,  # Pass the `_` function to the template
        "lang": lang
    })
# Utility functions
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()



@app.post("/{lang}/auth")
def auth(
    lang: str,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        # Render the login template with an error message
        _ = request.state._
        return templates.TemplateResponse("login.html", {
            "request": request,
            "_": _,  # Pass the `_` function to the template
            "lang": lang,
            "error": _("Invalid username or password")
        })
    
    # Generate an access token (if token-based auth is used)
    access_token = create_access_token(data={"sub": user.username})

    # Redirect to home or dashboard on success
    response = RedirectResponse(url=f"/{lang}", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


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


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()

    from multiprocessing import Process

    def open_chrome():
        url = "http://127.0.0.1:8000"  # Your server URL

        # Try to find Chrome's executable path
        chrome_path = which("chrome")  # Checks system PATH for Chrome
        if not chrome_path:
            # Check common installation paths if not in PATH
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            ]
            print(possible_paths)
            for path in possible_paths:
                if os.path.exists(path):
                    chrome_path = path
                    print(chrome_path)
                    break

        if chrome_path:
            # Open Chrome in kiosk mode if found
            subprocess.Popen([
                chrome_path,
                "--app=http://127.0.0.1:8000",  # Opens in app mode
                "--start-fullscreen"           # Fullscreen mode
            ])
        else:
            # Fall back to default browser if Chrome is not found
            print("Chrome not found. Opening in default browser...")
            webbrowser.open(url)

    # Start the FastAPI server in a separate process
    server_process = Process(target=start_server)
    server_process.start()

    # Wait for the server to initialize
    time.sleep(5)

    # Launch Chrome pointing to the FastAPI server
    chrome_process = open_chrome()
    input("Server started. Press Enter to terminate...")
    try:
        # Keep the server running
        server_process.join()
    except KeyboardInterrupt:
        # Handle graceful shutdown
        print("Shutting down...")
        server_process.terminate()  # Stop the server process
        chrome_process.terminate()  # Stop Chrome
