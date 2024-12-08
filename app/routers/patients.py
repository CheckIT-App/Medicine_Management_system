from typing import Optional
from app.models import Patient
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.schemas.patient import PatientCreate, PatientResponse
from app.crud.gender_codes import get_all_gender_codes
from app.crud import create_patient, get_all_patients, get_patient_by_id, update_patient, delete_patient
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def manage_patients(request: Request, lang: str, db: Session = Depends(get_db)):
    """
    Render the patient management page.
    """
    _ = request.state._
    patients = get_all_patients(db)
    genders = get_all_gender_codes(db)
    return templates.TemplateResponse(
        "manage_patients.html", {"request": request, "patients": patients, "genders": genders, "_": _, "lang": lang}
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient_details(patient_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific patient by their ID.
    """
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/save", response_class=RedirectResponse)
async def save_patient(
    request: Request,
    lang: str,
    patient_id: Optional[int] = Form(None),  # Optional field for patient ID
    first_name: str = Form(...),
    last_name: str = Form(...),
    identity_number: str = Form(...),
    age: int = Form(...),
    gender_id: int = Form(...),
    contact_info: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Add a new patient or update an existing patient.
    """
    _ = request.state._

    if patient_id:  # If patient_id is provided, update the patient
        patient = get_patient_by_id(db, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=_("Patient not found"))

        updated_data = {
            "first_name": first_name,
            "last_name": last_name,
            "identity_number": identity_number,
            "age": age,
            "gender_id": gender_id,
            "contact_info": contact_info,
        }
        update_patient(db, patient_id, updated_data)
    else:  # Add a new patient
        if db.query(Patient).filter(Patient.identity_number == identity_number).first():
            raise HTTPException(status_code=400, detail=_("Identity number already exists"))
        new_patient = PatientCreate(
            first_name=first_name,
            last_name=last_name,
            identity_number=identity_number,
            age=age,
            gender_id=gender_id,
            contact_info=contact_info,
        )
        create_patient(db, new_patient)

    return RedirectResponse(url=f"/{lang}/management/patients", status_code=303)


@router.delete("/{patient_id}", status_code=204)
async def delete_patient_handler(patient_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific patient by their ID.
    """
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    delete_patient(db, patient_id)
    return {"detail": f"Patient {patient_id} deleted successfully"}
