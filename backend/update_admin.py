"""Update admin user subscription to PRO."""
import sys
sys.path.insert(0, '.')

from app.db.session import SessionLocal
from sqlalchemy import text
from datetime import datetime, timedelta

def update_admin_to_pro():
    db = SessionLocal()
    try:
        # Check if admin exists
        result = db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": "abdullaevjonibek6118@gmail.com"})
        admin = result.fetchone()
        
        if not admin:
            print("❌ Admin пользователь не найден!")
            return
        
        # Update subscription to PRO
        expire_date = datetime.utcnow() + timedelta(days=365 * 10)  # 10 years
        
        db.execute(text("""
            UPDATE users 
            SET subscription_tier = :subscription_tier,
                subscription_end_date = :subscription_end_date,
                resumes_used_current_period = 0
            WHERE email = :email
        """), {
            "subscription_tier": "PRO",
            "subscription_end_date": expire_date,
            "email": "abdullaevjonibek6118@gmail.com"
        })
        db.commit()
        
        print("✅ Admin подписка обновлена успешно!")
        print(f"   Email: abdullaevjonibek6118@gmail.com")
        print(f"   Subscription: FREE → PRO (Безлимитный доступ)")
        print(f"   Valid until: {expire_date.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_to_pro()
