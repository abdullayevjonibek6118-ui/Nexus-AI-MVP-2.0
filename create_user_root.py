import sys
import os

# Add backend to python path so 'app' module can be found
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.session import SessionLocal
import app.db.base  # Register models
from app.models.user import User
from app.core.security import get_password_hash

def create_user(email, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.hashed_password = get_password_hash(password)
            user.is_active = True
            db.commit()
            print(f"User {email} already exists. Password updated.")
            return

        hashed_password = get_password_hash(password)
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            full_name="Admin",
            is_active=True
        )
        db.add(new_user)
        db.commit()
        print(f"User {email} created successfully.")
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    email = "abdullaevjonibek6118@gmail.com"
    password = "Joni(6118"
    create_user(email, password)
