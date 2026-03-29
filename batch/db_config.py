"""Configuration de connexion a la base PostGIS."""

import os

DB_HOST = os.getenv("DB_HOST", "prisme-postgis")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "prisme")
DB_USER = os.getenv("DB_USER", "prisme")
DB_PASSWORD = os.getenv("DB_PASSWORD", "prisme")


def get_connection_string() -> str:
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_psycopg2_params() -> dict:
    return {
        "host": DB_HOST,
        "port": DB_PORT,
        "dbname": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
    }
