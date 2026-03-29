package fr.prisme.repository;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Map;

@Repository
public class IndicateurValeurRepository {

    private static final String DETAILS_AGG_SUM = """
            jsonb_build_object(
                'inscrits',    SUM((iv.details->>'inscrits')::bigint),
                'abstentions', SUM((iv.details->>'abstentions')::bigint),
                'votants',     SUM((iv.details->>'votants')::bigint),
                'blancs',      SUM((iv.details->>'blancs')::bigint),
                'nuls',        SUM((iv.details->>'nuls')::bigint),
                'exprimes',    SUM((iv.details->>'exprimes')::bigint)
            )""";

    private static final String VALEUR_AGG_SUM = """
            SUM((iv.details->>'exprimes')::double precision)
              / NULLIF(SUM((iv.details->>'inscrits')::double precision), 0)""";

    private final JdbcClient jdbc;

    public IndicateurValeurRepository(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    public List<Map<String, Object>> findRegions(String indicateurId) {
        return jdbc.sql("""
                SELECT c.region_code AS code,
                       r.nom AS libelle,
                       %s AS valeur,
                       %s AS details
                  FROM indicateur_valeur iv
                  JOIN commune c ON c.code = iv.code_commune
                  JOIN region r ON r.code = c.region_code
                 WHERE iv.indicateur_id = :indicateurId
                 GROUP BY c.region_code, r.nom
                 ORDER BY c.region_code
                """.formatted(VALEUR_AGG_SUM, DETAILS_AGG_SUM))
            .param("indicateurId", indicateurId)
            .query()
            .listOfRows();
    }

    public List<Map<String, Object>> findDepartementsByRegion(
            String indicateurId, String regionCode) {
        return jdbc.sql("""
                SELECT c.departement_code AS code,
                       d.nom AS libelle,
                       %s AS valeur,
                       %s AS details
                  FROM indicateur_valeur iv
                  JOIN commune c ON c.code = iv.code_commune
                  JOIN departement d ON d.code = c.departement_code
                 WHERE iv.indicateur_id = :indicateurId
                   AND c.region_code = :regionCode
                 GROUP BY c.departement_code, d.nom
                 ORDER BY c.departement_code
                """.formatted(VALEUR_AGG_SUM, DETAILS_AGG_SUM))
            .param("indicateurId", indicateurId)
            .param("regionCode", regionCode)
            .query()
            .listOfRows();
    }

    public List<Map<String, Object>> findCommunesByDepartement(
            String indicateurId, String departementCode) {
        return jdbc.sql("""
                SELECT iv.code_commune AS code,
                       c.nom AS libelle,
                       iv.valeur,
                       iv.details
                  FROM indicateur_valeur iv
                  JOIN commune c ON c.code = iv.code_commune
                 WHERE iv.indicateur_id = :indicateurId
                   AND c.departement_code = :departementCode
                 ORDER BY c.code
                """)
            .param("indicateurId", indicateurId)
            .param("departementCode", departementCode)
            .query()
            .listOfRows();
    }
}
