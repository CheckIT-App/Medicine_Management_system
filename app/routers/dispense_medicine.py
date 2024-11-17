# dispense_medicine.py
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.constants import DispenseSteps
from app.hal.hardware_interface import HardwareInterface

router = APIRouter()
# Explicitly receive the templates object
templates: Jinja2Templates = None


hardware_interface = HardwareInterface()

@router.get("/", name="dispense_medicine", response_class=HTMLResponse)
async def dispense_medicine_home(request: Request, lang: str):
    _ = request.state._
    stage = DispenseSteps.SCAN_PATIENT_BARCODE
    return templates.TemplateResponse("dispense_medicine.html", {
        "request": request,
        "stage": stage,
        "Steps": DispenseSteps,
        "_": _,
        "lang": lang,
        "current_step": stage
    })

@router.post("/scan_patient", response_class=HTMLResponse)
async def scan_patient(request: Request, lang: str, barcode: str = Form(...)):
    _ = request.state._
    patient_medicines = hardware_interface.get_patient_medicines(barcode)
    if not patient_medicines:
        return templates.TemplateResponse("dispense_medicine.html", {
            "request": request,
            "stage": DispenseSteps.SCAN_PATIENT_BARCODE,
            "_": _,
            "Steps": DispenseSteps,
            "lang": lang,
            "current_step": DispenseSteps.SCAN_PATIENT_BARCODE,
            "error": _("Invalid patient barcode. Please try again.")
        })
    
    stage = DispenseSteps.SELECT_MEDICINES
    return templates.TemplateResponse("dispense_medicine.html", {
        "request": request,
        "stage": stage,
        "_": _,
        "Steps": DispenseSteps,
        "lang": lang,
        "current_step": stage,
        "active_medicines": patient_medicines
    })

@router.post("/dispense_medicines", response_class=HTMLResponse)
async def dispense_medicines(request: Request, lang: str, selected_medicines: list = Form(...)):
    _ = request.state._
    stage = DispenseSteps.DISPENSING_AND_COMPLETE

    # Start dispensing and await hardware completion
    await hardware_interface.dispense_medicines(selected_medicines)  # Assume this waits for hardware to complete

    # Render the template with the "ready" message after dispensing is done
    return templates.TemplateResponse("dispense_medicine.html", {
        "request": request,
        "stage": stage,
        "_": _,
        "Steps": DispenseSteps,
        "lang": lang,
        "current_step": stage,
        "dispensing_complete": True  # Flag to show "ready" message in template
    })