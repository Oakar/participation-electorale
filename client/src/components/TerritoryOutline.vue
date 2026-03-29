<script setup lang="ts">
import { ref, onMounted } from "vue";
import type { Territory } from "../types";

const props = defineProps<{ territory: Territory }>();

const pathData = ref("");
const viewBox = ref("0 0 100 100");

function projectCoords(
  coords: number[][],
  lonMin: number,
  latMin: number,
  scaleX: number,
  scaleY: number,
  svgH: number,
): string {
  return coords
    .map((c, i) => {
      const x = (c[0] - lonMin) * scaleX;
      const y = svgH - (c[1] - latMin) * scaleY; // flip Y
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join("") + "Z";
}

function extractPaths(geometry: any, lonMin: number, latMin: number, scaleX: number, scaleY: number, svgH: number): string {
  const rings: number[][][] = [];
  if (geometry.type === "Polygon") {
    rings.push(...geometry.coordinates);
  } else if (geometry.type === "MultiPolygon") {
    for (const poly of geometry.coordinates) {
      rings.push(...poly);
    }
  }
  return rings.map((r) => projectCoords(r, lonMin, latMin, scaleX, scaleY, svgH)).join(" ");
}

onMounted(async () => {
  try {
    const res = await fetch("/api/geo/regions");
    const geo = await res.json();
    const codes = new Set(props.territory.regionCodes);
    const features = geo.features.filter(
      (f: any) => codes.has(f.properties?.code)
    );

    const [[latMin, lonMin], [latMax, lonMax]] = props.territory.bounds;
    const geoW = lonMax - lonMin;
    const geoH = latMax - latMin;

    // SVG dimensions proportional to geographic extent
    const baseSize = 200;
    let svgW: number, svgH: number;
    if (geoW >= geoH) {
      svgW = baseSize;
      svgH = baseSize * (geoH / geoW);
    } else {
      svgH = baseSize;
      svgW = baseSize * (geoW / geoH);
    }

    const scaleX = svgW / geoW;
    const scaleY = svgH / geoH;

    const pad = 5;
    viewBox.value = `${-pad} ${-pad} ${svgW + pad * 2} ${svgH + pad * 2}`;

    pathData.value = features
      .map((f: any) => extractPaths(f.geometry, lonMin, latMin, scaleX, scaleY, svgH))
      .join(" ");
  } catch {
    // Silently fail — outline is decorative
  }
});
</script>

<template>
  <svg :viewBox="viewBox" class="h-full w-full" preserveAspectRatio="xMidYMid meet">
    <path
      v-if="pathData"
      :d="pathData"
      fill="#e5e7eb"
      stroke="#9ca3af"
      stroke-width="0.8"
      stroke-linejoin="round"
    />
  </svg>
</template>
