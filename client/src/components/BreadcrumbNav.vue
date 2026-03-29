<script setup lang="ts">
import { useAppState } from "../composables/useAppState";

const { breadcrumb } = useAppState();
</script>

<template>
  <nav class="mt-1 text-sm text-gray-500">
    <template v-for="(crumb, i) in breadcrumb" :key="i">
      <span v-if="i > 0" class="mx-1 text-gray-400">/</span>
      <router-link
        v-if="i < breadcrumb.length - 1"
        :to="crumb.to"
        class="text-blue-600 hover:underline"
      >
        {{ crumb.label }}
      </router-link>
      <span v-else class="font-semibold text-gray-700">{{ crumb.label }}</span>
    </template>
  </nav>
</template>
