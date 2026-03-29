# Architecture données — PRISME

## Objectif

Afficher les résultats électoraux sur une carte de France interactive (site statique) avec 3 niveaux de zoom :

1. **Régions** — vue par défaut
2. **Départements** — au clic sur une région
3. **Communes** — au clic sur un département

Un code couleur indique le taux de participation (`exprimes / inscrits * 100`) :

| Couleur | Taux de participation |
|---------|-----------------------|
| Rouge   | < 50%                 |
| Blanc   | 50% — 75%             |
| Bleu    | > 75%                 |

L'utilisateur peut filtrer par type d'élection et tour.

## Problème

Le fichier `aggregated_results.csv` fait ~1.6M de lignes (56 élections x ~35 000 communes). Charger ce fichier entièrement dans le navigateur n'est pas viable :

- Téléchargement de plusieurs dizaines de Mo
- Parsing CSV côté client coûteux
- Consommation mémoire excessive

## Solution : pré-découpage en JSON sur le filesystem

### Principe

Découper les données en petits fichiers JSON, organisés par niveau géographique. Chaque niveau (régions, départements, communes) a son propre dossier, avec un sous-dossier par scope parent. Chaque élection correspond à un fichier JSON nommé `{id_election}.json`. Le navigateur ne charge que le fichier correspondant à la vue courante.

### Arborescence

```
data/json/
├── elections.json                                # index des élections disponibles
│
├── regions/                                      # vue France entière
│   ├── 2002_pres_t1.json                         # toutes les régions pour cette élection
│   ├── 2002_pres_t2.json
│   └── ...                                       # 1 fichier par élection (56 fichiers)
│
├── departements/                                 # départements, groupés par région
│   ├── 84/                                       # Auvergne-Rhône-Alpes (code_region)
│   │   ├── 2002_pres_t1.json                     # départements de la région pour cette élection
│   │   ├── 2002_pres_t2.json
│   │   └── ...
│   ├── 27/                                       # Bourgogne-Franche-Comté
│   │   └── ...
│   └── ...
│
├── communes/                                     # communes, groupées par département
│   ├── 01/                                       # Ain (code_departement)
│   │   ├── 2002_pres_t1.json                     # communes du département pour cette élection
│   │   ├── 2002_pres_t2.json
│   │   └── ...
│   ├── 07/                                       # Ardèche
│   │   └── ...
│   └── ...
│
└── ...
```

### Décomposition de `id_election`

Le champ `id_election` suit le format `{année}_{type}_{tour}`, par exemple `2002_pres_t1`.

| Code   | Type d'élection   |
|--------|-------------------|
| `pres` | Présidentielle    |
| `legi` | Législative       |
| `euro` | Européenne        |
| `muni` | Municipale        |
| `cant` | Cantonale         |
| `regi` | Régionale         |
| `dpmt` | Départementale    |

### `elections.json` — index

Liste toutes les élections disponibles pour alimenter les filtres de l'interface.

```json
[
  { "type": "pres", "tour": "t1", "annee": "2002", "id_election": "2002_pres_t1" },
  { "type": "pres", "tour": "t2", "annee": "2002", "id_election": "2002_pres_t2" },
  { "type": "euro", "tour": "t1", "annee": "2004", "id_election": "2004_euro_t1" }
]
```

### Schéma JSON commun

Tous les fichiers de données (`regions/`, `departements/`, `communes/`) partagent le même schéma. Chaque fichier contient un tableau d'objets conformes à cette structure :

```json
{
  "code_region":                "string | null",
  "libelle_region":             "string | null",
  "code_departement":           "string | null",
  "libelle_departement":        "string | null",
  "code_commune":               "string | null",
  "libelle_commune":            "string | null",
  "inscrits":                   "number",
  "abstentions":                "number",
  "votants":                    "number",
  "blancs":                     "number",
  "nuls":                       "number",
  "exprimes":                   "number",
  "ratio_abstentions_inscrits": "number",
  "ratio_votants_inscrits":     "number",
  "ratio_exprimes_votants":     "number"
}
```

Les champs géographiques sont renseignés ou `null` selon le niveau d'agrégation :

| Champ                | Régions | Départements | Communes |
|----------------------|---------|--------------|----------|
| `code_region`        | x       | x            | x        |
| `libelle_region`     | x       | x            | x        |
| `code_departement`   | null    | x            | x        |
| `libelle_departement`| null    | x            | x        |
| `code_commune`       | null    | null         | x        |
| `libelle_commune`    | null    | null         | x        |
| colonnes numériques  | x       | x            | x        |

