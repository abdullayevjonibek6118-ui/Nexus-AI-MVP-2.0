
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.session import SessionLocal
import app.db.base
from app.models.user import User
from app.core import security

def test_login(email, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} not found")
            return
        
        is_valid = security.verify_password(password, user.hashed_password)
        print(f"Login test for {email}: {'SUCCESS' if is_valid else 'FAILED'}")
        print(f"User is_active: {user.is_active}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    email = "abdullaevjonibek6118@gmail.com"
    password = "Joni(6118"
    test_login(email, password)
