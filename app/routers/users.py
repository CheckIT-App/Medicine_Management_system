from urllib.parse import urlencode
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from app.crud.user import get_user_by_id, update_user
from app.models import User
from app.schemas.user import UserCreate, UserResponse
from app.utils.auth_utils import hash_password
from app.crud.role_codes import get_all_role_codes
from app.crud import create_user, get_all_users, delete_user,update_user
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def manage_users(request: Request, lang: str, db: Session = Depends(get_db)):
    """
    Display the user management page.
    """
    _ = request.state._
    user = request.state.user
    users = get_all_users(db)
    roles = get_all_role_codes(db)
    return templates.TemplateResponse(
        "manage_users.html", {
            "request": request,
            "users": users,
            "roles": roles,
            "form_data": {},  # No errors or form data by default
            "errors": "",
            "_": _,
            "lang": lang,
            "user":user
        }
    )
    
        


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_details(user_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific user by their ID.
    """
    user = get_user_by_id(db, user_id)
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/save", response_class=HTMLResponse)
async def save_user(
    request: Request,
    lang: str,
    user_id: Optional[int] = Form(None),  # Optional field for user ID
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    identity_number: str = Form(...),
    email: str = Form(...),
    password: Optional[str] = Form(None),  # Optional field for updating
    role_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """
    Save a new or updated user while retaining form data on error.
    """
    _ = request.state._
    user = request.state.user
    errors = []
    form_data = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "identity_number": identity_number,
        "email": email,
        "role_id": role_id,
    }

    if user_id:  # Update an existing user
        user = get_user_by_id(db, user_id)
        if not user:
            errors.append(_("User not found"))

        # Check for duplicates
        if db.query(User).filter(User.email == email, User.id != user_id).first():
            errors.append(_("Email already exists"))
        if db.query(User).filter(User.identity_number == identity_number, User.id != user_id).first():
            errors.append(_("Identity number already exists"))
        if db.query(User).filter(User.username == username, User.id != user_id).first():
            errors.append(_("Username already exists"))

        if errors:
            roles = get_all_role_codes(db)  # Fetch roles for the dropdown
            users = get_all_users(db)
            return templates.TemplateResponse(
                "manage_users.html",
                {
                    "request": request,
                    "errors": errors,
                    "form_data": form_data,
                    "roles": roles,
                    "users": users,
                    "_": _,
                    "lang": lang,
                    "user":user
                },
            )

        # Update the user details
        updated_data = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "identity_number": identity_number,
            "email": email,
            "role_id": role_id,
        }

        # Only hash password if it is provided
        if password:
            updated_data["password"] = hash_password(password)

        update_user(db, user_id, updated_data)
    else:  # Create a new user
        # Check for duplicates
        if db.query(User).filter(User.email == email).first():
            errors.append(_("Email already exists"))
        if db.query(User).filter(User.identity_number == identity_number).first():
            errors.append(_("Identity number already exists"))
        if db.query(User).filter(User.username == username).first():
            errors.append(_("Username already exists"))

        if errors:
            roles = get_all_role_codes(db)  # Fetch roles for the dropdown
            return templates.TemplateResponse(
                "manage_users.html",
                {
                    "request": request,
                    "errors": errors,
                    "form_data": form_data,
                    "roles": roles,
                    "_": _,
                    "lang": lang,
                    "user":user
                },
            )

        hashed_password = hash_password(password) if password else None
        new_user = UserCreate(
            username=username,
            first_name=first_name,
            last_name=last_name,
            identity_number=identity_number,
            email=email,
            password=hashed_password,
            role_id=role_id,
        )
        create_user(db, new_user)

    return RedirectResponse(url=f"/{lang}/management/users", status_code=303)

@router.delete("/{user_id}", status_code=204)
def delete_user(lang: str, user_id: int, db: Session = Depends(get_db)):
    # Fetch the user from the database
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user
    db.delete(user)
    db.commit()
    return {"detail": f"User {user_id} deleted successfully"}