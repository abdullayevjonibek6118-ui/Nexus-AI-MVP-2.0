
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.session import SessionLocal
import app.db.base
from app.models.user import User

def count_users():
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.email == "abdullaevjonibek6118@gmail.com").all()
        print(f"Total users with this email: {len(users)}")
        for u in users:
            print(f"ID: {u.id}, Email: {u.email}, Active: {u.is_active}, Tier: {u.subscription_tier}")
    finally:
        db.close()

if __name__ == "__main__":
    count_users()