Les colonnes numériques (`inscrits` à `ratio_exprimes_votants`) sont toujours présentes. Les ratios sont recalculés après chaque agrégation.

#### Exemple — `regions/2002_pres_t1.json`

```json
[
  {
    "code_region": "84",
    "libelle_region": "Auvergne-Rhône-Alpes",
    "code_departement": null,
    "libelle_departement": null,
    "code_commune": null,
    "libelle_commune": null,
    "inscrits": 5000000,
    "abstentions": 2500000,
    "votants": 2500000,
    "blancs": 25000,
    "nuls": 12000,
    "exprimes": 2463000,
    "ratio_abstentions_inscrits": 50.0,
    "ratio_votants_inscrits": 50.0,
    "ratio_exprimes_votants": 98.52
  }
]
```

#### Exemple — `departements/84/2002_pres_t1.json`

```json
[
  {
    "code_region": "84",
    "libelle_region": "Auvergne-Rhône-Alpes",
    "code_departement": "01",
    "libelle_departement": "Ain",
    "code_commune": null,
    "libelle_commune": null,
    "inscrits": 350000,
    "abstentions": 175000,
    "votants": 175000,
    "blancs": 1800,
    "nuls": 900,
    "exprimes": 172300,
    "ratio_abstentions_inscrits": 50.0,
    "ratio_votants_inscrits": 50.0,
    "ratio_exprimes_votants": 98.46
  }
]
```

#### Exemple — `communes/01/2002_pres_t1.json`

```json
[
  {
    "code_region": "84",
    "libelle_region": "Auvergne-Rhône-Alpes",
    "code_departement": "01",
    "libelle_departement": "Ain",
    "code_commune": "01001",
    "libelle_commune": "Abergement Clemenciat (L')",
    "inscrits": 492,
    "abstentions": 290,
    "votants": 202,
    "blancs": 0,
    "nuls": 8,
    "exprimes": 194,
    "ratio_abstentions_inscrits": 58.94,
    "ratio_votants_inscrits": 41.06,
    "ratio_exprimes_votants": 96.04
  }
]
```

### Parcours utilisateur et requêtes

| Action | Fichier chargé | Taille estimée |
|--------|---------------|----------------|
| Ouverture du site | `elections.json` | < 5 Ko |
| Sélection d'une élection | `regions/{id_election}.json` | < 2 Ko |
| Clic sur une région | `departements/{code_region}/{id_election}.json` | < 2 Ko |
| Clic sur un département | `communes/{code_departement}/{id_election}.json` | 5 — 50 Ko |

Le navigateur ne charge jamais plus qu'un fichier à la fois par action. Aucun calcul d'agrégation côté client.

### Volumétrie estimée

- 56 élections
- 1 dossier `regions/` → 56 fichiers
- `departements/` → 18 sous-dossiers x 56 = ~1 008 fichiers
- `communes/` → ~100 sous-dossiers x 56 = ~5 600 fichiers
- **Total : ~6 700 fichiers**, quelques dizaines de Mo au total sur disque

Compatible avec tout hébergement statique (GitHub Pages, Netlify, S3, etc.).

### Couleur de participation

Le calcul du taux et la classification couleur se font côté client à partir des données déjà présentes dans chaque fichier :

```
taux = exprimes / inscrits * 100
```

| Taux         | Couleur |
|--------------|---------|
| < 50%        | Rouge   |
| 50% — 75%    | Blanc   |
| > 75%        | Bleu    |

Le calcul est trivial et ne justifie pas de le pré-calculer dans les fichiers.

## Script à développer

Un script `batch/build_election_data.py` qui :

1. Lit `data/csv/aggregated_results.csv`
2. Décompose `id_election` en `type`, `tour`, `annee`
3. Agrège à 3 niveaux (région, département, commune)
4. Recalcule les ratios à chaque niveau
5. Génère l'arborescence JSON décrite ci-dessus
6. Génère `elections.json`

## Cartographie (GeoJSON)

Les contours géographiques nécessaires pour dessiner la carte :

- Régions : `regions.geojson`
- Départements : `departements.geojson`
- Communes : `communes.geojson` (ou découpé par département pour limiter la taille)

Sources possibles : données IGN simplifiées, projet [france-geojson](https://github.com/gregoiredavid/france-geojson) (licence ouverte).

La jointure entre les données et la carte se fait sur `code_region`, `code_departement` ou `code_commune`.
