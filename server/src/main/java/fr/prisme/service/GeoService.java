package fr.prisme.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import fr.prisme.repository.GeoRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
@Transactional(readOnly = true)
public class GeoService {

    private final GeoRepository geoRepository;
    private final ObjectMapper objectMapper;

    public GeoService(GeoRepository geoRepository, ObjectMapper objectMapper) {
        this.geoRepository = geoRepository;
        this.objectMapper = objectMapper;
    }

    public Map<String, Object> getRegions() {
        var rows = geoRepository.findAllRegions();
        return buildFeatureCollection(rows, List.of("code", "nom"));
    }

    public Map<String, Object> getDepartements() {
        var rows = geoRepository.findAllDepartements();
        return buildFeatureCollection(rows, List.of("code", "nom", "region_code"));
    }

    public Map<String, Object> getCommunesByDepartement(String deptCode) {
        var rows = geoRepository.findCommunesByDepartement(deptCode);
        return buildFeatureCollection(rows,
                List.of("code", "nom", "departement_code", "region_code", "epci"));
    }

    private Map<String, Object> buildFeatureCollection(List<Map<String, Object>> rows,
                                                        List<String> propertyKeys) {
        List<Map<String, Object>> features = new ArrayList<>(rows.size());

        for (Map<String, Object> row : rows) {
            Map<String, Object> properties = new LinkedHashMap<>();
            for (String key : propertyKeys) {
                Object val = row.get(key);
                if (val != null) {
                    properties.put(key, val);
                }
            }

            Object geometry;
            try {
                geometry = objectMapper.readValue((String) row.get("geom_json"), Map.class);
            } catch (JsonProcessingException e) {
                throw new RuntimeException("Invalid GeoJSON from PostGIS", e);
            }

            Map<String, Object> feature = new LinkedHashMap<>();
            feature.put("type", "Feature");
            feature.put("properties", properties);
            feature.put("geometry", geometry);
            features.add(feature);
        }

        Map<String, Object> fc = new LinkedHashMap<>();
        fc.put("type", "FeatureCollection");
        fc.put("features", features);
        return fc;
    }
}
