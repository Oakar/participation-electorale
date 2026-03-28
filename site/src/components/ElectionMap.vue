<script setup lang="ts">
import { onMounted, onUnmounted, watch, ref, shallowRef } from "vue";
import { useRoute } from "vue-router";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useAppState } from "../composables/useAppState";
import { useElectionData } from "../composables/useElectionData";
import LoadingIndicator from "./LoadingIndicator.vue";
import ErrorBlock from "./ErrorBlock.vue";
import { participationColor } from "../utils/colors";
import { TERRITORIES } from "../territories";
import type { ParticipationRecord } from "../types";

const mapContainer = ref<HTMLElement | null>(null);
const map = shallowRef<L.Map | null>(null);
const geoLayer = shallowRef<L.GeoJSON | null>(null);
const layerIndex = new Map<string, L.Layer>();
const mapError = ref<string | null>(null);
let renderGeneration = 0;

const route = useRoute();
const { selectRegion, selectDepartement, hoveredCode, hoverFeature } = useAppState();
const { data, loading, error, retry } = useElectionData();

const geoCache = new Map<string, GeoJSON.FeatureCollection>();

class GeoNotFoundError extends Error {
  constructor() {
    super("Carte non disponible pour ce territoire");
    this.name = "GeoNotFoundError";
  }
}

async function fetchGeo(path: string): Promise<GeoJSON.FeatureCollection> {
  if (geoCache.has(path)) return geoCache.get(path)!;
  const res = await fetch(import.meta.env.BASE_URL + path);
  const contentType = res.headers.get("content-type") ?? "";
  if (!res.ok || !contentType.includes("json")) {
    throw new GeoNotFoundError();
  }
  const geo = await res.json();
  geoCache.set(path, geo);
  return geo;
}

function buildIndex(
  records: ParticipationRecord[],
  keyFn: (r: ParticipationRecord) => string | null
): Map<string, ParticipationRecord> {
  const idx = new Map<string, ParticipationRecord>();
  for (const r of records) {
    const k = keyFn(r);
    if (k) idx.set(k, r);
  }
  return idx;
}

function tooltipContent(name: string, record: ParticipationRecord | undefined): string {
  if (!record) return `<b>${name}</b><br>Pas de données`;
  const pct = record.inscrits > 0
    ? ((record.exprimes / record.inscrits) * 100).toFixed(1)
    : "—";
  return `<b>${name}</b><br>Participation : ${pct}%<br>Inscrits : ${record.inscrits.toLocaleString("fr-FR")}`;
}

