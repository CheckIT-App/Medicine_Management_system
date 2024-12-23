from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
from app.models import User
from app.utils.auth_utils import create_access_token, verify_password
from app.crud.user import update_user

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = None
# Set a default config variable (to be overridden in main.py)
config = {}

@router.get("/{lang}/login", response_class=HTMLResponse)
async def login(request: Request, lang: str = "he"):
    _ = request.state._
    return templates.TemplateResponse("login.html", {
        "request": request,
        "_": _,
        "lang": lang,
    })


@router.get("/{lang}/logout", response_class=HTMLResponse)
async def logout(request: Request, lang: str = "he"):
    _ = request.state._
    response = RedirectResponse(url=f"/{lang}/login")
    response.delete_cookie("access_token", httponly=True)
    return response


@router.post("/{lang}/auth")
def auth(
    lang: str,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    ACCESS_TOKEN_EXPIRE_MINUTES = config["ACCESS_TOKEN_EXPIRE_MINUTES"]
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        # Render the login template with an error message
        _ = request.state._
        return templates.TemplateResponse("login.html", {
            "request": request,
            "_": _,  # Pass the `_` function to the template
            "lang": lang,
            "error": _("Invalid username or password")
        })


    # Generate an access token (if token-based auth is used)
    access_token = create_access_token(data={"sub": user.username},expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Redirect to home or dashboard on success
    response = RedirectResponse(url=f"/{lang}", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@router.post("/{lang}/change_password", response_class=JSONResponse)
async def change_password(
    request: Request,
    lang: str = "he",
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    _ = request.state._
    user = db.query(User).filter(User.id == request.state.user.id).first()

    if not user:
        raise HTTPException(status_code=401, detail=_("Not authenticated"))

    if not pwd_context.verify(current_password, user.password):
        return JSONResponse({"success": False, "errors": [_("Current password is incorrect")]}, status_code=400)

    if new_password != confirm_password:
        return JSONResponse({"success": False, "errors": [_("New passwords do not match")]}, status_code=400)

    user.password = pwd_context.hash(new_password)
    db.commit()
    db.refresh(user)

    return JSONResponse({"success": True, "message": _("Password changed successfully")}, status_code=200)


@router.post("/{lang}/update_profile", response_class=JSONResponse)
async def update_personal_details(
    request: Request,
    lang: str = "he",
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    _ = request.state._
    user = request.state.current_user

    if not user:
        return JSONResponse({"success": False, "errors": [_("Not authenticated")]}, status_code=401)

    errors = []

    if db.query(User).filter(User.email == email, User.id != user.id).first():
        errors.append(_("Email already exists"))
    if db.query(User).filter(User.username == username, User.id != user.id).first():
        errors.append(_("Username already exists"))

    if errors:
        return JSONResponse({"success": False, "errors": errors}, status_code=400)

    update_user(db, user.id, {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
    })

    return JSONResponse({"success": True, "message": _("Profile updated successfully")}, status_code=200)

def get_user_by_username(db: Session, username: str):
    try:
        return db.query(User).filter(User.username == username).first()
    except Exception as e:
        print(f"Error querying user: {e}")
        return None