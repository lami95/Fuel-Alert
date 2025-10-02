# Fuel Alert V1.4 mit UI + LDAP-Suche (Docker & GitHub Actions)

## Features
- Admin-Login (admin/adminpassword)
- Login via Synology LDAP (Benutzername reicht, DN wird gesucht)
- Dashboard mit Spritpreisen
- Admin-Seite mit Benutzerübersicht

## ENV Variablen (docker-compose.yml)
- LDAP_SERVER=ldap://192.168.1.100:389
- LDAP_BASE_DN=dc=ldap,dc=synology,dc=local
- LDAP_SEARCH_FILTER=(uid={username})

## Starten
```bash
docker-compose up -d
```

## GitHub Actions (Automatischer Build)
Jeder Push auf `main` baut und pusht Image nach GHCR:
`ghcr.io/<github-user>/fuel-alert:latest`
