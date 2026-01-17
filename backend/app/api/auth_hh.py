
import requests
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.core.config import settings
from app.core import security
from app.models.user import User

router = APIRouter()

HH_AUTH_URL = "https://hh.ru/oauth/authorize"
HH_TOKEN_URL = "https://hh.ru/oauth/token"
HH_USER_INFO_URL = "https://api.hh.ru/me"

@router.get("/login")
def login_hh():
    """
    Redirects user to HH.ru for authentication.
    """
    if not settings.HH_CLIENT_ID:
        raise HTTPException(status_code=500, detail="HH Client ID not configured")
        
    return RedirectResponse(
        f"{HH_AUTH_URL}?response_type=code&client_id={settings.HH_CLIENT_ID}&redirect_uri={settings.HH_REDIRECT_URI}"
    )

@router.get("/callback")
def callback_hh(code: str, db: Session = Depends(deps.get_db)):
    """
    Callback from HH.ru. Exchanges code for token and logs in/creates user.
    """
    # 1. Exchange code for token
    token_resp = requests.post(
        HH_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": settings.HH_CLIENT_ID,
            "client_secret": settings.HH_CLIENT_SECRET,
            "redirect_uri": settings.HH_REDIRECT_URI,
            "code": code
        }
    )
    
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get HH token")
        
    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    
    # 2. Get User Info
    user_resp = requests.get(
        HH_USER_INFO_URL,
        headers={"Authorization": f"Bearer {access_token}", "User-Agent": "NexusAi/1.0"}
    )
    
    if user_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get HH user info")
        
    user_info = user_resp.json()
    email = user_info.get("email")
    
    if not email:
        # Fallback if email is hidden or not provided (common in oauth)
        # For MVP we might error out or create a dummy email based on ID
        hh_id = user_info.get("id")
        email = f"hh_{hh_id}@example.com"
        
    # 3. Find or Create User
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Create new user
        # Generate random password since they use OAuth
        import secrets
        random_password = secrets.token_urlsafe(16)
        user = User(
            email=email,
            hashed_password=security.get_password_hash(random_password),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
    # 4. Create JWT Token for our app
    from datetime import timedelta
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_token = security.create_access_token(
        user.email, expires_delta=access_token_expires
    )
    
    # 5. Redirect to frontend with token
    # In production, use a secure way (e.g. cookie or intermediate page). 
    # For MVP, passing in URL fragment is acceptable but insecure.
    frontend_url = "http://localhost:3000/login.html?token=" + jwt_token
    return RedirectResponse(frontend_url)
