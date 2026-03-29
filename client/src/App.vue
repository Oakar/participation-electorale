<script setup lang="ts">
import { onMounted, watch } from "vue";
import { useAppState } from "./composables/useAppState";
import { apiDao } from "./services/apiDao";
import IndicateurSelector from "./components/IndicateurSelector.vue";
import BreadcrumbNav from "./components/BreadcrumbNav.vue";

const { categories, indicateurs, currentCategorieId, currentIndicateurId } =
  useAppState();

onMounted(async () => {
  categories.value = await apiDao.fetchCategories();
  if (categories.value.length > 0 && !currentCategorieId.value) {
    currentCategorieId.value = categories.value[0].id;
  }
});

watch(currentCategorieId, async (catId) => {
  if (!catId) return;
  indicateurs.value = await apiDao.fetchIndicateurs(catId);
  if (
    indicateurs.value.length > 0 &&
    !indicateurs.value.some((i) => i.id === currentIndicateurId.value)
  ) {
    currentIndicateurId.value = indicateurs.value[indicateurs.value.length - 1].id;
  }
}, { immediate: true });
</script>

<template>
  <div class="flex h-screen flex-col font-sans text-gray-800">
    <header class="border-b border-gray-200 bg-white px-4 py-3 shadow-sm">
      <div class="flex items-center justify-between gap-4">
        <h1 class="text-lg font-semibold text-gray-900">
          PRISME
        </h1>
        <IndicateurSelector />
      </div>
      <BreadcrumbNav />
    </header>
    <main class="relative flex min-h-0 flex-1">
      <router-view />
    </main>
  </div>
</template>
