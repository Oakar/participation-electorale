<script setup lang="ts">
import { onMounted } from "vue";
import { useAppState } from "./composables/useAppState";
import { staticDao } from "./services/staticDao";
import ElectionSelector from "./components/ElectionSelector.vue";
import BreadcrumbNav from "./components/BreadcrumbNav.vue";

const { elections } = useAppState();

onMounted(async () => {
  elections.value = await staticDao.fetchElections();
});
</script>

<template>
  <div class="flex h-screen flex-col font-sans text-gray-800">
    <header class="border-b border-gray-200 bg-white px-4 py-3 shadow-sm">
      <div class="flex items-center justify-between gap-4">
        <h1 class="text-lg font-semibold text-gray-900">
          Participation électorale en France
        </h1>
        <ElectionSelector />
      </div>
      <BreadcrumbNav />
    </header>
    <main class="relative flex min-h-0 flex-1">
      <router-view />
    </main>
  </div>
</template>
