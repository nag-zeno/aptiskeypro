"""
Seed Admin - AptisPro
=====================
Tu dong tao tai khoan admin khi khoi dong ung dung tren Render.
Doc thong tin tu bien moi truong:
  - ADMIN_EMAIL    : email tai khoan admin (mac dinh: admin@aptiskey.com)
  - ADMIN_PASSWORD : mat khau tai khoan admin (mac dinh: Admin@123456)
  - ADMIN_NAME     : ten hien thi (mac dinh: Administrator)

Idempotent: chay nhieu lan van an toan - khong tao lai neu da ton tai.

Cach chay:
    python seed_admin.py
"""

import os
import sys

# Them backend root vao sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine, SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash


def seed_admin():
    """Tao tai khoan admin mac dinh neu chua ton tai."""
    admin_email    = os.environ.get("ADMIN_EMAIL",    "admin@aptiskey.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@123456")
    admin_name     = os.environ.get("ADMIN_NAME",     "Administrator")

    # Tao bang neu chua ton tai
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == admin_email).first()
        if existing:
            print(f"[Admin Seed] OK - Tai khoan admin da ton tai: {admin_email} (bo qua)")
            if existing.role != UserRole.admin:
                existing.role = UserRole.admin
                db.commit()
                print(f"[Admin Seed] Da cap nhat role thanh admin cho {admin_email}")
            return

        hashed_password = get_password_hash(admin_password)
        admin_user = User(
            email=admin_email,
            full_name=admin_name,
            password_hash=hashed_password,
            role=UserRole.admin,
            is_active=True,
            is_email_verified=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("=" * 60)
        print("       AptisPro - TAO ADMIN ACCOUNT THANH CONG")
        print(f"       Email   : {admin_email}")
        print(f"       Ten     : {admin_name}")
        print(f"       Role    : {admin_user.role}")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\n[Admin Seed LOI] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
