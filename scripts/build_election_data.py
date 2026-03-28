"""
Genere l'arborescence JSON pour la carte electorale a partir du CSV brut.

Lit le CSV bureau de vote par chunks, agrege incrementalement
(BV -> commune -> departement -> region), et ecrit les fichiers JSON.

Voir docs/architecture_carto.md pour le detail de l'arborescence et du schema.

Usage:
    python scripts/prepare_json.py
"""

from __future__ import annotations

import json
import shutil
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import pandas as pd


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PipelineConfig:
    """Parametres du pipeline, injectables pour les tests."""

    input_file: Path = Path("data/csv/general_results.csv")
    ref_file: Path = Path("data/csv/ref_departements_regions.csv")
    output_dir: Path = Path("data/json")
    separator: str = ";"
    chunk_size: int = 50_000

    numeric_columns: tuple[str, ...] = (
        "inscrits", "abstentions", "votants", "blancs", "nuls", "exprimes",
    )

    usecols: tuple[str, ...] = (
        "id_election", "code_departement", "libelle_departement",
        "code_commune", "libelle_commune",
        "inscrits", "abstentions", "votants", "blancs", "nuls", "exprimes",
    )

    json_column_order: tuple[str, ...] = (
        "code_region", "libelle_region",
        "code_departement", "libelle_departement",
        "code_commune", "libelle_commune",
        "inscrits", "abstentions", "votants", "blancs", "nuls", "exprimes",
        "ratio_abstentions_inscrits",
        "ratio_votants_inscrits",
        "ratio_exprimes_votants",
    )


# ---------------------------------------------------------------------------
# Fonctions pures
# ---------------------------------------------------------------------------


def compute_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Recalcule les 3 ratios apres agregation (retourne une copie)."""
    df = df.copy()
    df["ratio_abstentions_inscrits"] = (df["abstentions"] / df["inscrits"] * 100).round(2)
    df["ratio_votants_inscrits"] = (df["votants"] / df["inscrits"] * 100).round(2)
    df["ratio_exprimes_votants"] = (df["exprimes"] / df["votants"] * 100).round(2)
    return df


def to_records(
    df: pd.DataFrame,
    null_columns: list[str],
    column_order: tuple[str, ...],
) -> list[dict]:
    """Convertit un DataFrame en liste de dicts avec le schema commun (sans mutation)."""
    df = df.copy()
    for col in null_columns:
        df[col] = None
    for col in column_order:
        if col not in df.columns:
            df[col] = None
    return df[list(column_order)].to_dict(orient="records")


def write_json(path: Path, data: list[dict]) -> None:
    """Ecrit un fichier JSON compact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------------------
# RegionLookup
# ---------------------------------------------------------------------------


class RegionLookup:
    """Mapping departement -> region a partir du fichier de reference."""

    def __init__(self, config: PipelineConfig) -> None:
        ref = pd.read_csv(config.ref_file, sep=config.separator, dtype=str)
        self._region_map: dict[str, str] = dict(
            zip(ref["code_departement"], ref["code_region"])
        )
        self._label_map: dict[str, str] = dict(
            zip(ref["code_departement"], ref["libelle_region"])
        )

    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajoute code_region et libelle_region au DataFrame."""
        df = df.copy()
        df["code_region"] = df["code_departement"].map(self._region_map)
        df["libelle_region"] = df["code_departement"].map(self._label_map)
        return df


# ---------------------------------------------------------------------------
# ChunkReader
# ---------------------------------------------------------------------------


class ChunkReader:
    """Lit le CSV par chunks, type les colonnes et enrichit avec les regions."""

    def __init__(self, config: PipelineConfig, region_lookup: RegionLookup) -> None:
        self._config = config
        self._region_lookup = region_lookup

    def iter_chunks(self) -> Iterator[pd.DataFrame]:
        """Yield des DataFrames prets a ingerer."""
        reader = pd.read_csv(
            self._config.input_file,
            sep=self._config.separator,
            dtype=str,
            usecols=list(self._config.usecols),
            chunksize=self._config.chunk_size,
        )
        for chunk in reader:
            for col in self._config.numeric_columns:
                chunk[col] = pd.to_numeric(chunk[col], errors="coerce").fillna(0).astype(int)
            chunk = self._region_lookup.enrich(chunk)
            yield chunk


# ---------------------------------------------------------------------------
# Accumulator
# ---------------------------------------------------------------------------

# Colonnes de labels conservees dans l'accumulateur
_LABEL_KEYS = (
    "libelle_commune", "code_departement", "libelle_departement",
    "code_region", "libelle_region",
)

# Colonnes de groupby pour pre-agreger chaque chunk
_GROUPBY_COLS = [
    "id_election", "code_commune", *_LABEL_KEYS,
]


class Accumulator:
    """Accumule les sommes au niveau commune a travers les chunks."""

    def __init__(self, config: PipelineConfig) -> None:
        self._numeric = list(config.numeric_columns)
        # (id_election, code_commune) -> {label: str, ..., col_num: int, ...}
        self._data: dict[tuple[str, str], dict] = {}

    def ingest(self, chunk: pd.DataFrame) -> None:
        """Pre-agrege le chunk puis fusionne dans l'accumulateur."""
        grouped = (
            chunk.groupby(_GROUPBY_COLS, as_index=False)[self._numeric].sum()
        )
        for row in grouped.itertuples(index=False):
            key = (row.id_election, row.code_commune)
            entry = self._data.get(key)
            if entry is None:
                entry = {label: getattr(row, label) for label in _LABEL_KEYS}
                for col in self._numeric:
                    entry[col] = 0
                self._data[key] = entry
            for col in self._numeric:
                entry[col] += getattr(row, col)

    def election_ids(self) -> list[str]:
        """Retourne les id_election tries."""
        return sorted({k[0] for k in self._data})

    def get_commune_df(self, id_election: str) -> pd.DataFrame:
        """Reconstruit un DataFrame communes pour une election donnee."""
        rows = []
        for (elec, code_commune), entry in self._data.items():
            if elec != id_election:
                continue
            row = {"code_commune": code_commune, **entry}
            rows.append(row)
        return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# JsonEmitter
