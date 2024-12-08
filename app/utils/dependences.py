
from fastapi import Depends, HTTPException
from app.utils.auth_utils import get_current_user


def require_role_router(allowed_roles: list):
    def dependency(user=Depends(get_current_user)):
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        if user.role.name not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied: Insufficient role")
        return user
    return dependency