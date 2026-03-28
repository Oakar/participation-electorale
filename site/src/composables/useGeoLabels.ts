import { reactive } from "vue";

/**
 * Cache code → libelle, rempli au fur et a mesure que les donnees sont chargees.
 * Permet au breadcrumb et a la sidebar d'afficher les noms sans attendre un fetch.
 */
const labels = reactive(new Map<string, string>());

export function useGeoLabels() {
  function store(code: string | null, libelle: string | null) {
    if (code && libelle) labels.set(code, libelle);
  }

  function get(code: string): string {
    return labels.get(code) ?? code;
  }

  function storeFromRecords(records: { code_region?: string | null; libelle_region?: string | null; code_departement?: string | null; libelle_departement?: string | null }[]) {
    for (const r of records) {
      store(r.code_region ?? null, r.libelle_region ?? null);
      store(r.code_departement ?? null, r.libelle_departement ?? null);
    }
  }

  return { get, store, storeFromRecords };
}
