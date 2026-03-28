<script setup lang="ts">
import { computed, watch } from "vue";
import { useAppState } from "../composables/useAppState";
import { useElectionData } from "../composables/useElectionData";
import LoadingIndicator from "./LoadingIndicator.vue";
import ErrorBlock from "./ErrorBlock.vue";

const {
  viewLevel,
  selectedTerritory,
  selectedRegion,
  selectedDepartement,
  hoveredCode,
  isBackNavigation,
  selectRegion,
  selectDepartement,
  hoverFeature,
  navigateTo,
} = useAppState();

const { data, loading, error, retry } = useElectionData();

const filteredData = computed(() => {
  if (viewLevel.value === "regions" && selectedTerritory.value) {
    const codes = new Set(selectedTerritory.value.regionCodes);
    return data.value.filter((r) => r.code_region && codes.has(r.code_region));
  }
  return data.value;
});

// Auto-skip levels with a single result (e.g. DOM-TOM where region = department)
watch(loading, (isLoading, wasLoading) => {
  if (isLoading || !wasLoading) return; // only react when loading finishes
  if (isBackNavigation.value) {
    isBackNavigation.value = false;
    return;
  }
  const level = viewLevel.value;
  if (level === "regions" && filteredData.value.length === 1) {
    const r = filteredData.value[0];
    selectRegion(r.code_region!, r.libelle_region!);
  } else if (level === "departements" && data.value.length === 1) {
    const r = data.value[0];
    selectDepartement(r.code_departement!, r.libelle_departement!);
  }
});
</script>

<template>
  <aside class="flex w-56 shrink-0 flex-col overflow-y-auto border-r border-gray-200 bg-white">
    <div class="border-b border-gray-100 px-4 py-3">
      <button
        class="flex cursor-pointer items-center gap-1 text-xs text-blue-600 hover:underline"
        @click="navigateTo('territoires')"
      >
        &larr; Territoires
      </button>
      <div class="mt-1 text-sm font-semibold text-gray-800">
        {{ selectedTerritory?.label }}
      </div>
    </div>

    <LoadingIndicator v-if="loading" class="px-4 py-6" />

    <ErrorBlock v-else-if="error" :message="error" class="px-4 py-6" @retry="retry" />

    <div v-else-if="viewLevel === 'regions'" class="flex flex-col py-1">
      <button
        v-for="record in filteredData"
        :key="record.code_region!"
        class="w-full cursor-pointer px-4 py-2 text-left text-sm transition-colors"
        :class="hoveredCode === record.code_region ? 'bg-blue-50 font-semibold text-blue-700' : 'text-gray-700 hover:bg-gray-50'"
        @click="selectRegion(record.code_region!, record.libelle_region!)"
        @mouseenter="hoverFeature(record.code_region!)"
        @mouseleave="hoverFeature(null)"
      >
        {{ record.libelle_region }}
      </button>
    </div>

    <div v-else-if="viewLevel === 'departements' && selectedRegion" class="flex flex-col py-1">
      <button
        class="flex cursor-pointer items-center gap-1 px-4 py-2 text-left text-sm font-semibold text-blue-600 hover:bg-gray-50"
        @click="navigateTo('regions')"
      >
        &larr; {{ selectedRegion.libelle }}
      </button>
      <button
        v-for="record in data"
        :key="record.code_departement!"
        class="w-full cursor-pointer px-4 py-2 text-left text-sm transition-colors"
        :class="hoveredCode === record.code_departement ? 'bg-blue-50 font-semibold text-blue-700' : 'text-gray-700 hover:bg-gray-50'"
        @click="selectDepartement(record.code_departement!, record.libelle_departement!)"
        @mouseenter="hoverFeature(record.code_departement!)"
        @mouseleave="hoverFeature(null)"
      >
        {{ record.libelle_departement }}
      </button>
    </div>

    <div v-else-if="viewLevel === 'communes' && selectedDepartement" class="flex flex-col py-1">
      <button
        class="flex cursor-pointer items-center gap-1 px-4 py-2 text-left text-sm font-semibold text-blue-600 hover:bg-gray-50"
        @click="navigateTo('departements')"
      >
        &larr; {{ selectedDepartement.libelle }}
      </button>
      <div class="px-4 pb-1 pl-4 text-xs text-gray-400">
        {{ data.length }} communes
      </div>
      <button
        v-for="record in data"
        :key="record.code_commune!"
        class="w-full cursor-pointer px-4 py-1 text-left text-xs transition-colors"
        :class="hoveredCode === record.code_commune ? 'bg-blue-50 font-semibold text-blue-700' : 'text-gray-600 hover:bg-gray-50'"
        @mouseenter="hoverFeature(record.code_commune!)"
        @mouseleave="hoverFeature(null)"
      >
        {{ record.libelle_commune }}
      </button>
    </div>
  </aside>
</template>