async function renderLayer() {
  if (!map.value) return;

  const generation = ++renderGeneration;

  if (geoLayer.value) {
    map.value.removeLayer(geoLayer.value);
    geoLayer.value = null;
  }
  layerIndex.clear();
  previousHighlight = null;
  mapError.value = null;

  try {
    const records = data.value;
    const territoryId = route.params.territory as string | undefined;
    const regionCode = route.params.region as string | undefined;
    const deptCode = route.params.dept as string | undefined;
    const territory = TERRITORIES.find((t) => t.id === territoryId) ?? null;

    let geo: GeoJSON.FeatureCollection;
    let index: Map<string, ParticipationRecord>;
    let level: "regions" | "departements" | "communes";

    if (deptCode) {
      level = "communes";
      geo = await fetchGeo(`geo/communes/${deptCode}.geojson`);
      index = buildIndex(records, (r) => r.code_commune);
    } else if (regionCode) {
      level = "departements";
      const allDepts = await fetchGeo("geo/departements.geojson");
      const deptCodes = new Set(records.map((r) => r.code_departement));
      geo = {
        type: "FeatureCollection",
        features: allDepts.features.filter((f) => deptCodes.has(f.properties?.code)),
      };
      index = buildIndex(records, (r) => r.code_departement);
    } else if (territory) {
      level = "regions";
      const allRegions = await fetchGeo("geo/regions.geojson");
      const codes = new Set(territory.regionCodes);
      geo = {
        type: "FeatureCollection",
        features: allRegions.features.filter((f) => codes.has(f.properties?.code)),
      };
      index = buildIndex(records, (r) => r.code_region);
    } else {
      return;
    }

    if (generation !== renderGeneration) return;

    geoLayer.value = L.geoJSON(geo, {
      style: (feature) => {
        const code = feature?.properties?.code;
        const record = index.get(code);
        const fillColor =
          record && record.inscrits > 0
            ? participationColor(record.exprimes, record.inscrits)
            : "#ccc";
        return {
          fillColor,
          fillOpacity: 0.8,
          color: "#555",
          weight: 1,
          opacity: 0.6,
        };
      },
      onEachFeature: (feature, layer) => {
        const code = feature.properties?.code;
        const name = feature.properties?.nom ?? code;
        const record = index.get(code);

        layerIndex.set(code, layer);
        layer.bindTooltip(tooltipContent(name, record));

        layer.on("mouseover", () => hoverFeature(code));
        layer.on("mouseout", () => hoverFeature(null));

        layer.on("click", () => {
          if (level === "regions") {
            const rec = index.get(code);
            selectRegion(code, rec?.libelle_region ?? name);
          } else if (level === "departements") {
            const rec = index.get(code);
            selectDepartement(code, rec?.libelle_departement ?? name);
          }
        });
      },
    }).addTo(map.value);

    if (level === "regions" && territory) {
      map.value.fitBounds(territory.bounds, { padding: [20, 20] });
    } else {
      map.value.fitBounds(geoLayer.value.getBounds(), { padding: [20, 20] });
    }
  } catch (e) {
    if (generation !== renderGeneration) return;
    mapError.value = e instanceof Error ? e.message : "Erreur d'affichage de la carte";
  }
}

let previousHighlight: L.Layer | null = null;

function applyHighlight(code: string | null) {
  if (previousHighlight && geoLayer.value) {
    geoLayer.value.resetStyle(previousHighlight as L.Path);
    previousHighlight = null;
  }
  if (!code || !map.value) return;

  const layer = layerIndex.get(code) as L.Path | undefined;
  if (!layer) return;

  layer.setStyle({ weight: 3, color: "#1a73e8", fillOpacity: 0.9 });
  previousHighlight = layer;
}

onMounted(() => {
  if (!mapContainer.value) return;
  map.value = L.map(mapContainer.value, {
    center: [46.6, 2.5],
    zoom: 6,
    zoomControl: true,
  });
  setTimeout(() => {
    map.value?.invalidateSize();
    if (!loading.value && data.value.length > 0) {
      renderLayer();
    }
  }, 100);
});

onUnmounted(() => {
  if (map.value) {
    map.value.remove();
    map.value = null;
  }
  geoLayer.value = null;
  layerIndex.clear();
});

watch([data, loading], () => {
  if (!loading.value && map.value) {
    renderLayer();
  }
});

watch(hoveredCode, (code) => {
  applyHighlight(code);
});
</script>

<template>
  <div class="absolute inset-0">
    <LoadingIndicator v-if="loading" class="absolute left-1/2 top-1/2 z-1000 -translate-x-1/2 -translate-y-1/2 rounded-lg bg-white/90 px-6 py-3 font-semibold shadow" />
    <ErrorBlock v-else-if="error" :message="error" class="absolute left-1/2 top-1/2 z-1000 -translate-x-1/2 -translate-y-1/2 rounded-lg bg-white/95 px-6 py-4 shadow" @retry="retry" />
    <ErrorBlock v-else-if="mapError" :message="mapError" class="absolute left-1/2 top-1/2 z-1000 -translate-x-1/2 -translate-y-1/2 rounded-lg bg-white/95 px-6 py-4 shadow" @retry="renderLayer" />
    <div ref="mapContainer" class="h-full w-full bg-gray-100"></div>
  </div>
</template>
