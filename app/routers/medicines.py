from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from app.crud import create_medicine_type, get_all_medicine_types, delete_medicine_type, update_medicine_type, get_medicine_type_by_id
from app.crud.medicine_size_codes import get_all_medicine_size_codes
from app.schemas.medicine import MedicineTypeCreate, MedicineTypeResponse
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def manage_medicine_types(request: Request, lang: str, db: Session = Depends(get_db)):
    """
    Display the medicine types management page.
    """
    _ = request.state._
    medicine_types = get_all_medicine_types(db)
    size_codes = get_all_medicine_size_codes(db)
    return templates.TemplateResponse(
        "manage_medicine_types.html", {"request": request, "medicine_types": medicine_types, "sizes": size_codes, "_": _, "lang": lang}
    )


@router.get("/{medicine_id}", response_model=MedicineTypeResponse)
async def get_medicine_details(medicine_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific medicine type by its ID.
    """
    medicine = get_medicine_type_by_id(db, medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine type not found")
    return medicine


@router.post("/save", response_class=RedirectResponse)
async def save_medicine_type(
    request: Request,
    lang: str,
    medicine_id: Optional[int] = Form(None),  # Optional field for medicine ID
    name: str = Form(...),
    barcode: str = Form(...),
    description: str = Form(...),
    size_id: int = Form(...),
    x: int = Form(...),
    y: int = Form(...),
    db: Session = Depends(get_db),
):
    _ = request.state._
    if medicine_id:  # If medicine_id is provided, update the medicine type
        medicine = get_medicine_type_by_id(db, medicine_id)
        if not medicine:
            raise HTTPException(status_code=404, detail=_("Medicine type not found"))

        updated_data = {
            "name": name,
            "barcode": barcode,
            "description": description,
            "size_id": size_id,
            "x": x,
            "y": y,
        }
        update_medicine_type(db, medicine_id, updated_data)
    else:  # If medicine_id is not provided, add a new medicine type
        new_medicine_type = MedicineTypeCreate(
            name=name, barcode=barcode, description=description, size_id=size_id, x=x, y=y
        )
        create_medicine_type(db, new_medicine_type)

    return RedirectResponse(url=f"/{lang}/management/medicines", status_code=303)


@router.delete("/{medicine_id}", status_code=204)
def delete_medicine_type_route(lang: str, medicine_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific medicine type by its ID.
    """
    medicine = get_medicine_type_by_id(db, medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine type not found")

    delete_medicine_type(db, medicine_id)
    return {"detail": f"Medicine type {medicine_id} deleted successfully"}


@router.get("/list", response_model=List[MedicineTypeResponse])
async def get_medicines(db: Session = Depends(get_db)):
    """
    Return a list of all medicine types in JSON format.
    """
    medicines = get_all_medicine_types(db)
    return medicines
