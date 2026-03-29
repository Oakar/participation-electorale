package fr.prisme.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.util.Map;

@Entity
@Table(name = "indicateur")
public class Indicateur {

    @Id
    @Column(name = "id", length = 50)
    private String id;

    @Column(name = "categorie_id", length = 20, nullable = false,
            insertable = false, updatable = false)
    private String categorieId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "categorie_id", nullable = false)
    private CategorieIndicateur categorie;

    @Column(name = "nom", length = 200, nullable = false)
    private String nom;

    @Column(name = "unite", length = 20)
    private String unite;

    @Column(name = "annee")
    private Short annee;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "metadata", columnDefinition = "jsonb")
    private Map<String, Object> metadata;

    protected Indicateur() {
    }

    public String getId() {
        return id;
    }

    public String getCategorieId() {
        return categorieId;
    }

    public CategorieIndicateur getCategorie() {
        return categorie;
    }

    public String getNom() {
        return nom;
    }

    public String getUnite() {
        return unite;
    }

    public Short getAnnee() {
        return annee;
    }

    public Map<String, Object> getMetadata() {
        return metadata;
    }
}
