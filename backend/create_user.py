import sys
import os

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
import app.db.base  # Import all models to ensure they are registered
from app.models.user import User
from app.core.security import get_password_hash

def create_user(email, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.hashed_password = get_password_hash(password)
            user.is_active = True
            user.subscription_tier = "PRO"
            db.commit()
            print(f"User {email} updated successfully (Tier: PRO).")
            return

        hashed_password = get_password_hash(password)
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            subscription_tier="PRO",
            full_name="Admin"
        )
        db.add(new_user)
        db.commit()
        print(f"User {email} created successfully (Tier: PRO).")
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    email = "abdullaevjonibek6118@gmail.com"
    password = "Joni(6118"
    create_user(email, password)
