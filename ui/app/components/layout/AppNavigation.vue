<script setup lang="ts">
import { onMounted } from 'vue'
import { NAVIGATION_LINKS } from '~/features/layout/navigation.constants'
import { useLayoutStore } from '~/stores/layout'
import { useI18n } from 'vue-i18n'

const layoutStore = useLayoutStore()
const { t } = useI18n()

onMounted(() => {
  layoutStore.initializeTheme()
})
</script>

<template>
  <header class="py-8 px-4 lg:px-10 bg-blue-800">
    <nav class="relative" :aria-label="t('navigation.mainLabel')">
      <div class="flex justify-between items-center">
        <button
          type="button"
          class="lg:hidden flex items-center p-3 rounded focus:outline-none"
          :aria-label="t('navigation.toggle')"
          :aria-expanded="layoutStore.mobileNavigationOpen"
          @click="layoutStore.toggleMobileNavigation"
        >
          <i class="pi pi-bars text-white text-xl" />
        </button>

        <ul class="hidden lg:flex lg:space-x-10 items-center">
          <li v-for="link in NAVIGATION_LINKS" :key="link.path">
            <NuxtLink class="text-white font-semibold hover:text-blue-50 flex items-center gap-1" :to="link.path">
              <i :class="link.icon" />
              {{ t(link.labelKey) }}
            </NuxtLink>
          </li>
        </ul>

        <button
          type="button"
          class="hidden lg:flex items-center text-white p-2 rounded-full transition hover:bg-blue-700 focus:outline-none"
          :aria-label="layoutStore.darkModeEnabled ? t('navigation.useLightTheme') : t('navigation.useDarkTheme')"
          @click="layoutStore.toggleTheme"
        >
          <i :class="layoutStore.darkModeEnabled ? 'pi pi-sun' : 'pi pi-moon'" />
        </button>
      </div>
    </nav>

    <transition name="fade">
      <div
        v-if="layoutStore.mobileNavigationOpen"
        class="fixed inset-0 z-40 bg-blue-800/90"
        @click="layoutStore.closeMobileNavigation"
      />
    </transition>
    <transition name="slide">
      <nav
        v-if="layoutStore.mobileNavigationOpen"
        class="fixed top-0 left-0 bottom-0 w-5/6 max-w-sm z-50 bg-white border-r flex flex-col py-8 overflow-y-auto"
        :aria-label="t('navigation.mobileLabel')"
      >
        <div class="flex items-center mb-12 px-6">
          <button
            type="button"
            class="ml-auto p-2"
            :aria-label="t('navigation.close')"
            @click="layoutStore.closeMobileNavigation"
          >
            <i class="pi pi-times text-2xl text-blue-800" />
          </button>
        </div>
        <ul>
          <li v-for="link in NAVIGATION_LINKS" :key="link.path">
            <NuxtLink
              class="block pl-8 py-4 font-semibold text-blue-800 hover:bg-blue-50 rounded flex items-center gap-2"
              :to="link.path"
              @click="layoutStore.closeMobileNavigation"
            >
              <i :class="link.icon" />
              {{ t(link.labelKey) }}
            </NuxtLink>
          </li>
        </ul>
      </nav>
    </transition>
  </header>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity .2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform .25s cubic-bezier(.4, 0, .2, 1), opacity .25s;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}
</style>
