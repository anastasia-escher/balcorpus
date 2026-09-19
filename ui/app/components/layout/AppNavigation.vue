<script setup lang="ts">
import {NAVIGATION_LINKS} from '~/features/layout/navigation.constants'
import type {NavigationVariant} from '~/features/layout/navigation.variants'
import {computed} from 'vue'
import {useLayoutStore} from '~/stores/layout'
import {useI18n} from 'vue-i18n'

const props = defineProps<{
  variant: NavigationVariant
}>()

const layoutStore = useLayoutStore()
const {t} = useI18n()

/**
 * Over a photograph the bar is painted in light ink under a dark scrim; on a
 * page without one it is paper with a hairline under it, like a running head.
 */
const overPhoto = computed(() => props.variant === 'over-photo')
</script>

<template>
  <header
    :class="
      overPhoto
        ? 'bg-gradient-to-b from-stone-950/70 via-stone-950/35 to-transparent pb-4'
        : 'border-b border-stone-200 bg-paper'
    ">
    <div class="mx-auto flex max-w-5xl items-center gap-4 px-6 py-4">
      <NuxtLink
        to="/"
        class="font-serif text-lg"
        :class="
          overPhoto
            ? 'text-paper drop-shadow-sm hover:text-terracotta-200'
            : 'text-stone-900 hover:text-terracotta-700'
        ">
        {{ t('site.name') }}
      </NuxtLink>

      <nav class="ml-auto" :aria-label="t('navigation.mainLabel')">
        <button
          type="button"
          class="p-1 sm:hidden"
          :class="overPhoto ? 'text-paper' : 'text-stone-700'"
          :aria-label="t('navigation.toggle')"
          :aria-expanded="layoutStore.mobileNavigationOpen"
          @click="layoutStore.toggleMobileNavigation">
          <UIcon name="i-lucide-menu" class="text-xl" />
        </button>

        <ul class="hidden gap-6 sm:flex">
          <li v-for="link in NAVIGATION_LINKS" :key="link.path">
            <NuxtLink
              class="text-sm transition-colors"
              :class="
                overPhoto
                  ? 'text-stone-200 drop-shadow-sm hover:text-white'
                  : 'text-stone-600 hover:text-stone-900'
              "
              :active-class="overPhoto ? 'text-white' : 'text-stone-900'"
              :to="link.path">
              {{ t(link.labelKey) }}
            </NuxtLink>
          </li>
        </ul>
      </nav>
    </div>

    <transition name="fade">
      <div
        v-if="layoutStore.mobileNavigationOpen"
        class="fixed inset-0 z-40 bg-stone-900/40"
        @click="layoutStore.closeMobileNavigation" />
    </transition>
    <transition name="slide">
      <!-- The drawer is paper in both variants: it covers the page rather
           than floating over the photograph. -->
      <nav
        v-if="layoutStore.mobileNavigationOpen"
        class="fixed top-0 bottom-0 left-0 z-50 flex w-5/6 max-w-xs flex-col overflow-y-auto border-r border-stone-200 bg-paper py-5"
        :aria-label="t('navigation.mobileLabel')">
        <div class="flex items-center px-6 pb-6">
          <span class="font-serif text-lg text-stone-900">{{ t('site.name') }}</span>
          <button
            type="button"
            class="ml-auto p-1 text-stone-500 hover:text-stone-900"
            :aria-label="t('navigation.close')"
            @click="layoutStore.closeMobileNavigation">
            <UIcon name="i-lucide-x" class="text-xl" />
          </button>
        </div>
        <ul>
          <li v-for="link in NAVIGATION_LINKS" :key="link.path">
            <NuxtLink
              class="block px-6 py-3 text-stone-600 hover:bg-paper-dark hover:text-stone-900"
              active-class="text-stone-900"
              :to="link.path"
              @click="layoutStore.closeMobileNavigation">
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
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition:
    transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),
    opacity 0.25s;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}
</style>
