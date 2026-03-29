package fr.prisme.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "commune")
public class Commune {

    @Id
    @Column(name = "code", length = 5)
    private String code;

    @Column(name = "nom", length = 100, nullable = false)
    private String nom;

    @Column(name = "departement_code", length = 3, nullable = false, insertable = false, updatable = false)
    private String departementCode;

    @Column(name = "region_code", length = 3, nullable = false, insertable = false, updatable = false)
    private String regionCode;

    @Column(name = "epci", length = 20)
    private String epci;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "departement_code", nullable = false)
    private Departement departement;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "region_code", nullable = false)
    private Region region;

    protected Commune() {
    }

    public String getCode() {
        return code;
    }

    public String getNom() {
        return nom;
    }

    public String getDepartementCode() {
        return departementCode;
    }

    public String getRegionCode() {
        return regionCode;
    }

    public String getEpci() {
        return epci;
    }

    public Departement getDepartement() {
        return departement;
    }

    public Region getRegion() {
        return region;
    }
}
