from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.user import Token, UserCreate, User as UserSchema

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.email, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserSchema)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        trial_start_date=datetime.utcnow(),
        subscription_tier="FREE",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# HH.ru OAuth Endpoints

@router.get("/hh/authorize")
def authorize_hh(
    current_user: User = Depends(deps.get_current_user),
):
    """Returns the authorization URL for HH.ru with state for security."""
    from app.services.hh import hh_service
    # We use user email or ID as state (should be encrypted/signed in production)
    # For MVP, we'll use a simple string; in real app, use a CSRF token.
    auth_url = hh_service.get_auth_url() + f"&state={current_user.id}"
    return {"url": auth_url}

@router.get("/hh/callback")
def callback_hh(
    code: str,
    state: str = None,
    db: Session = Depends(deps.get_db),
):
    """Handles callback, exchanges code, and saves token to user matching state."""
    from app.services.hh import hh_service
    token_data = hh_service.get_token(code)
    
    if "error" in token_data:
        raise HTTPException(status_code=400, detail=f"HH.ru Error: {token_data['error']}")
    
    if not state:
        raise HTTPException(status_code=400, detail="Missing state parameter")
    
    # Update user in DB
    user = db.query(User).filter(User.id == int(state)).first()
    if not user:
         raise HTTPException(status_code=404, detail="User in state not found")
         
    user.hh_access_token = token_data.get("access_token")
    user.hh_refresh_token = token_data.get("refresh_token")
    db.add(user)
    db.commit()
    
    # Redirect back to frontend settings or dashboard
    from fastapi.responses import RedirectResponse
    # return RedirectResponse(url="http://localhost:3000/settings.html?hh=connected")
    # For now, return JSON so user sees it worked
    return {"status": "success", "message": "HH.ru account connected successfully"}
