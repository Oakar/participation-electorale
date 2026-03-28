export interface Election {
  id_election: string;
  annee: string;
  type: string;
  tour: string;
}

export interface ParticipationRecord {
  code_region: string | null;
  libelle_region: string | null;
  code_departement: string | null;
  libelle_departement: string | null;
  code_commune: string | null;
  libelle_commune: string | null;
  inscrits: number;
  abstentions: number;
  votants: number;
  blancs: number;
  nuls: number;
  exprimes: number;
  ratio_abstentions_inscrits: number;
  ratio_votants_inscrits: number;
  ratio_exprimes_votants: number;
}

export type ViewLevel = "territoires" | "regions" | "departements" | "communes";

export interface Territory {
  id: string;
  label: string;
  regionCodes: string[];
  bounds: [[number, number], [number, number]];
}

export interface AppState {
  currentElection: string;
  viewLevel: ViewLevel;
  selectedTerritory: Territory | null;
  selectedRegion: { code: string; libelle: string } | null;
  selectedDepartement: { code: string; libelle: string } | null;
}

export const ELECTION_TYPE_LABELS: Record<string, string> = {
  pres: "Présidentielle",
  legi: "Législatives",
  euro: "Européennes",
  muni: "Municipales",
  regi: "Régionales",
  cant: "Cantonales",
  dpmt: "Départementales",
};
