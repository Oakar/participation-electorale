import type { Categorie, Indicateur, ValeurTerritoire } from "../types";
import type { IndicateurDao } from "./dao";

async function fetchApi<T>(path: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(`/api${path}`, { signal });
  if (!res.ok) {
    throw new Error(`Erreur API : ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const apiDao: IndicateurDao = {
  fetchCategories: () => fetchApi<Categorie[]>("/categories"),

  fetchIndicateurs: (catId) =>
    fetchApi<Indicateur[]>(`/categories/${catId}/indicateurs`),

  fetchRegions: (indId, signal) =>
    fetchApi<ValeurTerritoire[]>(`/indicateurs/${indId}/regions`, signal),

  fetchDepartements: (indId, regionCode, signal) =>
    fetchApi<ValeurTerritoire[]>(
      `/indicateurs/${indId}/regions/${regionCode}/departements`,
      signal,
    ),

  fetchCommunes: (indId, deptCode, signal) =>
    fetchApi<ValeurTerritoire[]>(
      `/indicateurs/${indId}/departements/${deptCode}/communes`,
      signal,
    ),
};
