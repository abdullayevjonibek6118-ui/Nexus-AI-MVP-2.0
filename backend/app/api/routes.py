from fastapi import APIRouter
from app.api import auth, vacancies, candidates, analytics, auth_hh, activities, chat, ai_settings

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(auth_hh.router, prefix="/auth/hh", tags=["auth_hh"])
api_router.include_router(vacancies.router, prefix="/vacancies", tags=["vacancies"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(ai_settings.router, prefix="/ai-settings", tags=["ai-settings"])
