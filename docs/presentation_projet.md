# PRISME - Presentation du projet

**PRISME** — Portail Regional d'Indicateurs Statistiques et de Mesures.

Plateforme de visualisation de donnees territoriales en France. L'utilisateur explore son territoire a travers differents indicateurs (elections, demographie, securite, economie, culture) sur une carte interactive a 3 niveaux de zoom (territoire, region, departement, commune).

---

## Table des matieres

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture globale](#architecture-globale)
3. [Brique 1 — Pipeline de donnees (Python)](#brique-1--pipeline-de-donnees-python)
4. [Brique 2 — Frontend interactif (Vue 3 + Leaflet)](#brique-2--frontend-interactif-vue-3--leaflet)
5. [Brique 3 — Donnees geographiques (GeoJSON)](#brique-3--donnees-geographiques-geojson)
6. [Brique 4 — Infrastructure et deploiement](#brique-4--infrastructure-et-deploiement)
7. [Fonctionnalites](#fonctionnalites)
8. [Parcours utilisateur](#parcours-utilisateur)
9. [Stack technique](#stack-technique)

---

## Vue d'ensemble

Le projet transforme un fichier CSV brut de 387 Mo (3,16 millions de lignes, granularite bureau de vote) en environ 6 000 petits fichiers JSON charges a la demande par le navigateur. Le site est 100 % statique : aucun serveur backend, aucune base de donnees. Il peut etre deploye sur GitHub Pages, Netlify, S3 ou tout hebergement de fichiers statiques.

**Chiffres cles :**

| Metrique | Valeur |
|----------|--------|
| Elections couvertes | 56 (1999 - 2026) |
| Types d'elections | 7 (pres, legi, euro, muni, regi, cant, dpmt) |
| Niveaux geographiques | 4 (territoire, region, departement, commune) |
| Fichiers JSON generes | ~6 157 |
| Taille max d'un fichier JSON | ~50 Ko (communes) |
| Memoire peak du pipeline | ~300 Mo |

---

## Architecture globale

```
┌───────────────────────────────────────────────────────────────────┐
│                        Donnees sources                            │
│  data/csv/general_results.csv          (387 Mo, 3.16M lignes)    │
│  data/csv/ref_departements_regions.csv (referentiel regions)      │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────────┐
│              Pipeline Python (batch/)                            │
│  build_election_data.py                                           │
│  Lecture par chunks → Enrichissement → Agregation → JSON          │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────────┐
│              Donnees generees (data/json/)                         │
│  elections.json                                                    │
│  regions/{id_election}.json                                       │
│  departements/{code_region}/{id_election}.json                    │
│  communes/{code_departement}/{id_election}.json                   │
└────────────────────────┬──────────────────────────────────────────┘
                         │  copie/symlink dans client/public/data/
                         ▼
┌───────────────────────────────────────────────────────────────────┐
│              Frontend Vue 3 (client/)                                │
│  Carte Leaflet + GeoJSON + selection d'elections                  │
│  Navigation hierarchique avec breadcrumbs                         │
│  Chargement a la demande des JSON                                 │
└───────────────────────────────────────────────────────────────────┘
```

---

## Brique 1 — Pipeline de donnees (Python)

**Fichier :** `batch/build_election_data.py` (362 lignes)
**Dependances :** Python 3.10+, pandas

### Objectif

Transformer le CSV brut des resultats electoraux (granularite bureau de vote) en une arborescence JSON pre-decoupee par niveau geographique et par election, directement consommable par le navigateur.

### Source des donnees

Les donnees electorales brutes proviennent de l'**open data gouvernemental** :
- **Source :** [data.gouv.fr — Resultats electoraux](https://explore.data.gouv.fr/fr/datasets/6481e741d4cf002ec0efec9d/)
- **Jeu de donnees :** resultats par bureau de vote pour l'ensemble des elections francaises depuis 1999
- **Licence :** Licence Ouverte / Open Licence (Etalab)

### Donnees d'entree

| Fichier | Taille | Description |
|---------|--------|-------------|
| `general_results.csv` | 387 Mo | Resultats par bureau de vote, separateur `;`, 25 colonnes (11 utilisees) — issu de data.gouv.fr |
| `ref_departements_regions.csv` | 2,5 Ko | Table de correspondance departement → region (102 lignes) |

Colonnes utilisees du CSV principal : `id_election`, `code_departement`, `libelle_departement`, `code_commune`, `libelle_commune`, `inscrits`, `abstentions`, `votants`, `blancs`, `nuls`, `exprimes`.

### Architecture du pipeline

Le pipeline est structure en 5 classes collaborant dans un flux lineaire :

```
RegionLookup ──► ChunkReader ──► Accumulator ──► JsonEmitter
                                                      │
                                                 Pipeline (orchestrateur)
```

| Classe | Responsabilite |
|--------|---------------|
| **PipelineConfig** | Configuration immuable (chemins, taille des chunks, colonnes) |
| **RegionLookup** | Charge le referentiel regions et enrichit les DataFrames avec `code_region` / `libelle_region` |
| **ChunkReader** | Lit le CSV par blocs de 50 000 lignes, convertit les types, enrichit avec les regions |
| **Accumulator** | Agrege les bureaux de vote au niveau commune en cumulant les sommes |
| **JsonEmitter** | Ecrit l'arborescence JSON (elections.json + 3 niveaux geographiques) |
| **Pipeline** | Orchestre le flux complet : chargement → ingestion → emission |

### Niveaux d'agregation

Pour chaque election, les donnees sont agregees en 3 niveaux :

1. **Communes** — regroupement des bureaux de vote par commune (`code_commune`)
2. **Departements** — somme des communes par departement (`code_departement`)
3. **Regions** — somme des departements par region (`code_region`)

A chaque niveau, trois ratios sont recalcules :
- `ratio_abstentions_inscrits` = abstentions / inscrits x 100
- `ratio_votants_inscrits` = votants / inscrits x 100
- `ratio_exprimes_votants` = exprimes / votants x 100

### Donnees de sortie

```
data/json/
├── elections.json                           # Index des 56 elections
├── regions/{id_election}.json               # 56 fichiers
├── departements/{code_region}/              # 23 dossiers
│   └── {id_election}.json                   # 56 fichiers par region → 741 total
└── communes/{code_departement}/             # 106 dossiers
    └── {id_election}.json                   # 56 fichiers par dept → 5 359 total
```

**Total : ~6 157 fichiers JSON**, format compact (sans indentation, UTF-8).

### Gestion memoire

Le CSV de 387 Mo n'est jamais charge en entier. La lecture par chunks de 50 000 lignes limite le pic memoire a environ 300 Mo, contre 1 a 2 Go si le fichier etait charge integralement.

---

## Brique 2 — Frontend interactif (Vue 3 + Leaflet)

**Dossier :** `client/`
**Stack :** Vue 3 (Composition API, TypeScript), Leaflet 1.9, Tailwind CSS 4, Vite 8

### Architecture des composants

```
App.vue
├── ElectionSelector.vue        # Selection du type d'election et du tour
├── BreadcrumbNav.vue           # Fil d'Ariane (territoire > region > departement)
├── TerritorySelector.vue       # Page d'accueil : choix du territoire
└── MapView.vue                 # Conteneur carte + sidebar
    ├── TerritorySidebar.vue    # Liste laterale des entites geographiques
    ├── ElectionMap.vue         # Carte Leaflet interactive
    ├── MapLegend.vue           # Legende du code couleur
    ├── TerritoryOutline.vue    # Apercu SVG du territoire
    ├── LoadingIndicator.vue    # Indicateur de chargement
    └── ErrorBlock.vue          # Affichage d'erreur avec bouton de retry
```

### Composants detailles

| Composant | Role |
|-----------|------|
| **App.vue** | Conteneur racine : header (titre, selecteur d'election, breadcrumb) + `<router-view>` |
| **TerritorySelector** | Page d'accueil affichant une grille de cartes (Metropole + Outre-mer) avec apercu SVG des contours |
| **MapView** | Layout flex combinant la sidebar et la carte |
| **ElectionMap** | Coeur de l'application : rendu Leaflet des GeoJSON, couleurs par taux de participation, tooltips au survol, navigation au clic |
| **TerritorySidebar** | Liste hierarchique des entites avec surbrillance synchronisee avec la carte |
| **ElectionSelector** | Deux niveaux de selection : type d'election puis election specifique (annee + tour) |
| **BreadcrumbNav** | Navigation cliquable montrant le chemin dans la hierarchie |
| **MapLegend** | Gradient de couleurs rouge → blanc → bleu avec les seuils de participation |

### Gestion d'etat (Composables)

L'etat de l'application repose sur 3 composables Vue 3 :

| Composable | Responsabilite |
|------------|---------------|
| **useAppState** | Etat global derive de la route : `viewLevel`, `currentElection`, `selectedTerritory`, `selectedRegion`, `selectedDepartement`, `hoveredCode`, `breadcrumb`. Fournit les methodes de navigation. |
| **useElectionData** | Chargement reactif des donnees : observe les parametres de route, interroge `staticDao`, gere le cache et l'annulation des requetes (`AbortSignal`). |
| **useGeoLabels** | Cache des noms geographiques (code → libelle) pour alimenter le breadcrumb et la sidebar avant l'arrivee des donnees completes. |

### Couche d'acces aux donnees

| Service | Role |
|---------|------|
| **dao.ts** | Interface d'acces aux donnees (type `Dao`) |
| **staticDao.ts** | Implementation : fetch des fichiers JSON statiques depuis `/public/data/` |

### Routage

Le routage utilise Vue Router en mode hash (`/#/...`) :

| Route | Vue | Niveau |
|-------|-----|--------|
| `/` | TerritorySelector | Selection du territoire |
| `/:territory` | MapView | Carte des regions |
| `/:territory/:region` | MapView | Carte des departements |
| `/:territory/:region/:dept` | MapView | Carte des communes |

L'election selectionnee est stockee en query parameter (`?election=2024_legi_t1`), permettant le partage d'URL.

### Systeme de couleurs

Le fichier `utils/colors.ts` convertit un taux de participation en couleur RGB par interpolation lineaire :

| Taux | Couleur | Signification |
|------|---------|---------------|
| 0 - 50 % | Rouge → Blanc | Participation faible |
| 50 - 75 % | Blanc | Participation moyenne |
| 75 - 100 % | Blanc → Bleu | Participation forte |

### Territoires

Les territoires regroupent les regions en zones navigables :

| Territoire | Regions |
|------------|---------|
| **Metropole** | 13 regions metropolitaines |
| **Amerique** | Guadeloupe, Martinique, Guyane |
| **Ocean Indien** | La Reunion, Mayotte |
| **Oceanie** | Nouvelle-Caledonie, Polynesie, Wallis-et-Futuna, Saint-Pierre-et-Miquelon |

Chaque territoire definit ses bornes geographiques (bounds) pour le cadrage initial de la carte.

---

## Brique 3 — Donnees geographiques (GeoJSON)

**Dossier :** `client/public/geo/`

Les contours geographiques sont stockes au format GeoJSON et charges par le composant `ElectionMap` :

| Fichier | Contenu | Chargement |
|---------|---------|------------|
| `regions.geojson` | Contours des regions francaises | A la selection d'un territoire |
| `departements.geojson` | Contours des departements | Au clic sur une region |
| `communes/{code_dept}.geojson` | Contours des communes par departement (96 fichiers) | Au clic sur un departement |

Chaque feature GeoJSON porte dans ses `properties` un champ `code` et `nom`, utilises pour faire la jointure avec les donnees de participation.

Les fichiers GeoJSON sont mis en cache cote client pour eviter les rechargements.

---

## Brique 4 — Infrastructure et deploiement

### Environnement de developpement

Le projet inclut une configuration **Dev Container** (`.devcontainer/`) :
- Image de base : Python 3.12 + Node.js 20
- Outils globaux : TypeScript, Claude Code CLI
- Ports exposes : 3000 (frontend), 8000, 5173
- Extensions VS Code : Python, ESLint, Prettier, Volar, Tailwind CSS

### CI/CD

Le fichier `.github/workflows/deploy.yml` deploie automatiquement le site sur **GitHub Pages** :
1. Declenchement : push sur `main` ou dispatch manuel
2. Build : `npm run build` (verification TypeScript + build Vite)
3. Deploiement : publication du dossier `client/dist/` sur GitHub Pages

### Commandes

| Commande | Description |
|----------|-------------|
| `pip install -r batch/requirements.txt` | Installation des dependances Python |
| `cd site && npm install` | Installation des dependances frontend |
| `python batch/build_election_data.py` | Generation des fichiers JSON (~6 000 fichiers) |
| `cd site && npm run dev` | Serveur de developpement (port 3000) |
| `cd site && npm run build` | Build de production dans `client/dist/` |
| `cd site && npm run preview` | Apercu du build de production |

---

## Fonctionnalites

### Navigation geographique multi-niveaux
- **4 niveaux** : territoire → region → departement → commune
- Navigation par clic sur la carte ou dans la sidebar
- Fil d'Ariane cliquable pour remonter dans la hierarchie
- Auto-skip des niveaux a un seul resultat

### Visualisation cartographique
- Carte choropleth coloree selon le taux de participation
- Gradient rouge (faible) → blanc (moyen) → bleu (fort)
- Tooltips au survol affichant le nom, le taux de participation et le nombre d'inscrits/votants
- Synchronisation carte ↔ sidebar (surbrillance au survol)

### Filtrage des elections
- Selection par type d'election (presidentielle, legislatives, etc.)
- Selection de l'annee et du tour
- 7 types d'elections couverts sur 56 scrutins

### Performance et UX
- **Chargement a la demande** : un seul fichier JSON charge a la fois (< 50 Ko)
- **Aucune agregation cote client** : les calculs sont pre-realises par le pipeline Python
- **Cache des GeoJSON** : les contours geographiques ne sont charges qu'une fois
- **Cache des labels** : les noms geographiques sont memorises pour le breadcrumb
- **Annulation des requetes** : les requetes en cours sont annulees lors d'un changement de vue
- **URL partageable** : l'etat de la vue est encode dans l'URL (territoire, region, departement, election)

### Support Outre-mer
- Territoires ultramarins regroupes par zone (Amerique, Ocean Indien, Oceanie)
- Bornes geographiques specifiques pour le cadrage de la carte
- Donnees electorales disponibles au meme niveau de detail que la metropole

---

## Parcours utilisateur

```
┌─────────────────────┐     ┌─────────────────────┐
│  Page d'accueil     │     │  Selection election  │
│  Choix du territoire│────►│  Type + annee + tour │
│  (grille de cartes) │     │  (header)            │
└─────────────────────┘     └──────────┬───────────┘
                                       │
                            ┌──────────▼───────────┐
                            │  Carte des regions    │
                            │  regions/{id}.json    │  < 2 Ko
                            └──────────┬───────────┘
                                       │ clic sur une region
                            ┌──────────▼───────────┐
                            │  Carte des departements│
                            │  departements/         │  < 2 Ko
                            │  {code_region}/{id}.json│
                            └──────────┬───────────┘
                                       │ clic sur un departement
                            ┌──────────▼───────────┐
                            │  Carte des communes   │
                            │  communes/             │  5-50 Ko
                            │  {code_dept}/{id}.json │
                            └──────────────────────┘
```

A chaque etape, le navigateur ne charge qu'un fichier JSON et le GeoJSON correspondant. L'experience est fluide meme sur des connexions lentes.

---

## Stack technique

| Brique | Technologie | Version |
|--------|-------------|---------|
| Carte interactive | [Leaflet](https://leafletjs.com/) | 1.9 |
| Framework frontend | [Vue 3](https://vuejs.org/) (Composition API) | 3.5 |
| Langage frontend | TypeScript | 5.9 |
| Build frontend | [Vite](https://vite.dev/) | 8.0 |
| Styles | [Tailwind CSS](https://tailwindcss.com/) | 4.2 |
| Donnees geographiques | GeoJSON (IGN / france-geojson) | — |
| Pipeline donnees | Python + pandas | 3.10+ |
| CI/CD | GitHub Actions → GitHub Pages | — |
| Environnement dev | Dev Container (Python 3.12 + Node.js 20) | — |
