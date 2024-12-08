from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.constants import Steps
from app.database import get_db
from app.models import MedicineType, MedicineInstance
from app.schemas.medicine import MedicineInstanceCreate
from app.hal.hardware_interface import HardwareInterface

router = APIRouter()

# Explicitly receive the templates object
templates: Jinja2Templates = None

hardware_interface = HardwareInterface()  # Initialize hardware interface

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
async def scan_barcode(request: Request, lang: str, db: Session = Depends(get_db), barcode:str=Form(...)):
    _ = request.state._
    stage = Steps.ENTER_MEDICINE_DETAILS
    print(barcode)
    # Async hardware scanning
    #barcode = await hardware_interface.scan_barcode()

    # Query the database for medicine type with this barcode
    medicine_type = db.query(MedicineType).filter(MedicineType.barcode == barcode).first()
    if not medicine_type:
        return templates.TemplateResponse("input_medicine.html", {
            "request": request,
            "stage": Steps.SCAN_BARCODE,
            "_": _,
            "Steps": Steps,
            "lang": lang,
            "current_step": Steps.SCAN_BARCODE,
            "error": _("Invalid barcode. Please try again.")
        })
    request.session["barcode"] = barcode
    return templates.TemplateResponse("input_medicine.html", {
        "request": request,
        "stage": stage,
        "_": _,
        "Steps": Steps,
        "lang": lang,
        "current_step": stage,
        "medicine_name": medicine_type.name,
        
    })


@router.post("/medicine_details", response_class=HTMLResponse)
async def medicine_details(
    request: Request,
    lang: str,
    db: Session = Depends(get_db),
    quantity: int = Form(...),
    expiration_date: str = Form(...),
    batch_number: str = Form(...),
    
):
    _ = request.state._
    stage = Steps.PLACE_IN_STORAGE
    
    # Validate form inputs
    if not all([quantity, expiration_date, batch_number]):
        return templates.TemplateResponse("input_medicine.html", {
            "request": request,
            "stage": Steps.ENTER_MEDICINE_DETAILS,
            "_": _,
            "Steps": Steps,
            "lang": lang,
            "current_step": Steps.ENTER_MEDICINE_DETAILS,
            "error": _("All fields are required.")
        })
    
    request.session["quantity"] = quantity
    request.session["expiration_date"] = expiration_date
    request.session["batch_number"] = batch_number
    # Simulate hardware operation
    await hardware_interface.open_storage()

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
async def authorize_barcode(
    request: Request,
    lang: str,
    db: Session = Depends(get_db),
    barcode: str = Form(...)
):
    _ = request.state._
    stage = Steps.CONFIRMATION
    p_barcode = request.session.get("barcode")
    print(p_barcode)
    if not p_barcode:
        raise HTTPException(status_code=404, detail=_("Barcode not found."))
    
    if not barcode==p_barcode:
        return templates.TemplateResponse("input_medicine.html", {
            "request": request,
            "stage": Steps.RESCAN_FOR_AUTHORIZATION,
            "_": _,
            "Steps": Steps,
            "lang": lang,
            "current_step": Steps.RESCAN_FOR_AUTHORIZATION,
            "error": _("Authorization failed. Barcode does not match.")
        })
    
    batch_number = request.session.get("batch_number")
    quantity = request.session.get("quantity")
    expiration_date = request.session.get("expiration_date")
    if not (batch_number and quantity and expiration_date):
        raise HTTPException(status_code=404, detail=_("Medicine details not found."))
    # Check if the barcode exists in the database
    medicine_type = db.query(MedicineType).filter(MedicineType.barcode == p_barcode).first()
    if not medicine_type:
        raise HTTPException(status_code=404, detail=_("Medicine type not found."))

    # Create a new medicine instance
    medicine_instance = MedicineInstance(
        medicine_type_id=medicine_type.id,
        batch_number=batch_number,
        quantity=quantity,
        expiration_date=expiration_date
    )
    db.add(medicine_instance)
    db.commit()
    # Check if the barcode exists in the database
    #medicine_type = db.query(MedicineType).filter(MedicineType.barcode == barcode).first()
    

    # Simulate hardware operation
    await hardware_interface.close_storage()

    return templates.TemplateResponse("input_medicine.html", {
        "request": request,
        "stage": stage,
        "_": _,
        "Steps": Steps,
        "lang": lang,
        "current_step": stage
    })
