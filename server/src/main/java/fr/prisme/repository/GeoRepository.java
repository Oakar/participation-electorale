package fr.prisme.repository;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Map;

@Repository
public class GeoRepository {

    private final JdbcClient jdbc;

    public GeoRepository(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    public List<Map<String, Object>> findAllRegions() {
        return jdbc.sql("""
                SELECT code, nom, ST_AsGeoJSON(geom) AS geom_json
                FROM region
                ORDER BY code
                """)
            .query()
            .listOfRows();
    }

    public List<Map<String, Object>> findAllDepartements() {
        return jdbc.sql("""
                SELECT code, nom, region_code, ST_AsGeoJSON(geom) AS geom_json
                FROM departement
                ORDER BY code
                """)
            .query()
            .listOfRows();
    }

    public List<Map<String, Object>> findCommunesByDepartement(String deptCode) {
        return jdbc.sql("""
                SELECT code, nom, departement_code, region_code, epci,
                       ST_AsGeoJSON(geom) AS geom_json
                FROM commune
                WHERE departement_code = :deptCode
                ORDER BY code
                """)
            .param("deptCode", deptCode)
            .query()
            .listOfRows();
    }
}
