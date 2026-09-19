<script setup lang="ts">
import {computed} from 'vue'
import {ELLIPSIS, pageItems} from '~/features/search/pagination'
import {useSearchStore} from '~/stores/search'
import {useI18n} from 'vue-i18n'

const searchStore = useSearchStore()
const {t} = useI18n()

const items = computed(() => pageItems(searchStore.page, searchStore.pageCount))
</script>

<template>
  <nav
    v-if="searchStore.pageCount > 1"
    class="mt-8 flex flex-wrap items-center gap-1 border-t border-stone-200 pt-5"
    :aria-label="t('pagination.label')">
    <button
      type="button"
      class="px-2 py-1 text-sm text-stone-500 transition-colors hover:text-stone-900 disabled:text-stone-300"
      :disabled="searchStore.page <= 1"
      @click="searchStore.goToPage(searchStore.page - 1)">
      {{ t('pagination.previous') }}
    </button>

    <template v-for="(item, index) in items" :key="`${item}-${index}`">
      <span v-if="item === ELLIPSIS" class="px-1 text-sm text-stone-400">…</span>
      <button
        v-else
        type="button"
        class="min-w-8 px-2 py-1 text-sm transition-colors"
        :class="
          item === searchStore.page
            ? 'font-semibold text-terracotta-700 underline underline-offset-4'
            : 'text-stone-500 hover:text-stone-900'
        "
        :aria-current="item === searchStore.page ? 'page' : undefined"
        @click="searchStore.goToPage(item)">
        {{ item }}
      </button>
    </template>

    <button
      type="button"
      class="px-2 py-1 text-sm text-stone-500 transition-colors hover:text-stone-900 disabled:text-stone-300"
      :disabled="searchStore.page >= searchStore.pageCount"
      @click="searchStore.goToPage(searchStore.page + 1)">
      {{ t('pagination.next') }}
    </button>
  </nav>
</template>
