export interface Categorie {
  id: string;
  nom: string;
}

export interface Indicateur {
  id: string;
  nom: string;
  unite: string;
  annee: number;
  metadata: Record<string, string>;
}

export interface ValeurTerritoire {
  code: string;
  libelle: string;
  valeur: number;
  details: Record<string, number>;
}

export type ViewLevel = "territoires" | "regions" | "departements" | "communes";

export interface Territory {
  id: string;
  label: string;
  regionCodes: string[];
  bounds: [[number, number], [number, number]];
}
