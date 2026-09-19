<script setup lang="ts">
import AppFooter from '~/components/layout/AppFooter.vue'
import AppNavigation from '~/components/layout/AppNavigation.vue'
</script>

<template>
  <UApp>
    <div class="relative flex min-h-screen flex-col bg-paper">
      <!-- The navigation floats over the cover photograph, which starts at the
           very top of the page, so it is taken out of the normal flow. -->
      <AppNavigation class="absolute inset-x-0 top-0 z-30" />
      <main class="flex-1">
        <slot />
      </main>
      <AppFooter />
    </div>
  </UApp>
</template>
