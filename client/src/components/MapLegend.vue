<script setup lang="ts">
import { useAppState } from "../composables/useAppState";

const { currentIndicateur } = useAppState();
</script>

<template>
  <div class="absolute bottom-8 left-3 z-[1000] rounded-lg bg-white/95 px-3.5 py-2.5 text-xs shadow-md">
    <div class="mb-1.5 font-semibold text-gray-700">{{ currentIndicateur?.nom ?? 'Indicateur' }}</div>
    <div
      class="h-3 w-48 rounded-sm"
      style="background: linear-gradient(to right, rgb(180, 0, 0), rgb(255, 255, 255) 50%, rgb(128, 128, 213) 75%, rgb(0, 0, 170))"
    ></div>
    <div class="mt-0.5 flex justify-between text-gray-500">
      <span>0%</span>
      <span>50%</span>
      <span>75%</span>
      <span>100%</span>
    </div>
  </div>
</template>
