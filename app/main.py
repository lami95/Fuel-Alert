import os
import threading
import time
import datetime
import schedule
import requests
import smtplib
from email.mime.text import MIMEText

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from .db import SessionLocal, engine
from .models import Base, User, Alert, Price, PriceHistory
from .auth import create_admin_if_missing, verify_password
from passlib.hash import bcrypt

SECRET_KEY = os.getenv('SECRET_KEY', 'change_me_secret')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '30'))
PRICE_API = os.getenv('PRICE_API', 'https://prix-carburants.services.public.lu/graphql')

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
EMAIL_FROM = os.getenv('EMAIL_FROM')

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
templates = Jinja2Templates(directory='app/templates')

# DB init
Base.metadata.create_all(bind=engine)
create_admin_if_missing()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def fetch_prices_from_api():
    try:
        query = {"query": "{ fuelPrices { fuelType price } }"}
        r = requests.post(PRICE_API, json=query, timeout=20)
        r.raise_for_status()
        data = r.json()
        return {p['fuelType']: float(p['price']) for p in data['data']['fuelPrices']}
    except Exception as e:
        print('fetch error', e)
        return None

def send_mail(to_email, subject, body):
    if not SMTP_SERVER or not EMAIL_FROM:
        print('SMTP not configured')
        return
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email
    try:
        s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        s.starttls()
        if SMTP_USER and SMTP_PASS:
            s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(EMAIL_FROM, [to_email], msg.as_string())
        s.quit()
    except Exception as e:
        print('mail error', e)

def check_prices_job():
    db = SessionLocal()
    try:
        prices = fetch_prices_from_api()
        if not prices:
            return
        now = datetime.datetime.utcnow()
        for fuel, new_price in prices.items():
            p = db.query(Price).filter(Price.fuel==fuel).first()
            if not p:
                p = Price(fuel=fuel, price=new_price, last_changed=now)
                db.add(p)
                db.add(PriceHistory(fuel=fuel, price=new_price, changed_at=now))
                db.commit()
                continue
            if abs((p.price or 0) - new_price) > 1e-6:
                old = p.price
                p.price = new_price
                p.last_changed = now
                db.add(PriceHistory(fuel=fuel, price=new_price, changed_at=now))
                db.commit()
                alerts = db.query(Alert).filter(Alert.fuel==fuel, Alert.active==True).all()
                for a in alerts:
                    user = db.query(User).filter(User.id==a.user_id).first()
                    if user and user.email:
                        send_mail(user.email, f'Preisänderung {fuel}', f'{fuel}: {old} € → {new_price} €')
    finally:
        db.close()

def scheduler_loop():
    print('Start scheduler... (interval {} minutes)'.format(CHECK_INTERVAL))
    check_prices_job()
    schedule.every(CHECK_INTERVAL).minutes.do(check_prices_job)
    while True:
        schedule.run_pending()
        time.sleep(5)

threading.Thread(target=scheduler_loop, daemon=True).start()

# --- Web routes ---
def current_user(request: Request, db: Session = Depends(get_db)):
    username = request.session.get('user')
    if not username:
        return None
    return db.query(User).filter(User.username==username).first()

@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    if request.session.get('user'):
        return RedirectResponse('/dashboard')
    return templates.TemplateResponse('login.html', {'request': request})

@app.post('/login')
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username==username).first()
    if not user:
        return templates.TemplateResponse('login.html', {'request': request, 'error': 'Benutzer nicht gefunden'})
    if not verify_password(user, password):
        return templates.TemplateResponse('login.html', {'request': request, 'error': 'Ungültiges Passwort'})
    request.session['user'] = username
    return RedirectResponse('/dashboard', status_code=302)

@app.get('/logout')
def logout(request: Request):
    request.session.clear()
    return RedirectResponse('/')


@app.get('/dashboard', response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), period: str = '1m'):
    user = current_user(request, db)
    if not user:
        return RedirectResponse('/')
    now = datetime.datetime.utcnow()
    if period == '1m':
        since = now - datetime.timedelta(days=30)
    elif period == '6m':
        since = now - datetime.timedelta(days=182)
    elif period == '1y':
        since = now - datetime.timedelta(days=365)
    else:
        since = now - datetime.timedelta(days=30)

    prices = db.query(Price).all()
    table = []
    for p in prices:
        elapsed = now - p.last_changed if p.last_changed else None
        qmin = db.query(PriceHistory).filter(PriceHistory.fuel==p.fuel, PriceHistory.changed_at >= since).order_by(PriceHistory.price.asc()).first()
        qmax = db.query(PriceHistory).filter(PriceHistory.fuel==p.fuel, PriceHistory.changed_at >= since).order_by(PriceHistory.price.desc()).first()
        table.append({
            'fuel': p.fuel,
            'price': p.price,
            'last_changed': p.last_changed,
            'elapsed': elapsed,
            'min': qmin.price if qmin else None,
            'max': qmax.price if qmax else None
        })
    return templates.TemplateResponse('dashboard.html', {'request': request, 'user': user, 'table': table, 'period': period})

@app.get('/settings', response_class=HTMLResponse)
def settings_get(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse('/')
    fuels = [p.fuel for p in db.query(Price).all()]
    user_alerts = {a.fuel: a.active for a in user.alerts}
    return templates.TemplateResponse('settings.html', {'request': request, 'fuels': fuels, 'user_alerts': user_alerts})

@app.post('/settings')
def settings_post(request: Request, db: Session = Depends(get_db), fuels: list[str] = Form(None)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse('/')
    selected = set(fuels or [])
    existing = {a.fuel: a for a in user.alerts}
    for fuel in selected:
        if fuel in existing:
            existing[fuel].active = True
        else:
            a = Alert(user_id=user.id, fuel=fuel, active=True)
            db.add(a)
    for fuel, a in existing.items():
        if fuel not in selected:
            a.active = False
    db.commit()
    return RedirectResponse('/settings', status_code=302)

@app.get('/admin', response_class=HTMLResponse)
def admin_get(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user or not user.is_admin:
        return RedirectResponse('/')
    users = db.query(User).all()
    return templates.TemplateResponse('admin.html', {'request': request, 'users': users})

@app.post('/admin/create')
def admin_create(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...), is_admin: str = Form(None), db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user or not user.is_admin:
        return RedirectResponse('/')
    if db.query(User).filter(User.username==username).first():
        return RedirectResponse('/admin')
    hashed = bcrypt.hash(password)
    u = User(username=username, password_hash=hashed, email=email, is_admin=bool(is_admin))
    db.add(u)
    db.commit()
    return RedirectResponse('/admin')
