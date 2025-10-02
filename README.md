# Fuel Alert 🚗⛽

Ein Docker-fähiger Service, der die aktuellen **Luxemburgischen Spritpreise** überwacht  
und dich per **E-Mail** benachrichtigt, sobald sich etwas ändert.  
Zusätzlich gibt es ein **Web-Dashboard** mit Admin-Login, Statistiken und Preis-Historie.  

---

## ✨ Features
- FastAPI Web-UI mit Login (Admin + Userverwaltung)
- Dashboard: aktuelle Preise, letzte Änderung, Min/Max-Werte in Zeiträumen (Monat, Halbjahr, Jahr)
- Preisüberwachung mit speicherbarer Historie
- Benachrichtigung per E-Mail (SMTP)
- Docker-Compose für einfache Installation
- **Keine LDAP-Integration** → komplett lokal verwaltet

---

## 🛠 Installation

### 1. Repository klonen oder ZIP entpacken
```bash
git clone https://github.com/<DEIN-USER>/fuel-alert.git
cd fuel-alert

