<script setup lang="ts">
import CorpusPagination from '~/components/common/CorpusPagination.vue'
import TextsTable from '~/components/texts/TextsTable.vue'
import {TEXTS_PAGE_SIZE, useTextList} from '~/composables/useTextList'
import {computed, onMounted} from 'vue'
import {pageRange} from '~/features/search/pagination'
import {useI18n} from 'vue-i18n'

const textList = useTextList()
const {t} = useI18n()

/** Which of all the texts this page is showing. */
const shownRange = computed(() => ({
  ...pageRange(textList.page.value, textList.textCount.value, TEXTS_PAGE_SIZE),
  total: textList.textCount.value,
}))

onMounted(textList.loadFirstPage)
</script>

<template>
  <article class="mx-auto max-w-5xl px-6 pt-12 pb-24">
    <header>
      <h1 class="font-serif text-3xl text-stone-900">{{ t('texts.title') }}</h1>
      <p class="mt-3 max-w-2xl text-sm text-stone-600">{{ t('texts.subtitle') }}</p>
    </header>

    <p v-if="textList.loading.value" class="mt-12 text-sm text-stone-500">
      {{ t('texts.loading') }}
    </p>

    <p
      v-else-if="textList.failed.value"
      class="mt-12 border-l-2 border-terracotta-500 bg-terracotta-50 px-4 py-3 text-sm text-terracotta-900">
      {{ t('texts.failed') }}
    </p>

    <p v-else-if="!textList.texts.value.length" class="mt-12 text-sm text-stone-600">
      {{ t('texts.empty') }}
    </p>

    <section v-else class="mt-10">
      <TextsTable :texts="textList.texts.value" />

      <p v-if="textList.pageCount.value > 1" class="mt-6 text-xs text-stone-500">
        {{ t('texts.showingRange', shownRange) }}
      </p>

      <CorpusPagination
        :page="textList.page.value"
        :page-count="textList.pageCount.value"
        @select="textList.goToPage" />
    </section>
  </article>
</template>
