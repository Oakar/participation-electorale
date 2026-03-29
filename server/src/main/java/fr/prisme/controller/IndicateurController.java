package fr.prisme.controller;

import fr.prisme.dto.CategorieDto;
import fr.prisme.dto.IndicateurDto;
import fr.prisme.dto.ValeurTerritoireDto;
import fr.prisme.service.IndicateurService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api")
public class IndicateurController {

    private final IndicateurService indicateurService;

    public IndicateurController(IndicateurService indicateurService) {
        this.indicateurService = indicateurService;
    }

    @GetMapping("/categories")
    public List<CategorieDto> categories() {
        return indicateurService.getAllCategories();
    }

    @GetMapping("/categories/{catId}/indicateurs")
    public List<IndicateurDto> indicateursByCategorie(@PathVariable String catId) {
        return indicateurService.getIndicateursByCategorie(catId);
    }

    @GetMapping("/indicateurs/{indId}/regions")
    public ResponseEntity<List<ValeurTerritoireDto>> valeursByRegion(
            @PathVariable String indId) {
        var result = indicateurService.getValeursByRegion(indId);
        return result.isEmpty()
                ? ResponseEntity.notFound().build()
                : ResponseEntity.ok(result);
    }

    @GetMapping("/indicateurs/{indId}/regions/{regionCode}/departements")
    public ResponseEntity<List<ValeurTerritoireDto>> valeursByDepartement(
            @PathVariable String indId,
            @PathVariable String regionCode) {
        var result = indicateurService.getValeursByDepartement(indId, regionCode);
        return result.isEmpty()
                ? ResponseEntity.notFound().build()
                : ResponseEntity.ok(result);
    }

    @GetMapping("/indicateurs/{indId}/departements/{deptCode}/communes")
    public ResponseEntity<List<ValeurTerritoireDto>> valeursByCommune(
            @PathVariable String indId,
            @PathVariable String deptCode) {
        var result = indicateurService.getValeursByCommune(indId, deptCode);
        return result.isEmpty()
                ? ResponseEntity.notFound().build()
                : ResponseEntity.ok(result);
    }
}
