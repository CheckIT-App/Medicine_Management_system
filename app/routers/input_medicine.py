# input_medicine.py
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.constants import Steps
from app.hal.hardware_interface import HardwareInterface

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

hardware_interface = HardwareInterface()  # Initialize hardware interface

MEDICINE_DATABASE = {
    "123456789": "Aspirin",
    "987654321": "Paracetamol"
}

@router.get("/", name="input_medicine", response_class=HTMLResponse)
async def input_medicine_home(request: Request, lang: str):
    _ = request.state._
    stage = Steps.SCAN_BARCODE
    current_step = stage
    return templates.TemplateResponse("input_medicine.html", {
        "request": request,
        "stage": stage,
        "_": _,
        "Steps": Steps,
        "lang": lang,
        "current_step": current_step
    })

@router.post("/scan_barcode", response_class=HTMLResponse)
async def scan_barcode(request: Request, lang: str):
    _ = request.state._
    stage = Steps.ENTER_MEDICINE_DETAILS
    barcode = await hardware_interface.scan_barcode()  # Async hardware scanning

    medicine_name = MEDICINE_DATABASE.get(barcode)
    if not medicine_name:
        return templates.TemplateResponse("input_medicine.html", {
            "request": request,
            "stage": Steps.SCAN_BARCODE,
            "_": _,
            "Steps": Steps,
            "lang": lang,
            "current_step": Steps.SCAN_BARCODE,
            "error": _("Invalid barcode. Please try again.")
        })
    return templates.TemplateResponse("input_medicine.html", {
        "request": request,
        "stage": stage,
        "_": _,
        "Steps": Steps,
        "lang": lang,
        "current_step": stage,
        "medicine_name": medicine_name
    })

@router.post("/medicine_details", response_class=HTMLResponse)
async def medicine_details(request: Request, lang: str, balls_number: int = Form(...), expiration_date: str = Form(...), batch_number: str = Form(...)):
    _ = request.state._
    stage = Steps.PLACE_IN_STORAGE
    if not all([balls_number, expiration_date, batch_number]):
        return templates.TemplateResponse("input_medicine.html", {
            "request": request,
            "stage": Steps.ENTER_MEDICINE_DETAILS,
            "_": _,
            "Steps": Steps,
            "lang": lang,
            "current_step": Steps.ENTER_MEDICINE_DETAILS,
            "error": _("All fields are required.")
        })

    await hardware_interface.open_storage()  # Async open storage
    return templates.TemplateResponse("input_medicine.html", {
        "request": request,
        "stage": stage,
        "_": _,
        "Steps": Steps,
        "lang": lang,
        "current_step": stage
    })

@router.post("/finish_placing_medicine", response_class=HTMLResponse)
async def finish_placing_medicine(request: Request, lang: str):
    _ = request.state._
    stage = Steps.RESCAN_FOR_AUTHORIZATION
    return templates.TemplateResponse("input_medicine.html", {
        "request": request,
        "stage": stage,
        "_": _,
        "Steps": Steps,
        "lang": lang,
        "current_step": stage
    })

@router.post("/authorize_barcode", response_class=HTMLResponse)
async def authorize_barcode(request: Request, lang: str, barcode: str = Form(...)):
    _ = request.state._
    stage = Steps.CONFIRMATION
    if barcode not in MEDICINE_DATABASE:
        return templates.TemplateResponse("input_medicine.html", {
            "request": request,
            "stage": Steps.RESCAN_FOR_AUTHORIZATION,
            "_": _,
            "Steps": Steps,
            "lang": lang,
            "current_step": Steps.RESCAN_FOR_AUTHORIZATION,
            "error": _("Authorization failed. Barcode does not match.")
        })

    await hardware_interface.close_storage()  # Async close storage
    return templates.TemplateResponse("input_medicine.html", {
        "request": request,
        "stage": stage,
        "_": _,
        "Steps": Steps,
        "lang": lang,
        "current_step": stage
    })
