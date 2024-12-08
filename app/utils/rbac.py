import asyncio
from fastapi import HTTPException
from functools import wraps

def require_role(allowed_roles: list):
    """
    Decorator to enforce role-based access.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            user = kwargs.get("user")  # Extract user from kwargs
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
