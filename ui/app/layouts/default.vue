<script setup lang="ts">
import AppFooter from '~/components/layout/AppFooter.vue'
import AppNavigation from '~/components/layout/AppNavigation.vue'
import {DEFAULT_NAVIGATION_VARIANT} from '~/features/layout/navigation.constants'
import {computed} from 'vue'
import {useRoute} from 'vue-router'

const route = useRoute()

// A page that opens with a cover photograph says so in its own page meta;
// every other page gets the plain bar.
const navigationVariant = computed(
  () => route.meta.navigationVariant ?? DEFAULT_NAVIGATION_VARIANT,
)
</script>

<template>
  <UApp>
    <div class="relative flex min-h-screen flex-col bg-paper">
      <!-- Over a photograph the bar is taken out of the flow so the picture
           can start at the very top of the page; otherwise it sits in the
           flow and the page below simply follows it. -->
      <AppNavigation
        :variant="navigationVariant"
        :class="navigationVariant === 'over-photo' ? 'absolute inset-x-0 top-0 z-30' : ''" />
      <main class="flex-1">
        <slot />
      </main>
      <AppFooter />
    </div>
  </UApp>
</template>
