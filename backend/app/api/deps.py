
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.user import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # print(f"DEBUG: Validating token: {token[:10]}...")
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        email: str = payload.get("sub")
        # print(f"DEBUG: Token payload email: {email}")
        if email is None:
            # print("DEBUG: Email is None")
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        # print(f"DEBUG: JWT Error: {e}")
        raise credentials_exception
    
    # print("DEBUG: Querying user DB...")
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        # print("DEBUG: User not found in DB")
        raise credentials_exception
    # print(f"DEBUG: User found: {user.email}")
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
