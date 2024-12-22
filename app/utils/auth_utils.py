
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.models import User
from app.database import get_db

SECRET_KEY = "your-secret-key"  # Replace with a secure, random key
ALGORITHM = "HS256"  # HMAC SHA256 algorithm for signing the token
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Generate a new JWT access token.
    """
    to_encode = data.copy()
    print(data)
    expire = datetime.now() + ( timedelta(minutes = (expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES)))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """
    Verify the given JWT and extract the payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def get_current_user(request: Request, db: Session = Depends(get_db)):
    # Get the token from the cookie
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")

    # Decode the token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get the user from the database
    user = db.query(User).filter(User.username == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

#passwords
from passlib.context import CryptContext

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)
