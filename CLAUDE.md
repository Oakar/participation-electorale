# PRISME — Carte interactive d'indicateurs territoriaux en France

## Présentation

Application web affichant des indicateurs territoriaux (élections, démographie, sécurité, économie, culture) sur une carte interactive de la France à trois niveaux : régions, départements, communes.

- **Frontend** Vue 3 + Leaflet (TypeScript)
- **Backend** Spring Boot 3 — API REST en lecture seule (Java 21)
- **ETL** Scripts Python (pandas, geopandas) pour alimenter la base
- **Base de données** PostGIS (PostgreSQL 16 + extension spatiale)

## Structure du monorepo

```
client/     # Application Vue.js (Vite, Tailwind)
server/     # API REST Spring Boot (Maven, Flyway, Hibernate Spatial)
batch/      # Scripts Python ETL (import GeoJSON + CSV → PostGIS)
infra/      # Docker Compose — base de données uniquement
data/       # Données sources : geo/ (GeoJSON) et csv/ (résultats élections)
docs/       # Documentation
```

## Environnement de développement

Le projet tourne dans un **devcontainer** (Python 3.12 + Node 20 + Java 21). Le container de dev est connecté au réseau Docker `prisme-network`.

La base PostGIS tourne dans un container séparé (`prisme-postgis`) démarré via `infra/docker-compose.yml`.

### Accès à la base de données

Le devcontainer et le container PostGIS partagent le réseau `prisme-network`. L'accès à la base se fait avec des **clients locaux** (psql, JDBC, psycopg2) directement via le hostname `prisme-postgis:5432` — **ne pas utiliser `docker exec`** pour interagir avec la base.

```
Host : prisme-postgis
Port : 5432
Base : prisme
User : prisme
Password : prisme
```

### Commandes de démarrage

```bash
# 1. Base de données (depuis l'hôte, Docker CLI absent du devcontainer)
cd infra && docker compose up -d

# 2-4 : depuis le devcontainer
cd server && mvn spring-boot:run    # Flyway applique les migrations au démarrage
cd batch && python import_all.py    # Import des données
cd client && npm run dev             # Frontend
```

## Conventions

- Le backend est **lecture seule** : pas de POST/PUT/DELETE, pas de logique d'écriture
- Flyway gère le schéma (`server/src/main/resources/db/migration/`)
- Les scripts batch sont idempotents (truncate + reimport)
- Les GeoJSON source sont dans `data/geo/`, pas dans `client/public/`
