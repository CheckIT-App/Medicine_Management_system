from operator import and_
from typing import List
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.constants import DispenseSteps
from app.database import get_db
from app.models import MedicineType, Patient, Prescription, PrescriptionItem, MedicineInstance
from app.utils.dependences import get_hardware
import logging

router = APIRouter()
# Explicitly receive the templates object
templates: Jinja2Templates = None

logger = logging.getLogger("dispense_medicine")
logging.basicConfig(level=logging.INFO)

# Home route for dispensing medicines
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
        "user": user,
        "current_step": stage,
    })

# Scan patient barcode and retrieve active medicines
@router.post("/scan_patient", response_class=HTMLResponse)
async def scan_patient(request: Request, lang: str, db: Session = Depends(get_db), barcode: str = Form(...)):
    _ = request.state._
    user = request.state.user

    try:
        # Fetch the patient by barcode
        patient = db.query(Patient).filter(Patient.contact_info == barcode).first()
        if not patient:
            error_msg = _("Invalid patient barcode. Please try again.")
            logger.warning(f"Scan failed for barcode {barcode}: {error_msg}")
            return templates.TemplateResponse("dispense_medicine.html", {
                "request": request,
                "stage": DispenseSteps.SCAN_PATIENT_BARCODE,
                "_": _,
                "Steps": DispenseSteps,
                "lang": lang,
                "user": user,
                "current_step": DispenseSteps.SCAN_PATIENT_BARCODE,
                "error": error_msg,
            })

        # Fetch active prescriptions for the patient
        prescriptions = db.query(Prescription).filter(Prescription.patient_id == patient.id).all()
        if not prescriptions:
            error_msg = _("No active prescriptions found for this patient.")
            logger.warning(f"No prescriptions for patient {patient.id}")
            return templates.TemplateResponse("dispense_medicine.html", {
                "request": request,
                "stage": DispenseSteps.SCAN_PATIENT_BARCODE,
                "_": _,
                "Steps": DispenseSteps,
                "lang": lang,
                "user": user,
                "current_step": DispenseSteps.SCAN_PATIENT_BARCODE,
                "error": error_msg,
            })

        # Collect medicines from prescriptions
        active_medicines = []
        for prescription in prescriptions:
            items = db.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == prescription.id).all()
            for item in items:
                medicine_type = db.query(MedicineType).filter(MedicineType.id == item.medicine_id).first()
                if medicine_type:
                    active_medicines.append({
                        "name": medicine_type.name,
                        "quantity": item.quantity,
                        "id": medicine_type.id,
                    })
        logger.info(f"Patient {patient.id} has {len(active_medicines)} active medicines.")

        stage = DispenseSteps.SELECT_MEDICINES
        return templates.TemplateResponse("dispense_medicine.html", {
            "request": request,
            "stage": stage,
            "_": _,
            "Steps": DispenseSteps,
            "lang": lang,
            "user": user,
            "current_step": stage,
            "active_medicines": active_medicines,
        })

    except Exception as e:
        logger.error(f"Unexpected error in /scan_patient: {str(e)}")
        raise HTTPException(status_code=500, detail=_("An unexpected error occurred. Please try again later."))

# Dispense selected medicines
@router.post("/dispense_medicines", response_class=HTMLResponse)
async def dispense_medicines(
    request: Request,
    lang: str,
    hardware=Depends(get_hardware),
    db: Session = Depends(get_db),
    selected_medicines: List[int] = Form(...),
    medicine_quantities: List[int] = Form(...),
):
    _ = request.state._
    user = request.state.user
    stage = DispenseSteps.DISPENSING_AND_COMPLETE

    try:
        # Validate input
        if not selected_medicines or not medicine_quantities:
            raise HTTPException(status_code=400, detail=_("No medicines or quantities provided."))

        if len(selected_medicines) != len(medicine_quantities):
            raise HTTPException(status_code=400, detail=_("Mismatch between selected medicines and quantities."))

        # Build list of medicines to dispense
        medicines_to_dispense = []
        for medicine_id, quantity in zip(selected_medicines, medicine_quantities):
            medicine_type = db.query(MedicineType).filter(MedicineType.id == int(medicine_id)).first()
            if not medicine_type:
                logger.error(f"Medicine type not found for ID {medicine_id}")
                raise HTTPException(status_code=404, detail=_("Medicine type not found."))

            if quantity <= 0:
                logger.warning(f"Invalid quantity {quantity} for medicine {medicine_id}")
                raise HTTPException(status_code=400, detail=_("Invalid quantity for medicine: ") + medicine_type.name)

            medicine_instances = db.query(MedicineInstance).filter(
                and_(
                    MedicineInstance.medicine_type_id == int(medicine_id),
                    MedicineInstance.quantity > 0
                )
            ).order_by(MedicineInstance.expiration_date).all()

            total_quantity = sum(instance.quantity for instance in medicine_instances)
            if total_quantity < quantity:
                logger.warning(f"Insufficient stock for medicine {medicine_id}")
                raise HTTPException(
                    status_code=400,
                    detail=_("Insufficient stock for medicine: ") + medicine_type.name
                )

            medicines_to_dispense.append({
                "id": int(medicine_id),
                "name": medicine_type.name,
                "x": medicine_type.x,
                "y": medicine_type.y,
                "amount": quantity,
            })

        # Dispense medicines via hardware
        await hardware.dispense_medicines(medicines_to_dispense)

        logger.info(f"Dispensed {len(medicines_to_dispense)} medicines successfully.")
        return templates.TemplateResponse("dispense_medicine.html", {
            "request": request,
            "stage": stage,
            "_": _,
            "Steps": DispenseSteps,
            "lang": lang,
            "user": user,
            "current_step": stage,
            "dispensing_complete": True,
        })

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in /dispense_medicines: {str(e)}")
        raise HTTPException(status_code=500, detail=_("An unexpected error occurred. Please try again later."))
