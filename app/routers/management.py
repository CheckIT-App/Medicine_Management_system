from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse, name="management")
async def management(request: Request, lang:str):
    return templates.TemplateResponse("management.html", {"request": request})