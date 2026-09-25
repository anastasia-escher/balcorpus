<script setup lang="ts">
import {computed, ref} from 'vue'
import {ELLIPSIS, pageItems} from '~/features/pagination/pagination'
import {useI18n} from 'vue-i18n'

/**
 * A pager for anything the corpus hands out a page at a time.
 *
 * It holds no state of its own: it is told which page is on screen and how
 * many there are, and reports back which one was asked for.
 */
const props = defineProps<{
  page: number
  pageCount: number
}>()

const emit = defineEmits<{select: [page: number]}>()

const {t} = useI18n()

const items = computed(() => pageItems(props.page, props.pageCount))

const pager = ref<HTMLElement | null>(null)

/**
 * Ask for a page, and scroll back to the top of the list.
 *
 * The pager stands at the bottom of the list it pages, inside the same
 * element, so that element's top is where the new page begins. Without
 * this the reader would be left looking at the end of the new page.
 */
const select = (wantedPage: number) => {
  emit('select', wantedPage)
  pager.value?.parentElement?.scrollIntoView({behavior: 'smooth', block: 'start'})
}
</script>

<template>
  <nav
    v-if="pageCount > 1"
    ref="pager"
    class="mt-8 flex flex-wrap items-center gap-1 border-t border-stone-200 pt-5"
    :aria-label="t('pagination.label')">
    <button
      type="button"
      class="px-2 py-1 text-sm text-stone-500 transition-colors hover:text-stone-900 disabled:text-stone-300"
      :disabled="page <= 1"
      @click="select(page - 1)">
      {{ t('pagination.previous') }}
    </button>

    <template v-for="(item, index) in items" :key="`${item}-${index}`">
      <span v-if="item === ELLIPSIS" class="px-1 text-sm text-stone-400">…</span>
      <button
        v-else
        type="button"
        class="min-w-8 px-2 py-1 text-sm transition-colors"
        :class="
          item === page
            ? 'font-semibold text-terracotta-700 underline underline-offset-4'
            : 'text-stone-500 hover:text-stone-900'
        "
        :aria-current="item === page ? 'page' : undefined"
        @click="select(item)">
        {{ item }}
      </button>
    </template>

    <button
      type="button"
      class="px-2 py-1 text-sm text-stone-500 transition-colors hover:text-stone-900 disabled:text-stone-300"
      :disabled="page >= pageCount"
      @click="select(page + 1)">
      {{ t('pagination.next') }}
    </button>
  </nav>
</template>
