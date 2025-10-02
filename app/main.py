from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from ldap3 import Server, Connection, ALL, SUBTREE

import os

# LDAP Konfiguration (ENV Variablen)
LDAP_SERVER = os.getenv("LDAP_SERVER", "ldap://192.168.1.100:389")
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN", "dc=ldap,dc=synology,dc=local")
LDAP_SEARCH_FILTER = os.getenv("LDAP_SEARCH_FILTER", "(uid={username})")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecret")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Admin-Bypass
    if username == "admin" and password == "adminpassword":
        request.session["user"] = username
        return RedirectResponse("/dashboard", status_code=302)

    # LDAP Login mit Suche
    try:
        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(server, auto_bind=True)
        search_filter = LDAP_SEARCH_FILTER.format(username=username)
        conn.search(search_base=LDAP_BASE_DN, search_filter=search_filter, search_scope=SUBTREE, attributes=["dn"])
        if conn.entries:
            user_dn = conn.entries[0].entry_dn
            print(f"Gefundener User-DN: {user_dn}")
            # Mit gefundenem DN und Passwort binden
            user_conn = Connection(server, user=user_dn, password=password, auto_bind=True)
            if user_conn.bind():
                request.session["user"] = username
                return RedirectResponse("/dashboard", status_code=302)
    except Exception as e:
        print("LDAP Login failed:", e)

    return templates.TemplateResponse("login.html", {"request": request, "error": "LDAP Login fehlgeschlagen"})

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
        "users": ["admin", "ldapuser1", "ldapuser2"]
    })
