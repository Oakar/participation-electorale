package fr.prisme.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "region")
public class Region {

    @Id
    @Column(name = "code", length = 3)
    private String code;

    @Column(name = "nom", length = 100, nullable = false)
    private String nom;

    protected Region() {
    }

    public String getCode() {
        return code;
    }

    public String getNom() {
        return nom;
    }
}