# ---------------------------------------------------------------------------


class JsonEmitter:
    """Ecrit toute l'arborescence JSON a partir de l'accumulateur."""

    def __init__(self, config: PipelineConfig) -> None:
        self._config = config
        self._counts: dict[str, int] = defaultdict(int)

    def emit_all(self, accumulator: Accumulator) -> None:
        """Genere elections.json puis les 3 niveaux geographiques."""
        self._prepare_output_dir()

        election_ids = accumulator.election_ids()
        self._emit_elections_index(election_ids)

        for i, id_election in enumerate(election_ids, 1):
            print(f"  [{i}/{len(election_ids)}] {id_election}")
            df_communes = compute_ratios(accumulator.get_commune_df(id_election))
            self._emit_communes(id_election, df_communes)

            df_dept = self._aggregate_departements(df_communes)
            self._emit_departements(id_election, df_dept)

            df_reg = self._aggregate_regions(df_dept)
            self._emit_regions(id_election, df_reg)

    def report(self) -> None:
        """Affiche le bilan de generation."""
        for level, count in self._counts.items():
            print(f"  {level} : {count} fichiers")

    # -- Output dir --

    def _prepare_output_dir(self) -> None:
        if self._config.output_dir.exists():
            shutil.rmtree(self._config.output_dir)
        self._config.output_dir.mkdir(parents=True)

    # -- Elections index --

    def _emit_elections_index(self, election_ids: list[str]) -> None:
        elections = []
        for id_election in election_ids:
            parts = id_election.split("_")
            elections.append({
                "id_election": id_election,
                "annee": parts[0],
                "type": parts[1],
                "tour": parts[2],
            })
        write_json(self._config.output_dir / "elections.json", elections)
        self._counts["elections.json"] = len(elections)

    # -- Communes --

    def _emit_communes(self, id_election: str, df: pd.DataFrame) -> None:
        for code_dept, group in df.groupby("code_departement"):
            records = to_records(group, null_columns=[], column_order=self._config.json_column_order)
            path = self._config.output_dir / "communes" / str(code_dept) / f"{id_election}.json"
            write_json(path, records)
            self._counts["communes"] += 1

    # -- Departements --

    def _aggregate_departements(self, df_communes: pd.DataFrame) -> pd.DataFrame:
        agg = (
            df_communes.groupby(
                ["code_region", "libelle_region", "code_departement", "libelle_departement"],
                as_index=False,
            )[list(self._config.numeric_columns)]
            .sum()
        )
        return compute_ratios(agg)

    def _emit_departements(self, id_election: str, df: pd.DataFrame) -> None:
        for code_region, group in df.groupby("code_region"):
            records = to_records(
                group,
                null_columns=["code_commune", "libelle_commune"],
                column_order=self._config.json_column_order,
            )
            path = self._config.output_dir / "departements" / str(code_region) / f"{id_election}.json"
            write_json(path, records)
            self._counts["departements"] += 1

    # -- Regions --

    def _aggregate_regions(self, df_dept: pd.DataFrame) -> pd.DataFrame:
        agg = (
            df_dept.groupby(
                ["code_region", "libelle_region"],
                as_index=False,
            )[list(self._config.numeric_columns)]
            .sum()
        )
        return compute_ratios(agg)

    def _emit_regions(self, id_election: str, df: pd.DataFrame) -> None:
        records = to_records(
            df,
            null_columns=[
                "code_departement", "libelle_departement",
                "code_commune", "libelle_commune",
            ],
            column_order=self._config.json_column_order,
        )
        path = self._config.output_dir / "regions" / f"{id_election}.json"
        write_json(path, records)
        self._counts["regions"] += 1


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


class Pipeline:
    """Orchestre le chargement par chunks, l'accumulation et l'emission."""

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self._config = config or PipelineConfig()

    def run(self) -> None:
        config = self._config

        print(f"Chargement du referentiel regions ({config.ref_file})...")
        region_lookup = RegionLookup(config)

        print(f"Lecture de {config.input_file} par chunks de {config.chunk_size} lignes...")
        reader = ChunkReader(config, region_lookup)
        accumulator = Accumulator(config)

        total_rows = 0
        for chunk in reader.iter_chunks():
            accumulator.ingest(chunk)
            total_rows += len(chunk)
            print(f"  {total_rows:>10,} lignes ingérées", end="\r")

        print(f"  {total_rows:>10,} lignes ingérées — {len(accumulator.election_ids())} elections")

        print("Emission des fichiers JSON...")
        emitter = JsonEmitter(config)
        emitter.emit_all(accumulator)
        emitter.report()

        print("Termine.")


# ---------------------------------------------------------------------------
# Point d'entree
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    Pipeline().run()
