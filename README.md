# Fuel Alert V1.1 🚀

Ein FastAPI-basiertes Tool für luxemburgische Spritpreise mit E-Mail-Benachrichtigung,
LDAP-Login (Synology kompatibel) und Admin-Dashboard.

## Features
- Regelmäßiger Abruf luxemburgischer Spritpreise (GraphQL API)
- Speicherung in SQLite mit History
- Benutzerverwaltung mit Admin-UI
- LDAP-Login (Synology Directory Server)
- E-Mail-Benachrichtigungen bei Preisänderungen
- Dashboard mit min/max Werten über 1M / 6M / 1Y
- **NEU V1.1:** GitHub Actions Workflow für automatisches Docker-Build & Push zu GHCR

## Nutzung
```bash
git clone https://github.com/<username>/fuel-alert.git
cd fuel-alert
cp .env.example .env
nano .env   # Werte eintragen
docker-compose up -d
```

## Hinweise
- SQLite DB liegt in `data/` und wird durch Synology Volume persistiert.
- `.env` enthält Secrets → wird durch `.gitignore` geschützt (nicht committen!).
- Docker-Image wird automatisch in GHCR gebaut: `ghcr.io/<username>/fuel-alert:latest`
