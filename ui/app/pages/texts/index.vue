<script setup lang="ts">
import CorpusPagination from '~/components/common/CorpusPagination.vue'
import TextsSearchField from '~/components/texts/TextsSearchField.vue'
import TextsTable from '~/components/texts/TextsTable.vue'
import {TEXTS_PAGE_SIZE} from '~/features/texts/texts.constants'
import {computed, onMounted, ref} from 'vue'
import {pageRange} from '~/features/pagination/pagination'
import {useListUrl} from '~/composables/useListUrl'
import {useTextList} from '~/composables/useTextList'
import {useI18n} from 'vue-i18n'

const textList = useTextList()
const listUrl = useListUrl()
const {t} = useI18n()

// What the page was opened with: a plain /texts, or a link carrying a search
// and a page number.
const openedWith = {search: listUrl.searchInUrl(), page: listUrl.pageInUrl()}

// The search now on screen, which paging has to keep asking for.
const currentSearch = ref(openedWith.search)

/** Which of all the texts this page is showing. */
const shownRange = computed(() => ({
  ...pageRange(textList.page.value, textList.itemCount.value, TEXTS_PAGE_SIZE),
  total: textList.itemCount.value,
}))

/** An empty query asks for the whole catalogue, which is what Clear wants. */
const narrowing = (search: string): Record<string, string> => (search ? {q: search} : {})

/** Put into the address whatever the list is actually showing now. */
const rememberInUrl = () => listUrl.writeToUrl({page: textList.page.value, search: currentSearch.value})

const search = async (query: string) => {
  currentSearch.value = query
  const applied = await textList.load(narrowing(query))

  if (applied) {
    rememberInUrl()
  }
}

const goToPage = async (page: number) => {
  const applied = await textList.goToPage(page)

  if (applied) {
    rememberInUrl()
  }
}

onMounted(async () => {
  await textList.load(narrowing(openedWith.search), openedWith.page)
  // The list may have opened on a different page than the link asked for, if
  // that page does not exist; the address follows what is on screen.
  rememberInUrl()
})
</script>

<template>
  <article class="mx-auto max-w-5xl px-6 pt-12 pb-24">
    <header>
      <h1 class="font-serif text-3xl text-stone-900">{{ t('texts.title') }}</h1>
      <p class="mt-3 max-w-2xl text-sm text-stone-600">{{ t('texts.subtitle') }}</p>
    </header>

    <div class="mt-8">
      <TextsSearchField :initial-query="openedWith.search" @search="search" />
    </div>

    <p v-if="textList.loading.value" class="mt-12 text-sm text-stone-500">
      {{ t('texts.loading') }}
    </p>

    <p
      v-else-if="textList.failed.value"
      class="mt-12 border-l-2 border-terracotta-500 bg-terracotta-50 px-4 py-3 text-sm text-terracotta-900">
      {{ t('texts.failed') }}
    </p>

    <p v-else-if="!textList.items.value.length" class="mt-12 text-sm text-stone-600">
      {{ t('texts.noMatches') }}
    </p>

    <section v-else class="mt-8">
      <TextsTable :texts="textList.items.value" />

      <p v-if="textList.pageCount.value > 1" class="mt-6 text-xs text-stone-500">
        {{ t('texts.showingRange', shownRange) }}
      </p>

      <CorpusPagination
        :page="textList.page.value"
        :page-count="textList.pageCount.value"
        @select="goToPage" />
    </section>
  </article>
</template>
