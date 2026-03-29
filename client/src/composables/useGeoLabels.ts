import { reactive } from "vue";
import type { ValeurTerritoire } from "../types";

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

  function storeFromRecords(records: ValeurTerritoire[]) {
    for (const r of records) {
      store(r.code, r.libelle);
    }
  }

  return { get, store, storeFromRecords };
}
