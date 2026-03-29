package fr.prisme.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import fr.prisme.dto.CategorieDto;
import fr.prisme.dto.IndicateurDto;
import fr.prisme.dto.ValeurTerritoireDto;
import fr.prisme.repository.CategorieIndicateurRepository;
import fr.prisme.repository.IndicateurJpaRepository;
import fr.prisme.repository.IndicateurValeurRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Map;

@Service
@Transactional(readOnly = true)
public class IndicateurService {

    private final CategorieIndicateurRepository categorieRepo;
    private final IndicateurJpaRepository indicateurRepo;
    private final IndicateurValeurRepository valeurRepo;
    private final ObjectMapper objectMapper;

    public IndicateurService(CategorieIndicateurRepository categorieRepo,
                             IndicateurJpaRepository indicateurRepo,
                             IndicateurValeurRepository valeurRepo,
                             ObjectMapper objectMapper) {
        this.categorieRepo = categorieRepo;
        this.indicateurRepo = indicateurRepo;
        this.valeurRepo = valeurRepo;
        this.objectMapper = objectMapper;
    }

    public List<CategorieDto> getAllCategories() {
        return categorieRepo.findAll().stream()
                .map(e -> new CategorieDto(e.getId(), e.getNom()))
                .toList();
    }

    public List<IndicateurDto> getIndicateursByCategorie(String categorieId) {
        return indicateurRepo.findByCategorieIdOrderByAnneeAscIdAsc(categorieId).stream()
                .map(e -> new IndicateurDto(
                        e.getId(), e.getNom(), e.getUnite(), e.getAnnee(), e.getMetadata()))
                .toList();
    }

    public List<ValeurTerritoireDto> getValeursByRegion(String indicateurId) {
        checkIndicateurExists(indicateurId);
        return valeurRepo.findRegions(indicateurId).stream()
                .map(this::toValeurDto)
                .toList();
    }

    public List<ValeurTerritoireDto> getValeursByDepartement(
            String indicateurId, String regionCode) {
        checkIndicateurExists(indicateurId);
        return valeurRepo.findDepartementsByRegion(indicateurId, regionCode).stream()
                .map(this::toValeurDto)
                .toList();
    }

    public List<ValeurTerritoireDto> getValeursByCommune(
            String indicateurId, String departementCode) {
        checkIndicateurExists(indicateurId);
        return valeurRepo.findCommunesByDepartement(indicateurId, departementCode).stream()
                .map(this::toValeurDto)
                .toList();
    }

    private void checkIndicateurExists(String indicateurId) {
        if (!indicateurRepo.existsById(indicateurId)) {
            throw new ResponseStatusException(
                    HttpStatus.NOT_FOUND, "Indicateur not found: " + indicateurId);
        }
    }

    private ValeurTerritoireDto toValeurDto(Map<String, Object> row) {
        return new ValeurTerritoireDto(
                (String) row.get("code"),
                (String) row.get("libelle"),
                row.get("valeur") != null ? ((Number) row.get("valeur")).doubleValue() : null,
                parseDetails(row.get("details")));
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> parseDetails(Object raw) {
        if (raw == null) {
            return null;
        }
        try {
            return objectMapper.readValue(raw.toString(), Map.class);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Invalid JSON in details column", e);
        }
    }
}
