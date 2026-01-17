
import sys
import os
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
import app.db.base
from app.models.user import User

def check_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "abdullaevjonibek6118@gmail.com").first()
        if user:
            print(f"User in backend db: {user.email}")
            print(f"Tier: {user.subscription_tier}")
        else:
            print("User NOT found in backend db")
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
