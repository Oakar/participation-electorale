<script setup lang="ts">
import { onMounted, onUnmounted, watch, ref, shallowRef } from "vue";
import { useRoute } from "vue-router";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useAppState } from "../composables/useAppState";
import { useIndicateurData } from "../composables/useIndicateurData";
import LoadingIndicator from "./LoadingIndicator.vue";
import ErrorBlock from "./ErrorBlock.vue";
import { ratioColor } from "../utils/colors";
import { TERRITORIES } from "../territories";
import type { ValeurTerritoire } from "../types";

const mapContainer = ref<HTMLElement | null>(null);
const map = shallowRef<L.Map | null>(null);
const geoLayer = shallowRef<L.GeoJSON | null>(null);
const labelLayer = shallowRef<L.LayerGroup | null>(null);
const layerIndex = new Map<string, L.Layer>();
const mapError = ref<string | null>(null);
let renderGeneration = 0;

const route = useRoute();
const { selectRegion, selectDepartement, hoveredCode, hoverFeature, currentIndicateur } = useAppState();
const { data, loading, error, retry } = useIndicateurData();

const geoCache = new Map<string, GeoJSON.FeatureCollection>();

class GeoNotFoundError extends Error {
  constructor() {
    super("Carte non disponible pour ce territoire");
    this.name = "GeoNotFoundError";
  }
}

async function fetchGeo(path: string): Promise<GeoJSON.FeatureCollection> {
  if (geoCache.has(path)) return geoCache.get(path)!;
  const res = await fetch(path);
  if (!res.ok) {
    throw new GeoNotFoundError();
  }
  const geo = await res.json();
  geoCache.set(path, geo);
  return geo;
}

function buildIndex(records: ValeurTerritoire[]): Map<string, ValeurTerritoire> {
  const idx = new Map<string, ValeurTerritoire>();
  for (const r of records) idx.set(r.code, r);
  return idx;
}

function tooltipContent(name: string, record: ValeurTerritoire | undefined): string {
  if (!record) return `<b>${name}</b><br>Pas de données`;
  const unite = currentIndicateur.value?.unite ?? "";
  const formatted = unite === "%"
    ? `${(record.valeur * 100).toFixed(1)}%`
    : `${record.valeur.toLocaleString("fr-FR")} ${unite}`;
  return `<b>${name}</b><br>${formatted}`;
}

async function renderLayer() {
  if (!map.value) return;

  const generation = ++renderGeneration;

  if (geoLayer.value) {
    map.value.removeLayer(geoLayer.value);
    geoLayer.value = null;
  }
  if (labelLayer.value) {
    map.value.removeLayer(labelLayer.value);
    labelLayer.value = null;
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
    let index: Map<string, ValeurTerritoire>;
    let level: "regions" | "departements" | "communes";

    if (deptCode) {
      level = "communes";
      geo = await fetchGeo(`/api/geo/communes/${deptCode}`);
      index = buildIndex(records);
    } else if (regionCode) {
      level = "departements";
      const allDepts = await fetchGeo("/api/geo/departements");
      const deptCodes = new Set(records.map((r) => r.code));
      geo = {
        type: "FeatureCollection",
        features: allDepts.features.filter((f) => deptCodes.has(f.properties?.code)),
      };
      index = buildIndex(records);
    } else if (territory) {
      level = "regions";
      const allRegions = await fetchGeo("/api/geo/regions");
      const codes = new Set(territory.regionCodes);
      geo = {
        type: "FeatureCollection",
        features: allRegions.features.filter((f) => codes.has(f.properties?.code)),
      };
      index = buildIndex(records);
    } else {
      return;
    }

    if (generation !== renderGeneration) return;

    geoLayer.value = L.geoJSON(geo, {
      style: (feature) => {
        const code = feature?.properties?.code;
        const record = index.get(code);
        const fillColor = record ? ratioColor(record.valeur) : "#ccc";
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

        // Tooltip uniquement pour les communes
        if (level === "communes") {
          layer.bindTooltip(tooltipContent(name, record));
        }

        layer.on("mouseover", () => hoverFeature(code));
        layer.on("mouseout", () => hoverFeature(null));

        layer.on("click", () => {
          if (level === "regions") {
            const rec = index.get(code);
            selectRegion(code, rec?.libelle ?? name);
          } else if (level === "departements") {
            const rec = index.get(code);
            selectDepartement(code, rec?.libelle ?? name);
          }
        });
      },
    }).addTo(map.value);

    // Labels fixes avec le taux pour régions et départements
    if (level !== "communes") {
      const unite = currentIndicateur.value?.unite ?? "";
      const markers: L.Marker[] = [];
      geoLayer.value.eachLayer((layer) => {
        const feature = (layer as L.GeoJSON).feature as GeoJSON.Feature;
        const code = feature.properties?.code;
        const record = index.get(code);
        if (!record) return;

        const label = unite === "%"
          ? `${(record.valeur * 100).toFixed(1)}%`
          : `${record.valeur.toLocaleString("fr-FR")}`;
        const bounds = (layer as L.Polygon).getBounds();
        const center = bounds.getCenter();

        const icon = L.divIcon({
          className: "participation-label",
          html: `<span>${label}</span>`,
          iconSize: [50, 20],
          iconAnchor: [25, 10],
        });
        markers.push(L.marker(center, { icon, interactive: false }));
      });
      labelLayer.value = L.layerGroup(markers).addTo(map.value);
    }

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
  labelLayer.value = null;
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
