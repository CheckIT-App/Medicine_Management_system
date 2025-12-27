from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.config import get_config
from app.constants import Steps
from app.database import get_db
from app.models import MedicineType, MedicineInstance
from app.utils.dependences import get_hardware
import logging

router = APIRouter()
templates: Jinja2Templates = None

logger = logging.getLogger("input_medicine")
logging.basicConfig(level=logging.INFO)

@router.get("/", name="input_medicine", response_class=HTMLResponse)
async def input_medicine_home(request: Request, lang: str):
    _ = request.state._
    user = request.state.user
    stage = Steps.SCAN_BARCODE
    logger.info("Rendering home page for input medicine.")
    return templates.TemplateResponse("input_medicine.html", {
        "request": request,
        "stage": stage,
        "_": _,
        "Steps": Steps,
        "lang": lang,
        "user": user,
        "current_step": stage,
    })


@router.post("/scan_barcode", response_class=HTMLResponse)
async def scan_barcode(request: Request, lang: str, db: Session = Depends(get_db), barcode: str = Form(...)):
    _ = request.state._
    user = request.state.user
    stage = Steps.ENTER_MEDICINE_DETAILS
    logger.info(f"Scanning barcode: {barcode}")

    try:
        medicine_type = db.query(MedicineType).filter(MedicineType.barcode == barcode).first()
        if not medicine_type:
            error_msg = _("Invalid barcode. Please try again.")
            logger.warning(f"Invalid barcode scanned: {barcode}")
            return templates.TemplateResponse("input_medicine.html", {
                "request": request,
                "stage": Steps.SCAN_BARCODE,
                "_": _,
                "Steps": Steps,
                "lang": lang,
                "user": user,
                "current_step": Steps.SCAN_BARCODE,
                "error": error_msg,
            })

        request.session["barcode"] = barcode
        logger.info(f"Barcode {barcode} associated with medicine {medicine_type.name}.")
        return templates.TemplateResponse("input_medicine.html", {
            "request": request,
            "stage": stage,
            "_": _,
            "Steps": Steps,
            "lang": lang,
            "user": user,
            "current_step": stage,
            "medicine_name": medicine_type.name,
        })
    except Exception as e:
        logger.error(f"Error during barcode scan: {str(e)}")
        raise HTTPException(status_code=500, detail=_("An unexpected error occurred. Please try again later."))


@router.post("/medicine_details", response_class=HTMLResponse)
async def medicine_details(
    request: Request,
    lang: str,
    hardware=Depends(get_hardware),
    db: Session = Depends(get_db),
    quantity: int = Form(...),
    expiration_date: str = Form(...),
    batch_number: str = Form(...),
):
    _ = request.state._
    user = request.state.user
    stage = Steps.PLACE_IN_STORAGE

    try:
        if not all([quantity, expiration_date, batch_number]):
            error_msg = _("All fields are required.")
            logger.warning(f"Missing input fields for medicine details: {request.form()}")
            return templates.TemplateResponse("input_medicine.html", {
                "request": request,
                "stage": Steps.ENTER_MEDICINE_DETAILS,
                "_": _,
                "Steps": Steps,
                "lang": lang,
                "user": user,
                "current_step": Steps.ENTER_MEDICINE_DETAILS,
                "error": error_msg,
            })

        request.session.update({
            "quantity": quantity,
            "expiration_date": expiration_date,
            "batch_number": batch_number,
        })
        logger.info("Opening storage for medicine placement.")
        await hardware.open_storage()

        return templates.TemplateResponse("input_medicine.html", {
            "request": request,
            "stage": stage,
            "_": _,
            "Steps": Steps,
            "lang": lang,
            "user": user,
            "current_step": stage,
        })
    except Exception as e:
        logger.error(f"Error during medicine details submission: {str(e)}")
        raise HTTPException(status_code=500, detail=_("An unexpected error occurred. Please try again later."))


@router.post("/finish_placing_medicine", response_class=HTMLResponse)
async def finish_placing_medicine(request: Request, lang: str, hardware=Depends(get_hardware)):
    _ = request.state._
    user = request.state.user
    stage = Steps.RESCAN_FOR_AUTHORIZATION

    try:
        logger.info("Closing storage after placing medicine.")
        await hardware.close_storage()

        return templates.TemplateResponse("input_medicine.html", {
            "request": request,
            "stage": stage,
            "_": _,
            "Steps": Steps,
            "lang": lang,
            "user": user,
            "current_step": stage,
        })
    except Exception as e:
        logger.error(f"Error during storage close: {str(e)}")
        raise HTTPException(status_code=500, detail=_("An unexpected error occurred. Please try again later."))


@router.post("/authorize_barcode", response_class=HTMLResponse)
async def authorize_barcode(
    request: Request,
    lang: str,
    hardware=Depends(get_hardware),
    db: Session = Depends(get_db),
    barcode: str = Form(...),
):
    _ = request.state._
    user = request.state.user
    stage = Steps.CONFIRMATION

    try:
        p_barcode = request.session.get("barcode")
        if not p_barcode:
            raise HTTPException(status_code=404, detail=_("Barcode not found."))

        if barcode != p_barcode:
            error_msg = _("Authorization failed. Barcode does not match.")
            logger.warning(f"Authorization failed for barcode {barcode}.")
            return templates.TemplateResponse("input_medicine.html", {
                "request": request,
                "stage": Steps.RESCAN_FOR_AUTHORIZATION,
                "_": _,
                "Steps": Steps,
                "lang": lang,
                "user": user,
                "current_step": Steps.RESCAN_FOR_AUTHORIZATION,
                "error": error_msg,
            })

        batch_number = request.session.get("batch_number")
        quantity = request.session.get("quantity")
        expiration_date = request.session.get("expiration_date")
        if not all([batch_number, quantity, expiration_date]):
            raise HTTPException(status_code=404, detail=_("Medicine details not found."))

        medicine_type = db.query(MedicineType).filter(MedicineType.barcode == p_barcode).first()
        if not medicine_type:
            raise HTTPException(status_code=404, detail=_("Medicine type not found."))

        # Create new medicine instance
        medicine_instance = MedicineInstance(
            medicine_type_id=medicine_type.id,
            batch_number=batch_number,
            quantity=quantity,
            expiration_date=expiration_date,
        )

        logger.info(f"Placing medicine {medicine_type.name} at X: {medicine_type.x}, Y: {medicine_type.y}.")
        await hardware.put_medicine(medicine_type.x, medicine_type.y)

        db.add(medicine_instance)
        db.commit()

        logger.info("Medicine placement and authorization successful.")
        return templates.TemplateResponse("input_medicine.html", {
            "request": request,
            "stage": stage,
            "_": _,
            "Steps": Steps,
            "lang": lang,
            "user": user,
            "current_step": stage,
        })

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during medicine authorization: {str(e)}")
        raise HTTPException(status_code=500, detail=_("An unexpected error occurred. Please try again later."))
