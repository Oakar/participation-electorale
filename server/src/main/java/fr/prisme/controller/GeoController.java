package fr.prisme.controller;

import fr.prisme.service.GeoService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/geo")
public class GeoController {

    private final GeoService geoService;

    public GeoController(GeoService geoService) {
        this.geoService = geoService;
    }

    @GetMapping("/regions")
    public Map<String, Object> regions() {
        return geoService.getRegions();
    }

    @GetMapping("/departements")
    public Map<String, Object> departements() {
        return geoService.getDepartements();
    }

    @GetMapping("/communes/{deptCode}")
    public ResponseEntity<Map<String, Object>> communesByDepartement(
            @PathVariable String deptCode) {
        Map<String, Object> fc = geoService.getCommunesByDepartement(deptCode);
        @SuppressWarnings("unchecked")
        List<?> features = (List<?>) fc.get("features");
        if (features.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(fc);
    }
}
