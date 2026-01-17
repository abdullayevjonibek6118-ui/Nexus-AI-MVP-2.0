import sys
import os
from datetime import datetime, timedelta

# Add parent directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import all models to resolve SQLAlchemy relationships
from app.models.user import User
from app.models.ai_settings import AISettings
from app.services.subscription import subscription_service
from app.core.config import settings

def test_trial_period():
    print("Testing Trial Period...")
    
    # Mock user 1: Just registered
    user1 = User(
        email="test1@example.com",
        trial_start_date=datetime.utcnow(),
        subscription_tier="FREE",
        resumes_used_current_period=0
    )
    
    days_left = subscription_service.get_days_left(user1)
    status = subscription_service.get_subscription_status(user1)
    
    assert days_left == 14
    assert status["can_upload"] == True
    print("✅ New user trial: PASS")

    # Mock user 2: Trial expired
    user2 = User(
        email="test2@example.com",
        trial_start_date=datetime.utcnow() - timedelta(days=15),
        subscription_tier="FREE",
        resumes_used_current_period=0
    )
    
    days_left = subscription_service.get_days_left(user2)
    status = subscription_service.get_subscription_status(user2)
    
    assert days_left == 0
    assert status["can_upload"] == False
    assert status["is_expired"] == True
    print("✅ Expired trial: PASS")

def test_resume_limits():
    print("\nTesting Resume Limits...")
    
    # Mock user 3: 30/30 LIMIT for FREE
    user3 = User(
        email="test3@example.com",
        trial_start_date=datetime.utcnow(),
        subscription_tier="FREE",
        resumes_used_current_period=30
    )
    
    status = subscription_service.get_subscription_status(user3)
    assert status["can_upload"] == False
    print("✅ FREE limit (30/30): PASS")

    # Mock user 4: 99/100 for START
    user4 = User(
        email="test4@example.com",
        trial_start_date=datetime.utcnow(),
        subscription_tier="START",
        resumes_used_current_period=99
    )
    
    status = subscription_service.get_subscription_status(user4)
    assert status["can_upload"] == True
    
    # Increment to 100
    subscription_service.record_resume_usage(user4)
    status = subscription_service.get_subscription_status(user4)
    assert status["can_upload"] == False
    print("✅ START limit (100/100): PASS")

    # Mock user 5: PRO unlimited
    user5 = User(
        email="test5@example.com",
        trial_start_date=datetime.utcnow(),
        subscription_tier="PRO",
        resumes_used_current_period=50000
    )
    
    status = subscription_service.get_subscription_status(user5)
    assert status["can_upload"] == True
    print("✅ PRO unlimited: PASS")

if __name__ == "__main__":
    print("🚀 Running Subscription Tests\n")
    try:
        test_trial_period()
        test_resume_limits()
        print("\n🎉 All subscription tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
