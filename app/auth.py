import os
from passlib.hash import bcrypt
from .db import SessionLocal
from .models import User

def create_admin_if_missing():
    ADMIN_USER = os.getenv('ADMIN_USER')
    ADMIN_PASS = os.getenv('ADMIN_PASS')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    if not ADMIN_USER or not ADMIN_PASS:
        return
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.username==ADMIN_USER).first()
        if u:
            return
        hashed = bcrypt.hash(ADMIN_PASS)
        admin = User(username=ADMIN_USER, password_hash=hashed, email=ADMIN_EMAIL, is_admin=True)
        db.add(admin)
        db.commit()
    finally:
        db.close()

def verify_password(user, password):
    if not user or not user.password_hash:
        return False
    return bcrypt.verify(password, user.password_hash)
