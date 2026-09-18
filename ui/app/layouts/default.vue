<script setup lang="ts">
import AppNavigation from '~/components/layout/AppNavigation.vue'
</script>

<template>
  <div class="bg-blue-50 min-h-screen w-full">
    <Toast />
    <AppNavigation />
    <main class="mt-8">
      <slot />
    </main>
  </div>
</template>
