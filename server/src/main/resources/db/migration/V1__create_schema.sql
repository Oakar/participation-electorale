CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE region (
    code VARCHAR(3) PRIMARY KEY,
    nom  VARCHAR(100) NOT NULL,
    geom geometry(MultiPolygon, 4326) NOT NULL
);

CREATE TABLE departement (
    code        VARCHAR(3) PRIMARY KEY,
    nom         VARCHAR(100) NOT NULL,
    region_code VARCHAR(3) NOT NULL REFERENCES region(code),
    geom        geometry(MultiPolygon, 4326) NOT NULL
);

CREATE TABLE commune (
    code             VARCHAR(5) PRIMARY KEY,
    nom              VARCHAR(100) NOT NULL,
    departement_code VARCHAR(3) NOT NULL REFERENCES departement(code),
    region_code      VARCHAR(3) NOT NULL REFERENCES region(code),
    epci             VARCHAR(20),
    geom             geometry(MultiPolygon, 4326) NOT NULL
);

CREATE TABLE categorie_indicateur (
    id  VARCHAR(20) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL
);

CREATE TABLE indicateur (
    id           VARCHAR(50) PRIMARY KEY,
    categorie_id VARCHAR(20) NOT NULL REFERENCES categorie_indicateur(id),
    nom          VARCHAR(200) NOT NULL,
    unite        VARCHAR(20),
    annee        SMALLINT,
    metadata     JSONB
);

CREATE TABLE indicateur_valeur (
    id               BIGSERIAL PRIMARY KEY,
    indicateur_id    VARCHAR(50) NOT NULL REFERENCES indicateur(id),
    code_region      VARCHAR(3) REFERENCES region(code),
    code_departement VARCHAR(3) REFERENCES departement(code),
    code_commune     VARCHAR(5) REFERENCES commune(code),
    valeur           DOUBLE PRECISION NOT NULL,
    details          JSONB,
    CONSTRAINT chk_territoire CHECK (
        (code_commune IS NOT NULL) OR
        (code_departement IS NOT NULL) OR
        (code_region IS NOT NULL)
    )
);
