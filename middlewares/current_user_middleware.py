from fastapi import Request
from requests import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import get_db
from app.utils.auth_utils import get_current_user
class CurrentUserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            db: Session = next(get_db())
            user = get_current_user(request, db=db)
            print(user)
            request.state.user = user
        except Exception as e:
            print(e)
            request.state.user = None
        finally:
            db.close()  # Ensure the session is closed after use
        response = await call_next(request)
        return response