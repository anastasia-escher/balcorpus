<script setup lang="ts">
import { SEARCH_TABS } from '~/features/search/search.constants'
import { useSearchStore } from '~/stores/search'
import { useI18n } from 'vue-i18n'

const searchStore = useSearchStore()
const { t } = useI18n()
</script>

<template>
  <div class="flex flex-wrap items-center justify-center mb-8 text-lg font-bold text-blue-700 gap-3 uppercase">
    <template v-for="(tab, index) in SEARCH_TABS" :key="tab.kind">
      <button
        type="button"
        class="hover:bg-blue-100 transition focus:outline-none uppercase p-2 rounded"
        :class="searchStore.activeSearchKind === tab.kind ? 'bg-blue-100 text-blue-900' : ''"
        @click="searchStore.selectSearchKind(tab.kind)"
      >
        {{ t(tab.labelKey) }}
      </button>
      <span v-if="index < SEARCH_TABS.length - 1" class="text-2xl font-black">&rsaquo;</span>
    </template>
  </div>
</template>
