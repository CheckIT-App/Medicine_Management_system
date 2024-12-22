from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.crud import get_medicine_supply

router = APIRouter()
templates = None

@router.get("/", response_class=HTMLResponse)
async def manage_supply(
    request: Request,
    lang: str,
    low_quantity_threshold: int = 10,  # Default threshold
    expiration_date_threshold: str = date.today().isoformat(),  # Default to today's date
    show_critical_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Display the supply management page.
    """
    _ = request.state._
    expiration_date = date.fromisoformat(expiration_date_threshold)
    
    report_data = get_medicine_supply(db, low_quantity_threshold, expiration_date, show_critical_only)
    print(report_data)
    return templates.TemplateResponse(
        "manage_supply.html",
        {
            "request": request,
            "report_data": report_data,
            "_": _,
            "lang": lang,
            "low_quantity_threshold": low_quantity_threshold,
            "expiration_date_threshold": expiration_date,
            "show_critical_only": show_critical_only
        }
    )
