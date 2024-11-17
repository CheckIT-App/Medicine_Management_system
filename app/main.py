import sys
import os

# Add the directory containing `app` to sys.path
if getattr(sys, 'frozen', False):  # Check if running in PyInstaller bundle
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

# import uvicorn
import subprocess
import time
from multiprocessing import Process, freeze_support
import tempfile
import webbrowser
from shutil import which

from app.middleware import LanguageMiddleware  # Import the middleware
from app.routers import management, input_medicine, dispense_medicine
from app.server import start_server


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


# Add the language middleware
app.add_middleware(LanguageMiddleware)

def get_translator(request: Request):
    return {"_": request.state._}

def move_robot_arm(action):
    print(f"Robot arm performing: {action}")

    time.sleep(1)  # Simulate a delay in action
@app.get("/", response_class=HTMLResponse)
async def redirect_to_default_language():
    return RedirectResponse(url="/he")
@app.get("/{lang}", response_class=HTMLResponse)
async def home(request: Request, lang: str = "he"):
    _ = request.state._
    print(f"Invalid barcode. Please try again.")
    return templates.TemplateResponse("home.html", {
        "request": request,
        "_": _,  # Pass the `_` function to the template
        "lang": lang
    })

@app.get("/move_arm/{action}", response_class=HTMLResponse)
async def move_arm(request: Request, action: str):
    move_robot_arm(action)
    return templates.TemplateResponse("action-result.html", {"request": request, "action": action})

# Include routers
app.include_router(management.router , prefix="/{lang}/management", tags=["management"])
# Include the input_medicine router
input_medicine.templates = templates
app.include_router(input_medicine.router, prefix="/{lang}/input_medicine", tags=["input_medicine"])
dispense_medicine.templates = templates
app.include_router(dispense_medicine.router, prefix="/{lang}/dispense_medicine", tags=["dispense_medicine"])



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
