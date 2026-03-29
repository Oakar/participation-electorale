<script setup lang="ts">
import { computed, watch } from "vue";
import { useAppState } from "../composables/useAppState";
import type { Indicateur } from "../types";

const ELECTION_TYPE_LABELS: Record<string, string> = {
  pres: "Présidentielle",
  legi: "Législatives",
  euro: "Européennes",
  muni: "Municipales",
  regi: "Régionales",
  cant: "Cantonales",
  dpmt: "Départementales",
};

const { categories, indicateurs, currentCategorieId, currentIndicateurId } =
  useAppState();

const isElectionCategory = computed(
  () => currentCategorieId.value === "elections",
);

interface IndicateurGroup {
  label: string;
  items: { id: string; label: string }[];
}

const groupedOptions = computed<IndicateurGroup[]>(() => {
  if (!isElectionCategory.value) {
    return [
      {
        label: "",
        items: indicateurs.value.map((i) => ({ id: i.id, label: i.nom })),
      },
    ];
  }

  const groups = new Map<string, Indicateur[]>();
  for (const ind of indicateurs.value) {
    const type = ind.metadata.type ?? "autre";
    if (!groups.has(type)) groups.set(type, []);
    groups.get(type)!.push(ind);
  }

  return [...groups.entries()].map(([type, list]) => ({
    label: ELECTION_TYPE_LABELS[type] ?? type,
    items: list.map((i) => ({
      id: i.id,
      label: `${i.annee} — Tour ${(i.metadata.tour ?? "").replace("t", "")}`,
    })),
  }));
});

watch(indicateurs, (list) => {
  if (list.length === 0) return;
  const currentValid = list.some((i) => i.id === currentIndicateurId.value);
  if (!currentValid) {
    currentIndicateurId.value = list[list.length - 1].id;
  }
});
</script>

<template>
  <div class="flex gap-2">
    <select
      v-if="categories.length > 1"
      :value="currentCategorieId"
      class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
      @change="currentCategorieId = ($event.target as HTMLSelectElement).value"
    >
      <option v-for="cat in categories" :key="cat.id" :value="cat.id">
        {{ cat.nom }}
      </option>
    </select>

    <select
      :value="currentIndicateurId"
      class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
      @change="currentIndicateurId = ($event.target as HTMLSelectElement).value"
    >
      <template v-for="group in groupedOptions" :key="group.label">
        <optgroup v-if="group.label" :label="group.label">
          <option v-for="item in group.items" :key="item.id" :value="item.id">
            {{ item.label }}
          </option>
        </optgroup>
        <template v-else>
          <option v-for="item in group.items" :key="item.id" :value="item.id">
            {{ item.label }}
          </option>
        </template>
      </template>
    </select>
  </div>
</template>
