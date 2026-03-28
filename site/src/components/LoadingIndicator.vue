<template>
  <div :class="props.class" class="text-center text-sm text-gray-400">
    Chargement...
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ class?: string }>();
</script>
