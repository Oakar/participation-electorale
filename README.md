# Carte electorale France

Carte interactive de la participation electorale en France, couvrant 56 elections de 1999 a 2026 (presidentielles, legislatives, europeennes, municipales, regionales, departementales, cantonales).

L'utilisateur navigue par zoom geographique (regions, departements, communes) et filtre par type d'election et tour. Un code couleur indique le taux de participation.

| Taux de participation | Couleur |
|-----------------------|---------|
| < 50%                 | Rouge   |
| 50% - 75%             | Blanc   |
| > 75%                 | Bleu    |

## Structure du projet

```
.
├── site/                   # Frontend Vue 3 + Leaflet
│   ├── src/
│   │   ├── components/     # ElectionMap, ElectionSelector, BreadcrumbNav, MapLegend
│   │   ├── composables/    # useAppState, useElectionData
│   │   ├── services/       # dao, staticDao (chargement des JSON)
│   │   └── utils/          # colors (calcul couleur participation)
│   └── public/
│       ├── geo/            # GeoJSON (regions, departements, communes)
│       └── data/           # JSON generes (symlink ou copie de data/json)
│
├── scripts/
│   ├── build_election_data.py  # Pipeline CSV → JSON (chunked, ~300 Mo peak)
│   └── aggregate_csv.py    # Agregation CSV bureau de vote → commune
│
├── data/
│   ├── csv/
│   │   ├── general_results.csv           # 3.16M lignes, granularite bureau de vote
│   │   ├── aggregated_results.csv        # Agrege par commune (genere par aggregate_csv.py)
│   │   └── ref_departements_regions.csv  # Referentiel departement → region
│   └── json/                             # Arborescence JSON (generee par build_election_data.py)
│       ├── elections.json
│       ├── regions/
│       ├── departements/{code_region}/
│       └── communes/{code_departement}/
│
├── docs/
│   ├── architecture_carto.md   # Architecture des donnees et schema JSON
│   └── build_election_data.md   # Documentation detaillee du pipeline
│
└── requirements.txt            # Dependances Python (pandas)
```

## Prerequis

- **Python 3.10+** et **pandas** pour le traitement des donnees
- **Node.js 18+** et **npm** pour le frontend

## Installation

```bash
# Dependances Python
pip install -r requirements.txt

# Dependances frontend
cd site && npm install
```

## Preparation des donnees

Le fichier source `data/csv/general_results.csv` contient les resultats bruts a granularite bureau de vote (387 Mo, 3.16M lignes). Le script `build_election_data.py` le decoupe en ~6 000 petits fichiers JSON charges a la demande par le navigateur.

```bash
python scripts/build_election_data.py
```

Le script :
1. Lit le CSV par chunks de 50 000 lignes (memoire peak ~300 Mo)
2. Enrichit chaque chunk avec les codes region via `ref_departements_regions.csv`
3. Agrege les bureaux de vote par commune
4. Derive les niveaux departement et region
5. Recalcule les ratios de participation a chaque niveau
6. Ecrit l'arborescence JSON dans `data/json/`

Les fichiers JSON doivent ensuite etre accessibles par le frontend dans `site/public/data/`.

## Lancer le site en developpement

```bash
cd site
npm run dev
```

Le serveur demarre sur `http://localhost:3000`.

## Build de production

```bash
cd site
npm run build
```

Les fichiers statiques sont generes dans `site/dist/`. Le site est deployable sur tout hebergement statique (GitHub Pages, Netlify, S3, etc.).

## Parcours utilisateur

| Action | Fichier JSON charge | Taille |
|--------|---------------------|--------|
| Ouverture du site | `elections.json` | < 5 Ko |
| Selection d'une election | `regions/{id_election}.json` | < 2 Ko |
| Clic sur une region | `departements/{code_region}/{id_election}.json` | < 2 Ko |
| Clic sur un departement | `communes/{code_dept}/{id_election}.json` | 5 - 50 Ko |

Le navigateur ne charge qu'un fichier a la fois. Aucune agregation cote client.

## Documentation

- [`docs/architecture_carto.md`](docs/architecture_carto.md) — architecture des donnees, schema JSON, arborescence
- [`docs/build_election_data.md`](docs/build_election_data.md) — documentation detaillee du pipeline Python
- [`scripts/README.md`](scripts/README.md) — documentation des scripts

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Carte interactive | [Leaflet](https://leafletjs.com/) 1.9 |
| Frontend | [Vue 3](https://vuejs.org/) (Composition API, TypeScript) |
| Build | [Vite](https://vite.dev/) 8 |
| Donnees geographiques | GeoJSON (IGN / france-geojson) |
| Pipeline donnees | Python 3.10+, pandas |
