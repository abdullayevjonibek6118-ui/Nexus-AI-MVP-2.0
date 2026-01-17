import sys
import os
from dotenv import load_dotenv

# Load backend .env explicitly
backend_env = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(backend_env)

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.ai_settings import AISettings
from app.core.security import get_password_hash

def create_user():
    db: Session = SessionLocal()
    
    try:
        # Create or update user
        user = db.query(User).filter(User.email == "jonithe20@gmail.com").first()
        if not user:
            user = User(
                email="jonithe20@gmail.com",
                hashed_password=get_password_hash("Password123!"),
                full_name="Jonibek Test",
                is_active=True
            )
            db.add(user)
            db.commit()
            print("User created.")
        else:
            user.hashed_password = get_password_hash("Password123!")
            user.is_active = True # Ensure user is active
            db.commit()
            print("User jonithe20@gmail.com already exists. Password updated to Password123!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_user()
