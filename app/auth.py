from passlib.hash import bcrypt
from ldap3 import Server, Connection, ALL, SUBTREE
import os

LDAP_URI = os.getenv('LDAP_URI')
LDAP_BASE_DN = os.getenv('LDAP_BASE_DN')
LDAP_BIND_DN = os.getenv('LDAP_BIND_DN')
LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PASSWORD')
LDAP_USER_DN_FORMAT = os.getenv('LDAP_USER_DN_FORMAT', 'uid={username},' + (LDAP_BASE_DN or ''))

from .db import SessionLocal
from .models import User

def verify_local_password(user: User, password: str) -> bool:
    if not user or not user.password_hash:
        return False
    return bcrypt.verify(password, user.password_hash)

def ldap_auth(username: str, password: str) -> bool:
    if not LDAP_URI or not LDAP_BASE_DN:
        return False
    server = Server(LDAP_URI, get_info=ALL)
    try:
        if LDAP_BIND_DN and LDAP_BIND_PASSWORD:
            conn = Connection(server, user=LDAP_BIND_DN, password=LDAP_BIND_PASSWORD, auto_bind=True)
            search_filter = f"(uid={username})"
            conn.search(LDAP_BASE_DN, search_filter, SUBTREE, attributes=['dn'])
            if len(conn.entries) == 0:
                return False
            user_dn = conn.entries[0].entry_dn
            conn.unbind()
        else:
            user_dn = LDAP_USER_DN_FORMAT.format(username=username)
        user_conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        user_conn.unbind()
        return True
    except Exception:
        return False

def create_local_admin_if_missing():
    from .db import SessionLocal
    from .models import User
    import os
    session = SessionLocal()
    try:
        admin_user = session.query(User).filter(User.is_admin==True).first()
        if admin_user:
            return
        ADMIN_USER = os.getenv('ADMIN_USER')
        ADMIN_PASS = os.getenv('ADMIN_PASS')
        ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        if ADMIN_USER and ADMIN_PASS:
            hashed = bcrypt.hash(ADMIN_PASS)
            u = User(username=ADMIN_USER, password_hash=hashed, email=ADMIN_EMAIL, is_admin=True)
            session.add(u)
            session.commit()
    finally:
        session.close()
