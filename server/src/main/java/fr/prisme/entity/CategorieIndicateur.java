package fr.prisme.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "categorie_indicateur")
public class CategorieIndicateur {

    @Id
    @Column(name = "id", length = 20)
    private String id;

    @Column(name = "nom", length = 100, nullable = false)
    private String nom;

    protected CategorieIndicateur() {
    }

    public String getId() {
        return id;
    }

    public String getNom() {
        return nom;
    }
}
