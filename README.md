# PRISME — Carte interactive d'indicateurs territoriaux en France

Application web de visualisation d'indicateurs territoriaux (elections, demographie, securite, economie, culture) sur une carte interactive a trois niveaux : regions, departements, communes.

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Frontend | Vue 3, TypeScript, Leaflet, Tailwind |
| Backend | Spring Boot 3.4, Java 21, Hibernate Spatial |
| Base de donnees | PostGIS (PostgreSQL 16) |
| ETL | Python 3.12, pandas, geopandas |
| Migrations | Flyway |
| Build frontend | Vite 8 |

## Structure du monorepo

```
client/     # Frontend Vue.js
server/     # API REST Spring Boot (lecture seule)
batch/      # Scripts Python ETL
infra/      # Docker Compose (PostGIS)
data/       # Donnees sources : geo/ (GeoJSON) et csv/ (resultats elections)
docs/       # Documentation
```

## Demarrage rapide

### Prerequis

- Docker (pour PostGIS)
- Java 21 + Maven
- Node.js 20 + npm
- Python 3.12 + pip

Le projet est configure pour un **devcontainer** (Python + Node + Java). Le container PostGIS tourne separement.

### 1. Base de donnees

```bash
cd infra && docker compose up -d
```

PostGIS demarre sur `prisme-postgis:5432` (ou `localhost:5432` hors devcontainer).

### 2. Backend (cree le schema via Flyway au premier lancement)

```bash
cd server && mvn spring-boot:run
```

L'API demarre sur `http://localhost:8080`.

### 3. Import des donnees

```bash
cd batch
pip install -r requirements.txt
python import_all.py
```

Importe les GeoJSON (regions, departements, communes) puis les donnees electorales (~1.6M lignes).

### 4. Frontend

```bash
cd client
npm install
npm run dev
```

Le frontend demarre sur `http://localhost:3000/prisme/`. Un proxy Vite redirige `/api` vers le backend.

## API REST

### Indicateurs

| Methode | URL | Description |
|---------|-----|-------------|
| GET | `/api/categories` | Liste des categories |
| GET | `/api/categories/{catId}/indicateurs` | Indicateurs d'une categorie |
| GET | `/api/indicateurs/{indId}/regions` | Valeurs agregees par region |
| GET | `/api/indicateurs/{indId}/regions/{regionCode}/departements` | Valeurs par departement |
| GET | `/api/indicateurs/{indId}/departements/{deptCode}/communes` | Valeurs par commune |

### GeoJSON

| Methode | URL | Description |
|---------|-----|-------------|
| GET | `/api/geo/regions` | FeatureCollection regions |
| GET | `/api/geo/departements` | FeatureCollection departements |
| GET | `/api/geo/communes/{deptCode}` | FeatureCollection communes |

## Donnees

Les donnees electorales couvrent 56 elections (1999-2026). Elles sont stockees au niveau commune dans PostGIS et agregees a la volee par l'API pour les niveaux departement et region.

| Table | Lignes |
|-------|--------|
| region | 26 |
| departement | 109 |
| commune | 35 039 |
| indicateur | 56 |
| indicateur_valeur | ~1.6M |

## Documentation

- [`docs/presentation_projet.md`](docs/presentation_projet.md) — Presentation du projet
- [`docs/architecture_carto.md`](docs/architecture_carto.md) — Architecture des donnees
- [`docs/build_election_data.md`](docs/build_election_data.md) — Pipeline Python ETL
- [`migration-plan.md`](migration-plan.md) — Plan de migration vers PostGIS + Spring Boot
