from operator import and_
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.constants import DispenseSteps
from app.database import get_db
from app.models import MedicineType, Patient, Prescription, PrescriptionItem, MedicineInstance
from app.hal.hardware_interface import HardwareInterface

router = APIRouter()
# Explicitly receive the templates object
templates: Jinja2Templates = None

hardware_interface = HardwareInterface()

@router.get("/", name="dispense_medicine", response_class=HTMLResponse)
async def dispense_medicine_home(request: Request, lang: str):
    _ = request.state._
    user = request.state.user
    stage = DispenseSteps.SCAN_PATIENT_BARCODE
    return templates.TemplateResponse("dispense_medicine.html", {
        "request": request,
        "stage": stage,
        "Steps": DispenseSteps,
        "_": _,
        "lang": lang,
        "user":user,
        "current_step": stage
    })


@router.post("/scan_patient", response_class=HTMLResponse)
async def scan_patient(request: Request, lang: str, db: Session = Depends(get_db), barcode: str = Form(...)):
    _ = request.state._
    user = request.state.user

    # Fetch the patient by barcode
    patient = db.query(Patient).filter(Patient.contact_info == barcode).first()
    if not patient:
        return templates.TemplateResponse("dispense_medicine.html", {
            "request": request,
            "stage": DispenseSteps.SCAN_PATIENT_BARCODE,
            "_": _,
            "Steps": DispenseSteps,
            "lang": lang,
            "user":user,
            "current_step": DispenseSteps.SCAN_PATIENT_BARCODE,
            "error": _("Invalid patient barcode. Please try again.")
        })

    # Fetch active prescriptions and related medicines for the patient
    prescriptions = (
        db.query(Prescription)
        .filter(Prescription.patient_id == patient.id)
        .all()
    )
    if not prescriptions:
        return templates.TemplateResponse("dispense_medicine.html", {
            "request": request,
            "stage": DispenseSteps.SCAN_PATIENT_BARCODE,
            "_": _,
            "Steps": DispenseSteps,
            "lang": lang,
            "user":user,
            "current_step": DispenseSteps.SCAN_PATIENT_BARCODE,
            "error": _("No active prescriptions found for this patient.")
        })

    # Build a list of medicines from prescription items
    active_medicines = []
    for prescription in prescriptions:
        items = (
            db.query(PrescriptionItem)
            .filter(PrescriptionItem.prescription_id == prescription.id)
            .all()
        )
        for item in items:
            medicine_type = db.query(MedicineType).filter(MedicineType.id == item.medicine_id).first()
            print(medicine_type)
            if medicine_type:
                active_medicines.append({
                    "name": medicine_type.name,
                    "quantity": item.quantity,
                    "id": medicine_type.id
                })
                print(active_medicines)

    stage = DispenseSteps.SELECT_MEDICINES
    return templates.TemplateResponse("dispense_medicine.html", {
        "request": request,
        "stage": stage,
        "_": _,
        "Steps": DispenseSteps,
        "lang": lang,
        "user":user,
        "current_step": stage,
        "active_medicines": active_medicines
    })


@router.post("/dispense_medicines", response_class=HTMLResponse)
async def dispense_medicines(
    request: Request,
    lang: str,
    db: Session = Depends(get_db),
    selected_medicines: list = Form(...)
):
    _ = request.state._
    user = request.state.user
    stage = DispenseSteps.DISPENSING_AND_COMPLETE
    print("selected medicines", selected_medicines)
    # Validate selected medicines
    if not selected_medicines:
        raise HTTPException(status_code=400, detail=_("No medicines selected for dispensing."))

    # Deduct quantities from selected medicines
    for medicine_id in selected_medicines:
        medicine_instance = db.query(MedicineInstance).filter(
            and_(
                MedicineInstance.medicine_type_id == int(medicine_id),
                MedicineInstance.quantity > 0
            )
            ).order_by(MedicineInstance.expiration_date).first()
        if not medicine_instance or medicine_instance.quantity <= 0:
            raise HTTPException(status_code=400, detail=_("Invalid or out-of-stock medicine selected."))

        # Simulate dispensing by decrementing the quantity
        medicine_instance.quantity -= 1
        db.commit()

    # Simulate hardware dispensing
    await hardware_interface.dispense_medicines(selected_medicines)  # Assume this waits for hardware to complete

    # Render the template with the "ready" message after dispensing is done
    return templates.TemplateResponse("dispense_medicine.html", {
        "request": request,
        "stage": stage,
        "_": _,
        "Steps": DispenseSteps,
        "lang": lang,
        "user":user,
        "current_step": stage,
        "dispensing_complete": True  # Flag to show "ready" message in template
    })
