<script setup lang="ts">
import { useAppState } from "../composables/useAppState";
import { METROPOLE, OUTREMER_GROUPS } from "../territories";
import type { Territory } from "../types";
import TerritoryOutline from "./TerritoryOutline.vue";

const { selectTerritory } = useAppState();

function onClick(territory: Territory) {
  selectTerritory(territory);
}
</script>

<template>
  <div class="flex-1 overflow-auto bg-gray-50 p-6 md:p-10">
    <div class="mx-auto max-w-4xl">
      <h2 class="mb-6 text-center text-xl font-semibold text-gray-700">
        Sélectionnez un territoire
      </h2>

      <div class="flex flex-col gap-4 md:flex-row">
        <!-- Metropole -->
        <button
          class="flex flex-1 cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
          @click="onClick(METROPOLE)"
        >
          <div class="w-full flex-1">
            <TerritoryOutline :territory="METROPOLE" />
          </div>
          <h3 class="text-sm font-semibold text-gray-800">{{ METROPOLE.label }}</h3>
        </button>

        <!-- Outre-mer par continent -->
        <div class="flex flex-1 flex-col gap-4">
          <div v-for="group in OUTREMER_GROUPS" :key="group.label">
            <h3 class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400">
              {{ group.label }}
            </h3>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="territory in group.territories"
                :key="territory.id"
                class="flex cursor-pointer flex-col items-center gap-1.5 rounded-lg border border-gray-200 bg-white p-3 shadow-sm transition-shadow hover:shadow-md"
                @click="onClick(territory)"
              >
                <div class="h-14 w-14">
                  <TerritoryOutline :territory="territory" />
                </div>
                <h3 class="text-center text-xs font-semibold text-gray-800">{{ territory.label }}</h3>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
