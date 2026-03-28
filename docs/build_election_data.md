# Documentation du script `build_election_data.py`

## Vue d'ensemble

Le script `scripts/build_election_data.py` transforme le fichier CSV brut des resultats electoraux (`data/csv/general_results.csv`, 387 Mo, ~3.16M lignes a granularite **bureau de vote**) en une arborescence de petits fichiers JSON pre-decoupes par niveau geographique et par election.

Le script lit le CSV **par chunks** (50 000 lignes) pour limiter la consommation memoire, agrege incrementalement les bureaux de vote en communes, puis derive les niveaux departement et region. Les informations de region (absentes du CSV) sont injectees via le fichier de reference `data/csv/ref_departements_regions.csv`.

Le design complet de l'arborescence cible est decrit dans [`docs/architecture_carto.md`](architecture_carto.md).

## Prerequis

- **Python 3.10+**
- **pandas** (`pip install pandas`)
- `data/csv/general_results.csv` — CSV brut a granularite bureau de vote (separateur `;`)
- `data/csv/ref_departements_regions.csv` — mapping departement → region (102 lignes)

## Usage

```bash
python scripts/build_election_data.py
```

Aucun argument requis. Les chemins sont configurables via `PipelineConfig`.

## Fichiers d'entree

### `general_results.csv`

CSV avec separateur `;`, une ligne par **bureau de vote** et par election.

| Colonne utilisee | Type | Description |
|-------------------|------|-------------|
| `id_election` | string | Identifiant `{annee}_{type}_{tour}` (ex: `2022_pres_t1`) |
| `code_departement` | string | Code du departement |
| `libelle_departement` | string | Nom du departement |
| `code_commune` | string | Code INSEE de la commune (inclut le prefixe departement) |
| `libelle_commune` | string | Nom de la commune |
| `inscrits` | number | Nombre d'inscrits |
| `abstentions` | number | Nombre d'abstentions |
| `votants` | number | Nombre de votants |
| `blancs` | number | Nombre de votes blancs |
| `nuls` | number | Nombre de votes nuls |
| `exprimes` | number | Nombre de votes exprimes |

Les colonnes non listees (`code_bv`, `code_canton`, `code_circonscription`, ratios CSV, `id_brut_miom`) sont ignorees via `usecols`.

### `ref_departements_regions.csv`

| Colonne | Description |
|---------|-------------|
| `code_departement` | Code du departement |
| `code_region` | Code de la region |
| `libelle_region` | Nom de la region |

## Sortie produite

```
data/json/
├── elections.json                              # Index des 56 elections
├── regions/{id_election}.json                  # Donnees agregees par region
├── departements/{code_region}/{id_election}.json    # Departements d'une region
├── communes/{code_departement}/{id_election}.json   # Communes d'un departement
```

Les fichiers JSON sont compacts (pas d'indentation, `separators=(",", ":")`) et encodes en UTF-8.

## Architecture du pipeline

```
general_results.csv (387 Mo)        ref_departements_regions.csv
        |                                    |
        v                                    v
   ChunkReader (50K lignes)           RegionLookup (dict)
        |                                    |
        +-------- enrichissement region -----+
        |
        v
   Accumulator (groupby chunk → merge dans dict)
        |  dict[(id_election, code_commune)] = {labels + sommes}
        |
        v (apres dernier chunk)
   JsonEmitter — pour chaque election :
        |— communes DataFrame → compute_ratios → communes/*.json
        |— groupby dept → compute_ratios → departements/*.json
        |— groupby region → compute_ratios → regions/*.json
        +— elections.json
```

## Classes et responsabilites

### `PipelineConfig` (dataclass, frozen)

Parametres injectables du pipeline : chemins, separateur, chunk_size, colonnes.

| Parametre | Valeur par defaut | Role |
|-----------|-------------------|------|
| `input_file` | `data/csv/general_results.csv` | CSV source |
| `ref_file` | `data/csv/ref_departements_regions.csv` | Referentiel regions |
| `output_dir` | `data/json` | Dossier de sortie |
| `chunk_size` | `50_000` | Taille des chunks de lecture |
| `numeric_columns` | 6 colonnes | Colonnes sommables |
| `usecols` | 11 colonnes | Colonnes lues du CSV |
| `json_column_order` | 15 colonnes | Schema JSON de sortie |

### `RegionLookup`

Charge `ref_departements_regions.csv` (102 lignes) et expose `enrich(df)` qui ajoute `code_region` et `libelle_region` a un DataFrame via mapping sur `code_departement`.

### `ChunkReader`

Lit le CSV par chunks de 50K lignes via `pd.read_csv(chunksize=...)`. Pour chaque chunk :
1. Ne charge que les `usecols` (11 colonnes sur 25)
2. Type les colonnes numeriques en int
3. Enrichit avec les colonnes region via `RegionLookup`

### `Accumulator`

Accumule les sommes numeriques au niveau commune a travers tous les chunks.

- **`ingest(chunk)`** : pre-agrege le chunk par `groupby` pandas, puis fusionne les sommes dans un dictionnaire interne `(id_election, code_commune) → {labels + sommes}`
- **`election_ids()`** : retourne la liste triee des elections vues
- **`get_commune_df(id_election)`** : reconstruit un DataFrame communes pour une election

L'accumulation gere correctement les communes dont les bureaux de vote sont repartis sur plusieurs chunks.

### `JsonEmitter`

Ecrit toute l'arborescence JSON a partir de l'accumulateur. Pour chaque election :
1. Recupere le DataFrame communes, calcule les ratios, ecrit les fichiers communes
2. Agrege par departement, calcule les ratios, ecrit les fichiers departements
3. Agrege par region, calcule les ratios, ecrit les fichiers regions
4. Ecrit `elections.json` (index)

### `Pipeline`

Orchestre le tout :
1. Charge le referentiel regions
2. Itere les chunks et les ingere dans l'accumulateur
3. Declenche l'emission JSON
4. Affiche le bilan

## Fonctions pures

### `compute_ratios(df)`

Recalcule 3 ratios arrondis a 2 decimales (retourne une copie, sans mutation) :

| Ratio | Formule |
|-------|---------|
| `ratio_abstentions_inscrits` | `abstentions / inscrits * 100` |
| `ratio_votants_inscrits` | `votants / inscrits * 100` |
| `ratio_exprimes_votants` | `exprimes / votants * 100` |

### `to_records(df, null_columns, column_order)`

Convertit un DataFrame en `list[dict]` avec le schema JSON commun. Les `null_columns` sont mises a `null` selon le niveau d'agregation.

### `write_json(path, data)`

Ecrit un fichier JSON compact avec creation des repertoires parents.

## Consommation memoire

| Composant | Estimation |
|-----------|-----------|
| Chunk en lecture | ~30 Mo (50K lignes pandas) |
| Accumulateur | ~200-300 Mo (56 elections x ~35K communes) |
| Emission (1 election) | ~negligeable (~35K lignes) |
| **Peak total** | **~300 Mo** |

A comparer avec ~1-2 Go si le CSV etait charge integralement dans pandas.

## Volumetrie de sortie

| Niveau | Nombre de fichiers |
|--------|--------------------|
| `elections.json` | 1 |
| `regions/` | 56 |
| `departements/` | 736 |
| `communes/` | 5 354 |
| **Total** | **6 147 fichiers** |

## Points d'attention

- **Execution destructive** : `data/json/` est entierement supprime a chaque execution.
- **Division par zero** : si `inscrits` ou `votants` vaut 0, les ratios produiront `NaN`/`inf`.
- **Pas de validation d'entree** : une colonne manquante dans le CSV provoquera une `KeyError`.
