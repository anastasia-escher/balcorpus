<script setup lang="ts">
import AppNavigation from '~/components/layout/AppNavigation.vue'
</script>

<template>
  <UApp>
    <div class="bg-blue-50 min-h-screen w-full dark:bg-gray-950">
      <AppNavigation />
      <main class="mt-8">
        <slot />
      </main>
    </div>
  </UApp>
</template>
