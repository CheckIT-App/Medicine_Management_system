import asyncio
from fastapi import HTTPException, Request
from functools import wraps

def require_role(allowed_roles: list):
    """
    Decorator to enforce role-based access.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(request:Request, *args, **kwargs):
            # Get user from request state (set by middleware)
            user = getattr(request.state, "user", None)
            if not user:
                raise HTTPException(status_code=403, detail="Access denied: No user provided")
            if user.role.name not in allowed_roles:
                raise HTTPException(status_code=403, detail="Access denied: Insufficient role")
            # Await the wrapped function if it's a coroutine
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            # Call synchronously if not a coroutine
            return func(*args, **kwargs)
        return async_wrapper
    return decorator
