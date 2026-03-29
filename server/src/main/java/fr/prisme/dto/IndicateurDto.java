package fr.prisme.dto;

import java.util.Map;

public record IndicateurDto(
        String id,
        String nom,
        String unite,
        Short annee,
        Map<String, Object> metadata) {
}
