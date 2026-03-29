package fr.prisme.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "departement")
public class Departement {

    @Id
    @Column(name = "code", length = 3)
    private String code;

    @Column(name = "nom", length = 100, nullable = false)
    private String nom;

    @Column(name = "region_code", length = 3, nullable = false, insertable = false, updatable = false)
    private String regionCode;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "region_code", nullable = false)
    private Region region;

    protected Departement() {
    }

    public String getCode() {
        return code;
    }

    public String getNom() {
        return nom;
    }

    public String getRegionCode() {
        return regionCode;
    }

    public Region getRegion() {
        return region;
    }
}
