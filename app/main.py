from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import time
import gettext
import os

from app.middleware import LanguageMiddleware  # Import the middleware
from app.routers import management, input_medicine, dispense_medicine


app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Load translations based on the selected language
# Function to load the appropriate translation
# def load_translation(lang: str):
#     locale_path = os.path.join(os.path.dirname(__file__), "translations")
#     try:
#         translation = gettext.translation("messages", localedir=locale_path, languages=[lang], fallback=True)
#         translation.install()
#         return translation.gettext
#     except FileNotFoundError:
#         gettext.install("messages", localedir=locale_path)
#         return gettext.gettext

# Mount static files directory

app.mount("/static", StaticFiles(directory="app/static"), name="static")

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
app.include_router(input_medicine.router, prefix="/{lang}/input_medicine", tags=["input_medicine"])
app.include_router(dispense_medicine.router, prefix="/{lang}/dispense_medicine", tags=["dispense_medicine"])