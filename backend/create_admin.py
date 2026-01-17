"""Create admin user for Nexus AI."""
import sys
sys.path.insert(0, '.')

from app.db.session import SessionLocal
from app.db.base import Base  # Import Base first
from sqlalchemy import text
from app.core import security
from datetime import datetime, timedelta

def create_admin_user():
    db = SessionLocal()
    try:
        # Check if admin already exists using raw SQL
        result = db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": "abdullaevjonibek6118@gmail.com"})
        existing_user = result.fetchone()
        
        if existing_user:
            print("⚠️  Admin пользователь уже существует!")
            print(f"   Email: {existing_user[1]}")  # email is column 1
            print(f"   Subscription: {existing_user[6]}")  # subscription_tier
            return
        
        # Hash password
        hashed_pw = security.get_password_hash("Joni(6118")
        now = datetime.utcnow()
        expire_date = now + timedelta(days=365 * 10)  # 10 years
        
        # Insert admin using raw SQL to avoid relationship issues
        db.execute(text("""
            INSERT INTO users (email, hashed_password, full_name, is_active, trial_start_date, subscription_tier, subscription_end_date, resumes_used_current_period)
            VALUES (:email, :hashed_password, :full_name, :is_active, :trial_start_date, :subscription_tier, :subscription_end_date, :resumes_used_current_period)
        """), {
            "email": "abdullaevjonibek6118@gmail.com",
            "hashed_password": hashed_pw,
            "full_name": "Admin",
            "is_active": 1,
            "trial_start_date": now,
            "subscription_tier": "PRO",
            "subscription_end_date": expire_date,
            "resumes_used_current_period": 0
        })
        db.commit()
        
        print("✅ Admin пользователь создан успешно!")
        print(f"   Email: abdullaevjonibek6118@gmail.com")
        print(f"   Password: Joni(6118")
        print(f"   Subscription: PRO (Безлимитный доступ)")
        print(f"   Valid until: {expire_date.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
