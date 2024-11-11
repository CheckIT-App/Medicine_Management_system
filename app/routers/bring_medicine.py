from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse, name="bring_medicine")
async def bring_medicine(request: Request, lang:str):
    return templates.TemplateResponse("bring_medicine.html", {"request": request})
