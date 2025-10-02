# Changelog

Alle signifikanten Änderungen am Fuel Alert Projekt werden hier dokumentiert.

## [v1.1] - YYYY-MM-DD
### Added
- GitHub Actions Workflow zum automatischen Docker-Build & Push zu GHCR
- Docker-Compose nutzt nun direkt `ghcr.io/<username>/fuel-alert:latest`
- README.md aktualisiert für GHCR Hinweise

### Fixed
- Minimal-App und Ordnerstruktur angepasst

## [v1.0] - YYYY-MM-DD
### Added
- Grundfunktion: Abruf luxemburgischer Spritpreise
- E-Mail-Benachrichtigung bei Preisänderung
- LDAP-Login für Synology
- Admin-Dashboard
- Persistente SQLite Datenbank
