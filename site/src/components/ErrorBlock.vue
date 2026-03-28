<script setup lang="ts">
const props = defineProps<{
  message: string;
  class?: string;
}>();

const emit = defineEmits<{
  retry: [];
}>();
</script>

<template>
  <div :class="props.class" class="flex flex-col items-center gap-3 text-center text-sm">
    <p class="text-red-600">{{ message }}</p>
    <div class="flex gap-2">
      <button
        class="cursor-pointer rounded bg-blue-600 px-3 py-1 text-white hover:bg-blue-700"
        @click="emit('retry')"
      >
        Réessayer
      </button>
      <router-link
        :to="{ name: 'home' }"
        class="rounded border border-gray-300 px-3 py-1 text-gray-600 hover:bg-gray-50"
      >
        Retour à l'accueil
      </router-link>
    </div>
  </div>
</template>
