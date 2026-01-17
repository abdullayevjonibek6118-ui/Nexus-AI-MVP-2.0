
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.session import SessionLocal
import app.db.base  # This registers all models including AISettings
from app.models.user import User

def check_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "abdullaevjonibek6118@gmail.com").first()
        if user:
            print(f"User found: {user.email}")
            print(f"Is active: {user.is_active}")
            print(f"Subscription: {user.subscription_tier}")
            print(f"Hashed password: {user.hashed_password}")
        else:
            print("User not found")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
