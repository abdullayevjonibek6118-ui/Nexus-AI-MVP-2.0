"""Create a test user for testing the application."""
from app.db.session import SessionLocal
from app.models.user import User
from app.core import security
from datetime import datetime

def create_test_user():
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("Test user already exists!")
            return
        
        # Create test user
        user = User(
            email="test@example.com",
            hashed_password=security.get_password_hash("test123"),
            full_name="Test User",
            is_active=True,
            trial_start_date=datetime.utcnow(),
            subscription_tier="FREE",
            resumes_used_current_period=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Test user created successfully!")
        print(f"   Email: {user.email}")
        print(f"   Password: test123")
        print(f"   Subscription: {user.subscription_tier}")
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
