import type { Territory } from "./types";

export interface TerritoryGroup {
  label: string;
  territories: Territory[];
}

export const METROPOLE: Territory = {
  id: "metropole",
  label: "France métropolitaine",
  regionCodes: ["11", "24", "27", "28", "32", "44", "52", "53", "75", "76", "84", "93", "94"],
  bounds: [[41.3, -5.5], [51.2, 9.8]],
};

export const OUTREMER_GROUPS: TerritoryGroup[] = [
  {
    label: "Amérique",
    territories: [
      {
        id: "guadeloupe",
        label: "Guadeloupe",
        regionCodes: ["01"],
        bounds: [[15.8, -61.9], [16.55, -60.95]],
      },
      {
        id: "martinique",
        label: "Martinique",
        regionCodes: ["02"],
        bounds: [[14.35, -61.25], [14.9, -60.8]],
      },
      {
        id: "guyane",
        label: "Guyane",
        regionCodes: ["03"],
        bounds: [[2.1, -54.6], [5.8, -51.6]],
      },
      {
        id: "saint-pierre-et-miquelon",
        label: "Saint-Pierre-et-Miquelon",
        regionCodes: ["975"],
        bounds: [[46.7, -56.5], [47.2, -56.1]],
      },
    ],
  },
  {
    label: "Océan Indien",
    territories: [
      {
        id: "reunion",
        label: "La Réunion",
        regionCodes: ["04"],
        bounds: [[-21.4, 55.2], [-20.85, 55.85]],
      },
      {
        id: "mayotte",
        label: "Mayotte",
        regionCodes: ["06"],
        bounds: [[-13.05, 44.95], [-12.6, 45.35]],
      },
    ],
  },
  {
    label: "Océanie",
    territories: [
      {
        id: "polynesie-francaise",
        label: "Polynésie française",
        regionCodes: ["987"],
        bounds: [[-27.7, -154.8], [-7.8, -134.4]],
      },
      {
        id: "nouvelle-caledonie",
        label: "Nouvelle-Calédonie",
        regionCodes: ["988"],
        bounds: [[-22.8, 163.5], [-19.5, 168.2]],
      },
    ],
  },
];

/** All territories as a flat list */
export const TERRITORIES: Territory[] = [
  METROPOLE,
  ...OUTREMER_GROUPS.flatMap((g) => g.territories),
];
