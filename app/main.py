<<<<<<< HEAD
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# Sessions aktivieren (für Login-Status)
app.add_middleware(SessionMiddleware, secret_key="supersecret")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Beispiel: einfacher Login (später LDAP oder Admin-Daten aus .env)
    if username == "admin" and password == "adminpassword":
        request.session["user"] = username
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Login fehlgeschlagen"})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_price": "1.62 €",
        "last_change": "vor 2h",
        "min_price": "1.55 €",
        "max_price": "1.75 €",
        "interval": "1 Monat",
        "user": request.session["user"]
    })

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    if request.session.get("user") != "admin":
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "users": ["admin", "user1", "ldapuser"]
    })
=======
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'Fuel Alert API V1.1 läuft!'}
>>>>>>> 59c48fcda017a2e6774269863543fb80aea8dc0c
