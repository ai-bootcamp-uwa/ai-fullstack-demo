from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import settings

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token data model
class TokenData(BaseModel):
    username: str = None

# Simple user database (in production, use a real database)
USERS_DB = {
    "admin": {"username": "admin", "password": "$2b$12$4Ell9VbcZ6/cjV7v50CTYuOL1VCjngC.mMNspaLNUd.TgLa2.XPze", "role": "admin"},  # admin123
    "user": {"username": "user", "password": "$2b$12$4Ell9VbcZ6/cjV7v50CTYuOL1VCjngC.mMNspaLNUd.TgLa2.XPze", "role": "user"},    # user123 (same hash for simplicity)
    "demo": {"username": "demo", "password": "$2b$12$4Ell9VbcZ6/cjV7v50CTYuOL1VCjngC.mMNspaLNUd.TgLa2.XPze", "role": "user"},    # demo123 (same hash for simplicity)
}

def authenticate_user(username: str, password: str):
    """Authenticate user credentials."""
    user = USERS_DB.get(username)
    if not user or not pwd_context.verify(password, user["password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user info"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = USERS_DB.get(token_data.username)
    if user is None:
        raise credentials_exception
    
    return {"username": user["username"], "role": user["role"]}

def get_current_user(current_user: dict = Depends(verify_token)):
    """Get current authenticated user"""
    return current_user

def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile information"""
    return current_user 