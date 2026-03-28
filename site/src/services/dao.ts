import type { Election, ParticipationRecord } from "../types";

export interface ElectionDao {
  fetchElections(): Promise<Election[]>;
  fetchRegions(electionId: string, signal?: AbortSignal): Promise<ParticipationRecord[]>;
  fetchDepartements(regionCode: string, electionId: string, signal?: AbortSignal): Promise<ParticipationRecord[]>;
  fetchCommunes(deptCode: string, electionId: string, signal?: AbortSignal): Promise<ParticipationRecord[]>;
}
