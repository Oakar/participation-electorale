<script setup lang="ts">
import { ref, watch } from "vue";
import { useAppState } from "../composables/useAppState";

const { elections, electionTypes, electionsForType, currentElectionId } = useAppState();

const selectedType = ref("");
const availableElections = ref<{ id: string; label: string }[]>([]);

watch(selectedType, (type) => {
  const list = electionsForType(type).map((e) => ({
    id: e.id_election,
    label: `${e.annee} — Tour ${e.tour.replace("t", "")}`,
  }));
  availableElections.value = list;
  const currentStillValid = list.some((e) => e.id === currentElectionId.value);
  if (!currentStillValid && list.length > 0) {
    currentElectionId.value = list[list.length - 1].id;
  }
});

watch(electionTypes, (types) => {
  if (types.length === 0) return;
  if (!selectedType.value) {
    const match = currentElectionId.value
      ? elections.value.find((e) => e.id_election === currentElectionId.value)
      : null;
    if (match && types.some((t) => t.value === match.type)) {
      selectedType.value = match.type;
    } else {
      selectedType.value = types[0].value;
    }
  }
}, { immediate: true });
</script>

<template>
  <div class="flex gap-2">
    <select
      v-model="selectedType"
      class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
    >
      <option v-for="t in electionTypes" :key="t.value" :value="t.value">
        {{ t.label }}
      </option>
    </select>
    <select
      v-model="currentElectionId"
      class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
    >
      <option v-for="e in availableElections" :key="e.id" :value="e.id">
        {{ e.label }}
      </option>
    </select>
  </div>
</template>
