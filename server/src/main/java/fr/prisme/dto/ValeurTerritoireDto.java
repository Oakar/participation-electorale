package fr.prisme.dto;

import java.util.Map;

public record ValeurTerritoireDto(
        String code,
        String libelle,
        Double valeur,
        Map<String, Object> details) {
}
