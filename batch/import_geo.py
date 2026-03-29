"""
Charge les GeoJSON (regions, departements, communes) dans PostGIS.

Usage:
    python batch/import_geo.py
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
from shapely.geometry import MultiPolygon
from sqlalchemy import create_engine, text

from db_config import get_connection_string

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "geo"


def ensure_multipolygon(geom):
    """Convertit un Polygon en MultiPolygon si necessaire."""
    if geom is None:
        return None
    if geom.geom_type == "Polygon":
        return MultiPolygon([geom])
    return geom


def load_regions(engine) -> None:
    path = DATA_DIR / "regions.geojson"
    print(f"  Lecture de {path}...")
    gdf = gpd.read_file(path)
    gdf = gdf.rename(columns={"code": "code", "nom": "nom"})
    gdf = gdf[["code", "nom", "geometry"]]
    gdf["geometry"] = gdf["geometry"].apply(ensure_multipolygon)
    gdf = gdf.set_geometry("geometry")
    gdf = gdf.set_crs(epsg=4326, allow_override=True)
    gdf.rename_geometry("geom").to_postgis("region", engine, if_exists="append", index=False)
    print(f"  {len(gdf)} regions chargees.")


def load_departements(engine) -> None:
    path = DATA_DIR / "departements.geojson"
    print(f"  Lecture de {path}...")
    gdf = gpd.read_file(path)
    gdf = gdf.rename(columns={"region": "region_code"})
    gdf = gdf[["code", "nom", "region_code", "geometry"]]
    gdf["geometry"] = gdf["geometry"].apply(ensure_multipolygon)
    gdf = gdf.set_geometry("geometry")
    gdf = gdf.set_crs(epsg=4326, allow_override=True)
    gdf.rename_geometry("geom").to_postgis("departement", engine, if_exists="append", index=False)
    print(f"  {len(gdf)} departements charges.")


def load_communes(engine) -> None:
    communes_dir = DATA_DIR / "communes"
    files = sorted(communes_dir.glob("*.geojson"))
    print(f"  {len(files)} fichiers communes trouves.")
    seen_codes: set[str] = set()
    total = 0
    for f in files:
        gdf = gpd.read_file(f)
        gdf = gdf.rename(columns={
            "departement": "departement_code",
            "region": "region_code",
            "codeDepartement": "departement_code",
            "codeRegion": "region_code",
        })
        if "epci" not in gdf.columns:
            gdf["epci"] = None
        gdf = gdf[["code", "nom", "departement_code", "region_code", "epci", "geometry"]]
        # Ignorer les doublons (ex: 97.geojson vs 975.geojson)
        gdf = gdf[~gdf["code"].isin(seen_codes)]
        if gdf.empty:
            continue
        seen_codes.update(gdf["code"].tolist())
        gdf["geometry"] = gdf["geometry"].apply(ensure_multipolygon)
        gdf = gdf.set_geometry("geometry")
        gdf = gdf.set_crs(epsg=4326, allow_override=True)
        gdf.rename_geometry("geom").to_postgis("commune", engine, if_exists="append", index=False)
        total += len(gdf)
        print(f"    {f.stem}: {len(gdf)} communes", end="\r")
    print(f"  {total} communes chargees.                    ")


def truncate_geo_tables(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE commune, departement, region CASCADE"))
    print("  Tables geo videes (truncate cascade).")


def run() -> None:
    print("=== Import des donnees geographiques ===")
    engine = create_engine(get_connection_string())
    truncate_geo_tables(engine)
    load_regions(engine)
    load_departements(engine)
    load_communes(engine)
    engine.dispose()
    print("=== Import geo termine ===\n")


if __name__ == "__main__":
    run()
