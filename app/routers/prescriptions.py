from app.crud.prescription import delete_prescription_items
from app.models import MedicineType, PrescriptionItem
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.prescription import PrescriptionCreate, PrescriptionResponse
from app.schemas.prescription_item import PrescriptionItemCreate
from app.crud import (
    create_prescription,
    get_all_prescriptions,
    get_all_patients,
    get_all_users,
    add_prescription_items,
    get_prescription_by_id,
    update_prescription,
    delete_prescription
)
from app.crud.medicine import get_all_medicine_types
from app.schemas.medicine import MedicineTypeResponse
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def manage_prescriptions(request: Request, lang: str, db: Session = Depends(get_db)):
    """
    Display the prescription management page with enriched prescription data.
    """
    _ = request.state._
    
    # Fetch core data
    prescriptions = get_all_prescriptions(db)
    patients = get_all_patients(db)
    users = get_all_users(db)
    medicines = get_all_medicine_types(db)

    # Create mapping for patients and users
    patients_map = {patient.id: f"{patient.first_name} {patient.last_name}" for patient in patients}
    users_map = {user.id: f"{user.first_name} {user.last_name}" for user in users}

    # Enrich prescriptions with medicines
    enriched_prescriptions = []
    for prescription in prescriptions:
        # Fetch prescription items for the prescription
        items = (
            db.query(PrescriptionItem)
            .filter(PrescriptionItem.prescription_id == prescription.id)
            .all()
        )

        # Collect medicine details and quantities
        active_medicines = []
        for item in items:
            medicine_type = (
                db.query(MedicineType)
                .filter(MedicineType.id == item.medicine_id)
                .first()
            )
            if medicine_type:
                active_medicines.append({
                    "name": medicine_type.name,
                    "quantity": item.quantity
                })

        # Add enriched prescription data
        enriched_prescriptions.append({
            "id": prescription.id,
            "patient_id": prescription.patient_id,
            "prescribed_by": prescription.prescribed_by,
            "medicines": active_medicines
        })

    return templates.TemplateResponse(
        "manage_prescriptions.html",
        {
            "request": request,
            "prescriptions": enriched_prescriptions,
            "patients": patients,
            "patients_map": patients_map,
            "users_map": users_map,
            "users": users,
            "medicines": medicines,
            "_": _,
            "lang": lang,
        },
    )

@router.post("/save", response_class=RedirectResponse)
async def save_prescription(
    request: Request,
    lang: str,
    prescription_id: Optional[int] = Form(None),
    patient_id: int = Form(...),
    prescribed_by: int = Form(...),
    medicine_ids: List[int] = Form(...),
    quantities: List[int] = Form(...),
    db: Session = Depends(get_db),
):
    """
    Save a new or updated prescription.
    """
    _ = request.state._
    if prescription_id:  # Update an existing prescription
        prescription = get_prescription_by_id(db, prescription_id)
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")

        # Update the prescription details
        updated_data = {
            "patient_id": patient_id,
            "prescribed_by": prescribed_by,
        }
        update_prescription(db, prescription_id, updated_data)

        # Update prescription items (for simplicity, delete and re-add)
        delete_prescription_items(db, prescription_id)
        prescription_items = [
            PrescriptionItemCreate(prescription_id=prescription_id, medicine_id=med_id, quantity=qty)
            for med_id, qty in zip(medicine_ids, quantities)
        ]
        add_prescription_items(db, prescription_items)

    else:  # Create a new prescription
        new_prescription = PrescriptionCreate(patient_id=patient_id, prescribed_by=prescribed_by)
        prescription = create_prescription(db, new_prescription)

        prescription_items = [
            PrescriptionItemCreate(prescription_id=prescription.id, medicine_id=med_id, quantity=qty)
            for med_id, qty in zip(medicine_ids, quantities)
        ]
        add_prescription_items(db, prescription_items)

    return RedirectResponse(url=f"/{lang}/management/prescriptions", status_code=303)


@router.delete("/{prescription_id}", status_code=204)
def delete_prescription_endpoint(prescription_id: int, db: Session = Depends(get_db)):
    """
    Delete a prescription by ID.
    """
    # prescription = get_prescription_by_id(db, prescription_id)
    # if not prescription:
    #     raise HTTPException(status_code=404, detail="Prescription not found")
    delete_prescription(db, prescription_id)
    return {"detail": f"Prescription {prescription_id} deleted successfully"}


@router.get("/medicines_list", response_model=List[MedicineTypeResponse])
async def get_medicines(db: Session = Depends(get_db)):
    """
    Get a list of all medicines.
    """
    medicines = get_all_medicine_types(db)
    print(medicines)
    return [MedicineTypeResponse.from_orm(med) for med in medicines]

@router.get("/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription_details(prescription_id: int, db: Session = Depends(get_db)):
    prescription = get_prescription_by_id(db, prescription_id)
    print(prescription)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Serialize the prescription using the Pydantic model
    return prescription#PrescriptionResponse.from_orm(prescription)
