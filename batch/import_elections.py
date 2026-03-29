"""
Charge les donnees electorales (CSV) dans PostGIS.

Reprend la logique d'agregation BV -> commune de build_election_data.py,
puis insere dans indicateur + indicateur_valeur.

Usage:
    python batch/import_elections.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from db_config import get_psycopg2_params

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "csv"

INPUT_FILE = DATA_DIR / "general_results.csv"
REF_FILE = DATA_DIR / "ref_departements_regions.csv"

SEPARATOR = ";"
CHUNK_SIZE = 50_000

NUMERIC_COLS = ("inscrits", "abstentions", "votants", "blancs", "nuls", "exprimes")

USECOLS = (
    "id_election", "code_departement",
    "code_commune",
    "inscrits", "abstentions", "votants", "blancs", "nuls", "exprimes",
)

ELECTION_TYPES = {
    "pres": "Presidentielle",
    "legi": "Legislatives",
    "euro": "Europeennes",
    "regi": "Regionales",
    "dpmt": "Departementales",
    "cant": "Cantonales",
    "muni": "Municipales",
}

TOUR_LABELS = {"t1": "1er tour", "t2": "2nd tour"}


def build_region_map() -> dict[str, str]:
    ref = pd.read_csv(REF_FILE, sep=SEPARATOR, dtype=str)
    return dict(zip(ref["code_departement"], ref["code_region"]))


def parse_election_id(id_election: str) -> dict:
    parts = id_election.split("_")
    annee = int(parts[0])
    type_code = parts[1]
    tour = parts[2]
    type_label = ELECTION_TYPES.get(type_code, type_code)
    tour_label = TOUR_LABELS.get(tour, tour)
    return {
        "annee": annee,
        "type_code": type_code,
        "tour": tour,
        "nom": f"{type_label} {annee} — {tour_label}",
    }


def accumulate_communes(region_map: dict[str, str]) -> dict[tuple[str, str], dict]:
    """Lit le CSV par chunks et agrege au niveau commune."""
    acc: dict[tuple[str, str], dict] = {}
    total = 0

    reader = pd.read_csv(
        INPUT_FILE, sep=SEPARATOR, dtype=str,
        usecols=list(USECOLS), chunksize=CHUNK_SIZE,
    )
    for chunk in reader:
        for col in NUMERIC_COLS:
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce").fillna(0).astype(int)
        chunk["code_region"] = chunk["code_departement"].map(region_map)

        grouped = chunk.groupby(
            ["id_election", "code_commune", "code_departement", "code_region"],
            as_index=False,
        )[list(NUMERIC_COLS)].sum()

        for row in grouped.itertuples(index=False):
            key = (row.id_election, row.code_commune)
            entry = acc.get(key)
            if entry is None:
                entry = {
                    "code_departement": row.code_departement,
                    "code_region": row.code_region,
                }
                for col in NUMERIC_COLS:
                    entry[col] = 0
                acc[key] = entry
            for col in NUMERIC_COLS:
                entry[col] += getattr(row, col)

        total += len(chunk)
        print(f"  {total:>10,} lignes lues", end="\r")

    print(f"  {total:>10,} lignes lues — {len(acc)} enregistrements communes")
    return acc


def insert_categorie(cur) -> None:
    cur.execute(
        "INSERT INTO categorie_indicateur (id, nom) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        ("elections", "Elections"),
    )


def insert_indicateurs(cur, election_ids: list[str]) -> None:
    rows = []
    for id_election in election_ids:
        info = parse_election_id(id_election)
        rows.append((
            id_election,
            "elections",
            info["nom"],
            "%",
            info["annee"],
            f'{{"type": "{info["type_code"]}", "tour": "{info["tour"]}", "aggregation": "sum"}}',
        ))
    execute_values(
        cur,
        "INSERT INTO indicateur (id, categorie_id, nom, unite, annee, metadata) VALUES %s ON CONFLICT DO NOTHING",
        rows,
    )
    print(f"  {len(rows)} indicateurs inseres.")


def insert_valeurs_communes(cur, acc: dict[tuple[str, str], dict]) -> None:
    """Insere les valeurs au niveau commune."""
    # Charger les codes communes existants pour ignorer les orphelins
    cur.execute("SELECT code FROM commune")
    valid_communes = {row[0] for row in cur.fetchall()}

    batch = []
    batch_size = 5000
    total = 0
    skipped = 0

    for (id_election, code_commune), entry in acc.items():
        if code_commune not in valid_communes:
            skipped += 1
            continue

        inscrits = entry["inscrits"]
        exprimes = entry["exprimes"]
        valeur = round(exprimes / inscrits, 4) if inscrits > 0 else 0

        details = {col: entry[col] for col in NUMERIC_COLS}

        batch.append((
            id_election,
            entry["code_region"],
            entry["code_departement"],
            code_commune,
            valeur,
            psycopg2.extras.Json(details),
        ))

        if len(batch) >= batch_size:
            _flush(cur, batch)
            total += len(batch)
            print(f"  {total:>10,} valeurs inserees", end="\r")
            batch.clear()

    if batch:
        _flush(cur, batch)
        total += len(batch)

    print(f"  {total:>10,} valeurs inserees (communes), {skipped} orphelins ignores")


def _flush(cur, batch: list[tuple]) -> None:
    execute_values(
        cur,
        """INSERT INTO indicateur_valeur
           (indicateur_id, code_region, code_departement, code_commune, valeur, details)
           VALUES %s""",
        batch,
    )


def truncate_election_data(cur) -> None:
    cur.execute("DELETE FROM indicateur_valeur WHERE indicateur_id IN (SELECT id FROM indicateur WHERE categorie_id = 'elections')")
    cur.execute("DELETE FROM indicateur WHERE categorie_id = 'elections'")
    cur.execute("DELETE FROM categorie_indicateur WHERE id = 'elections'")
    print("  Donnees elections purgees.")


def run() -> None:
    print("=== Import des donnees electorales ===")

    print("Chargement du referentiel regions...")
    region_map = build_region_map()

    print(f"Lecture de {INPUT_FILE} par chunks de {CHUNK_SIZE}...")
    acc = accumulate_communes(region_map)

    election_ids = sorted({k[0] for k in acc})
    print(f"  {len(election_ids)} elections detectees.")

    print("Insertion en base...")
    conn = psycopg2.connect(**get_psycopg2_params())
    try:
        with conn:
            with conn.cursor() as cur:
                truncate_election_data(cur)
                insert_categorie(cur)
                insert_indicateurs(cur, election_ids)
                insert_valeurs_communes(cur, acc)
    finally:
        conn.close()

    print("=== Import elections termine ===\n")


if __name__ == "__main__":
    run()
