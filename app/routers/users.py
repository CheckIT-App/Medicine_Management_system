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
    users = get_all_users(db)
    roles = get_all_role_codes(db)
    return templates.TemplateResponse(
        "manage_users.html", {"request": request, "users": users, "roles": roles, "_": _, "lang": lang}
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


@router.post("/save", response_class=RedirectResponse)
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
    _ = request.state._
    print("enter")
    if user_id:  # If user_id is provided, update the user
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=_("User not found"))

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
    else:  # If user_id is not provided, add a new user
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail=_("Email already exists"))
        if db.query(User).filter(User.identity_number == identity_number).first():
            raise HTTPException(status_code=400, detail=_("Identity number already exists"))

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