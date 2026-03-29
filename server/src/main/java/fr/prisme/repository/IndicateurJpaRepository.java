package fr.prisme.repository;

import fr.prisme.entity.Indicateur;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface IndicateurJpaRepository
        extends JpaRepository<Indicateur, String> {

    List<Indicateur> findByCategorieIdOrderByAnneeAscIdAsc(String categorieId);
}
