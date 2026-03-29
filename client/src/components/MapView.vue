<script setup lang="ts">
import TerritorySidebar from "./TerritorySidebar.vue";
import ElectionMap from "./ElectionMap.vue";
import MapLegend from "./MapLegend.vue";
</script>

<template>
  <TerritorySidebar />
  <div class="relative flex-1">
    <ElectionMap />
    <MapLegend />
  </div>
</template>
