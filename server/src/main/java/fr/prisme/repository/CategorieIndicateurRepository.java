package fr.prisme.repository;

import fr.prisme.entity.CategorieIndicateur;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CategorieIndicateurRepository
        extends JpaRepository<CategorieIndicateur, String> {
}
