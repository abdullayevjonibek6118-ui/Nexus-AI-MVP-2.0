from datetime import datetime
from app.models.user import User
from app.core.config import settings

class SubscriptionService:
    @staticmethod
    def get_tier_info(tier: str) -> dict:
        return settings.SUBSCRIPTION_TIERS.get(tier, settings.SUBSCRIPTION_TIERS["FREE"])

    @classmethod
    def get_days_left(cls, user: User) -> int:
        if not user.trial_start_date:
            return 0
        
        delta = datetime.utcnow() - user.trial_start_date
        trial_days = cls.get_tier_info("FREE").get("trial_days", 14)
        days_left = trial_days - delta.days
        return max(0, days_left)

    @classmethod
    def get_subscription_status(cls, user: User) -> dict:
        tier_info = cls.get_tier_info(user.subscription_tier)
        days_left = cls.get_days_left(user)
        
        is_trial = tier_info.get("is_trial", False)
        is_expired = False
        
        if is_trial and days_left <= 0:
            is_expired = True
            
        if user.subscription_end_date and user.subscription_end_date < datetime.utcnow():
            is_expired = True

        return {
            "tier": user.subscription_tier,
            "tier_name": tier_info["name"],
            "limit": tier_info["resume_limit"],
            "used": user.resumes_used_current_period,
            "days_left": days_left,
            "is_trial": is_trial,
            "is_expired": is_expired,
            "can_upload": not is_expired and user.resumes_used_current_period < tier_info["resume_limit"]
        }

    @classmethod
    def can_upload_resume(cls, user: User) -> bool:
        status = cls.get_subscription_status(user)
        return status["can_upload"]

    @classmethod
    def record_resume_usage(cls, user: User):
        user.resumes_used_current_period += 1
        # In a real app, we would also check if we need to reset the period here
        # For MVP, we just increment.

subscription_service = SubscriptionService()
