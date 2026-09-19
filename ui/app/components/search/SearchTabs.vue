<script setup lang="ts">
import {SEARCH_TABS} from '~/features/search/search.constants'
import {useSearchStore} from '~/stores/search'
import {useI18n} from 'vue-i18n'

const searchStore = useSearchStore()
const {t} = useI18n()
</script>

<template>
  <div class="border-b border-stone-200" role="tablist">
    <!-- The negative margin lets the active tab's rule sit on top of the
         container's rule, so the two read as one line. -->
    <div class="-mb-px flex flex-wrap gap-x-7 gap-y-1">
      <button
        v-for="tab in SEARCH_TABS"
        :key="tab.kind"
        type="button"
        role="tab"
        :aria-selected="searchStore.activeSearchKind === tab.kind"
        class="border-b-2 pb-3 text-xs tracking-[0.12em] uppercase transition-colors focus:outline-none"
        :class="
          searchStore.activeSearchKind === tab.kind
            ? 'border-terracotta-600 text-stone-900'
            : 'border-transparent text-stone-500 hover:text-stone-800'
        "
        @click="searchStore.selectSearchKind(tab.kind)">
        {{ t(tab.labelKey) }}
      </button>
    </div>
  </div>
</template>
