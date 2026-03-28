import type { Election, ParticipationRecord } from "../types";
import type { ElectionDao } from "./dao";

const BASE = import.meta.env.BASE_URL + "data";

async function fetchJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(`${BASE}/${path}`, { signal });
  const contentType = res.headers.get("content-type") ?? "";
  if (!res.ok || !contentType.includes("application/json")) {
    throw new Error(`Données non disponibles : ${path}`);
  }
  return res.json();
}

export const staticDao: ElectionDao = {
  fetchElections: () => fetchJson<Election[]>("elections.json"),

  fetchRegions: (electionId, signal) =>
    fetchJson<ParticipationRecord[]>(`regions/${electionId}.json`, signal),

  fetchDepartements: (regionCode, electionId, signal) =>
    fetchJson<ParticipationRecord[]>(
      `departements/${regionCode}/${electionId}.json`,
      signal,
    ),

  fetchCommunes: (deptCode, electionId, signal) =>
    fetchJson<ParticipationRecord[]>(
      `communes/${deptCode}/${electionId}.json`,
      signal,
    ),
};
