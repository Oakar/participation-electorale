import type { Categorie, Indicateur, ValeurTerritoire } from "../types";

export interface IndicateurDao {
  fetchCategories(): Promise<Categorie[]>;
  fetchIndicateurs(categorieId: string): Promise<Indicateur[]>;
  fetchRegions(indicateurId: string, signal?: AbortSignal): Promise<ValeurTerritoire[]>;
  fetchDepartements(indicateurId: string, regionCode: string, signal?: AbortSignal): Promise<ValeurTerritoire[]>;
  fetchCommunes(indicateurId: string, deptCode: string, signal?: AbortSignal): Promise<ValeurTerritoire[]>;
}
