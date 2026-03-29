-- Index sur les clés étrangères
CREATE INDEX idx_indicateur_categorie ON indicateur(categorie_id);
CREATE INDEX idx_valeur_indicateur ON indicateur_valeur(indicateur_id);
CREATE INDEX idx_valeur_commune ON indicateur_valeur(code_commune);
CREATE INDEX idx_valeur_departement ON indicateur_valeur(code_departement);
CREATE INDEX idx_valeur_region ON indicateur_valeur(code_region);

-- Index composite pour la requête la plus fréquente
CREATE INDEX idx_valeur_indicateur_commune ON indicateur_valeur(indicateur_id, code_commune);

-- Index sur les FK géographiques
CREATE INDEX idx_departement_region ON departement(region_code);
CREATE INDEX idx_commune_departement ON commune(departement_code);
CREATE INDEX idx_commune_region ON commune(region_code);

-- Index spatiaux GIST
CREATE INDEX idx_region_geom ON region USING GIST(geom);
CREATE INDEX idx_departement_geom ON departement USING GIST(geom);
CREATE INDEX idx_commune_geom ON commune USING GIST(geom);
