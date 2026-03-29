# PRISME — Infrastructure

Ce dossier contient les fichiers Docker Compose des bases de donnees du projet PRISME.

Les bases de donnees tournent dans Docker et sont accessibles via le reseau par les applications (`server/`, `batch/`) qui, elles, tournent en dehors de Docker en developpement.

## Prerequis

- Docker et Docker Compose installes

## Demarrage

```bash
cd infra
docker compose up -d
```

PostGIS demarre sur `localhost:5432` avec la base `prisme`.

## Reseau Docker

Le docker-compose cree un reseau nomme `prisme-network`. Ce reseau permet :

- Aux containers de communiquer entre eux par nom de service (ex: `postgis:5432`)
- Aux futurs services dockerises (server Spring Boot en production, etc.) de rejoindre ce reseau

### Connecter un autre container au reseau

Si le backend Spring Boot tourne aussi dans Docker (ex: en production), il peut rejoindre le reseau existant :

```yaml
# dans un autre docker-compose.yml
services:
  api:
    build: ../server
    networks:
      - prisme-network

networks:
  prisme-network:
    external: true
```

Avec `external: true`, le compose reutilise le reseau `prisme-network` deja cree par `infra/docker-compose.yml` au lieu d'en creer un nouveau.

### En developpement (devcontainer)

Le devcontainer du projet est configure pour rejoindre le reseau `prisme-network` via `runArgs: ["--network=prisme-network"]` dans `.devcontainer/devcontainer.json`.

Les applications lancees dans le devcontainer (`mvn spring-boot:run`, `python import_all.py`, `npm run dev`) se connectent a PostGIS via le nom de service Docker : `postgis:5432`.

**Important :** le reseau `prisme-network` doit exister avant de lancer le devcontainer. Il faut donc demarrer l'infra en premier :

```bash
cd infra && docker compose up -d
```

## Parametres de connexion

| Parametre | Valeur |
|-----------|--------|
| Host | `postgis` (depuis le devcontainer ou tout container du reseau) |
| Port | `5432` |
| Base | `prisme` |
| Utilisateur | `prisme` |
| Mot de passe | `prisme` |

## Commandes utiles

```bash
# Demarrer les services
docker compose up -d

# Voir les logs
docker compose logs -f postgis

# Se connecter a la base en psql
docker exec -it prisme-postgis psql -U prisme -d prisme

# Verifier que PostGIS est installe
docker exec -it prisme-postgis psql -U prisme -d prisme -c "SELECT PostGIS_Version();"

# Arreter les services
docker compose down

# Arreter et supprimer les donnees
docker compose down -v
```
