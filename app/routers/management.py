from typing import List
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session,joinedload
from app.crud.gender_codes import get_all_gender_codes
from app.crud.medicine_size_codes import get_all_medicine_size_codes
from app.crud.role_codes import get_all_role_codes
from app.database import get_db
from app.utils.auth_utils import get_current_user, hash_password
from app.models import MedicineType, RoleCode, User, Patient, Prescription
from app.schemas.medicine import MedicineTypeCreate, MedicineTypeResponse
from app.schemas.user import UserCreate
from app.schemas.patient import PatientCreate
from app.schemas.prescription import PrescriptionCreate
from app.schemas.prescription_item import PrescriptionItemCreate
from app.crud import (
    create_medicine_type,
    get_all_medicine_types,
    create_user,
    get_all_users,
    create_patient,
    get_all_patients,
    create_prescription,
    get_all_prescriptions,
)
from app.utils.rbac import require_role

router = APIRouter()
templates = None


@router.get("/",name="management_dashboard", response_class=HTMLResponse)
async def management_dashboard(request: Request, lang: str):
    """
    Render the management dashboard where admins can choose to manage medicines, users, patients, and prescriptions.
    """
    _ = request.state._
    return templates.TemplateResponse("management_dashboard.html", {"request": request, "_": _, "lang": lang})


# # MedicineType Management
# @router.get("/medicine", response_class=HTMLResponse)
# async def manage_medicine_types(request: Request, lang: str, db: Session = Depends(get_db)):
#     _ = request.state._
#     medicine_types = get_all_medicine_types(db)
#     size_codes = get_all_medicine_size_codes(db)
#     return templates.TemplateResponse(
#         "manage_medicine_types.html", {"request": request, "medicine_types": medicine_types, "sizes":size_codes, "_": _, "lang": lang}
#     )


# @router.post("/medicine/add", response_class=RedirectResponse)
# async def add_medicine_type(
#     request: Request,
#     lang: str,
#     name: str = Form(...),
#     barcode: str = Form(...),
#     description: str = Form(...),
#     size_id: int = Form(...),
#     x: int = Form(...),
#     y: int = Form(...),
#     db: Session = Depends(get_db),
# ):
#     _ = request.state._
#     new_medicine_type = MedicineTypeCreate(
#         name=name, barcode=barcode, description=description, size_id=size_id, x=x, y=y
#     )
#     create_medicine_type(db, new_medicine_type)
#     return RedirectResponse(url=f"/{lang}/management/medicine", status_code=303)


# # User Management
# @router.get("/users", response_class=HTMLResponse)
# #@require_role(["Admin"])  # Ensure only "admin" can access
# async def manage_users(
#     request: Request,
#     lang: str,
#     db: Session = Depends(get_db),
#     #user: User = Depends(get_current_user)  # Inject current user
# ):
#     """
#     View for managing users. Accessible only by admin users.
#     """
#     _ = request.state._
    
#     # Debugging to confirm the user and role
#     print(f"Access granted to: {user.name}, Role: {user.role.name}")

#     # Fetch data
#     users = get_all_users(db)
#     roles = get_all_role_codes(db)  # Fetch all role codes

#     # Render the template
#     return templates.TemplateResponse(
#         "manage_users.html",
#         {
#             "request": request,
#             "users": users,
#             "roles": roles,
#             "_": _,
#             "lang": lang
#         }
#     )

# @router.post("/users/add", response_class=RedirectResponse)
# async def add_user(
#     request: Request,
#     lang: str,
#     name: str = Form(...),
#     email: str = Form(...),
#     password: str = Form(...),
#     role_id: int = Form(...),
#     db: Session = Depends(get_db),
# ):
#     _ = request.state._
#     # Check for duplicate email
#     if db.query(User).filter(User.email == email).first():
#         raise HTTPException(status_code=400, detail=_("Email already exists"))

#     # Hash password before saving
#     hashed_password = hash_password(password)
#     new_user = UserCreate(name=name, email=email, password=hashed_password, role_id=role_id)

#     try:
#         create_user(db, new_user)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=_("Error creating user"))

#     return RedirectResponse(url=f"/{lang}/management/users", status_code=303)

# # Patient Management
# @router.get("/patients", response_class=HTMLResponse)
# @require_role(["admin"])
# async def manage_patients(request: Request, lang: str, db: Session = Depends(get_db)):
#     _ = request.state._
#     patients = get_all_patients(db)
#     genders = get_all_gender_codes(db)
#     return templates.TemplateResponse(
#         "manage_patients.html", {"request": request, "patients": patients, "genders":genders, "_": _, "lang": lang}
#     )


# @router.post("/patients/add", response_class=RedirectResponse)
# async def add_patient(
#     request: Request,
#     lang: str,
#     name: str = Form(...),
#     age: int = Form(...),
#     gender_id: int = Form(...),
#     contact_info: str = Form(...),
#     db: Session = Depends(get_db),
# ):
#     _ = request.state._
#     new_patient = PatientCreate(name=name, age=age, gender_id=gender_id, contact_info=contact_info)
#     create_patient(db, new_patient)
#     return RedirectResponse(url=f"/{lang}/management/patients", status_code=303)


# @router.get("/prescriptions", response_class=HTMLResponse)
# async def manage_prescriptions(request: Request, lang: str, db: Session = Depends(get_db)):
#     _ = request.state._
#     prescriptions = get_all_prescriptions(db)
#     patients = get_all_patients(db)
#     users = get_all_users(db)
#     return templates.TemplateResponse(
#         "manage_prescriptions.html", {
#             "request": request,
#             "prescriptions": prescriptions,
#             "_": _,
#             "lang": lang,
#             "patients": patients,
#             "users": users
#         }
#     )


# @router.post("/prescriptions/add", response_class=RedirectResponse)
# async def add_prescription(
#     request: Request,
#     lang: str,
#     patient_id: int = Form(...),
#     prescribed_by: int = Form(...),
#     medicine_ids: List[str] = Form(...),  # Accept as strings initially
#     quantities: List[str] = Form(...),   # Accept as strings initially
#     db: Session = Depends(get_db),
# ):
#     _ = request.state._
#     medicine_ids = [int(med_id) for med_id in medicine_ids]
#     quantities = [int(qty) for qty in quantities]
#     # Create a new prescription
#     new_prescription = PrescriptionCreate(patient_id=patient_id, prescribed_by=prescribed_by)
#     prescription = create_prescription(db, new_prescription)

#     # Add medicines to the prescription
#     prescription_items = [
#         PrescriptionItemCreate(
#             prescription_id=prescription.id,  # Use the ID from the newly created prescription
#             medicine_id=medicine_id,
#             quantity=quantity
#         )
#         for medicine_id, quantity in zip(medicine_ids, quantities)
#     ]
#     add_prescription_items(db, prescription_items)

#     return RedirectResponse(url=f"/{lang}/management/prescriptions", status_code=303)


# @router.get('/medicines_list', response_model=List[MedicineTypeResponse])
# async def get_medicines(db: Session = Depends(get_db)):
#     medicines = get_all_medicine_types(db)
    
#     return medicines