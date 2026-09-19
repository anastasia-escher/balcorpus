<script setup lang="ts">
import CorpusPagination from '~/components/common/CorpusPagination.vue'
import SearchResultContext from '~/components/search/SearchResultContext.vue'
import {SEARCH_PAGE_SIZE} from '~/features/search/search.constants'
import {pageRange} from '~/features/pagination/pagination'
import {wordForm} from '~/features/corpus/word-form'
import {splitSentenceAroundToken} from '~/features/search/highlight'
import {computed} from 'vue'
import {useSearchStore} from '~/stores/search'
import {useSentenceContext} from '~/composables/useSentenceContext'
import {useI18n} from 'vue-i18n'
import type {SearchResult} from '~/features/search/search.types'

const searchStore = useSearchStore()
const {t} = useI18n()
const context = useSentenceContext()

/** The sentence the hit came from, split so the hit can be marked. */
const sentenceParts = (result: SearchResult) =>
  splitSentenceAroundToken(result.source_sentence || result.diplomatic_sentence, wordForm(result))

/** Which matches of the whole result set this page is showing. */
const shownRange = computed(() => ({
  ...pageRange(searchStore.page, searchStore.resultCount ?? 0, SEARCH_PAGE_SIZE),
  total: searchStore.resultCount ?? 0,
}))

/** The annotation of one hit, as label/value pairs, skipping what is missing. */
const annotations = (result: SearchResult) =>
  [
    {label: t('search.results.labels.lemma'), value: result.lemma},
    {label: t('search.results.labels.partOfSpeech'), value: result.pos_tag},
    {label: t('search.results.labels.ud'), value: result.ud_type},
  ].filter(entry => Boolean(entry.value))
</script>

<template>
  <div v-if="searchStore.loading" class="mt-12 text-center text-sm text-stone-500">
    {{ t('search.results.loading') }}
  </div>

  <p
    v-else-if="searchStore.searchErrorKey"
    class="mt-12 border-l-2 border-terracotta-500 bg-terracotta-50 px-4 py-3 text-sm text-terracotta-900">
    {{ t(searchStore.searchErrorKey) }}
  </p>

  <section v-else-if="searchStore.hasSearched" class="mt-12">
    <h2 class="font-serif text-lg text-stone-900">
      {{ t('search.results.title', {count: searchStore.resultCount}) }}
    </h2>

    <p v-if="!searchStore.results.length" class="mt-4 text-sm text-stone-600">
      {{ t('search.results.empty') }}
    </p>

    <ol v-else class="mt-6 divide-y divide-stone-200 border-t border-stone-200">
      <li v-for="result in searchStore.results" :key="result.id" class="py-5">
        <p class="font-serif text-lg leading-relaxed text-stone-800">
          {{ sentenceParts(result).before
          }}<mark
            v-if="sentenceParts(result).match"
            class="bg-terracotta-100 px-0.5 font-semibold text-terracotta-900">
            {{ sentenceParts(result).match }}</mark
          >{{ sentenceParts(result).after }}
        </p>

        <dl class="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-xs text-stone-500">
          <div v-for="entry in annotations(result)" :key="entry.label" class="flex gap-1.5">
            <dt class="tracking-[0.08em] uppercase">{{ entry.label }}</dt>
            <dd class="font-medium text-stone-700">{{ entry.value }}</dd>
          </div>
        </dl>

        <p class="mt-1.5 text-xs text-stone-400">
          {{
            t('search.results.location', {
              textName:
                result.text_name || t('search.results.fallbackTextName', {textId: result.text_id}),
              sentenceId: result.sentence_id,
            })
          }}
          <template v-if="result.speaker_name">
            {{ t('search.results.speaker', {speakerName: result.speaker_name}) }}</template
          >
        </p>

        <button
          type="button"
          class="mt-2 text-xs text-stone-500 underline-offset-4 transition-colors hover:text-terracotta-700 hover:underline"
          :aria-expanded="context.isOpen(result)"
          @click="context.toggleContext(result)">
          {{ context.isOpen(result) ? t('search.context.hide') : t('search.context.show') }}
        </button>

        <SearchResultContext
          v-if="context.isOpen(result)"
          :sentences="context.sentencesFor(result)"
          :matched-sentence-id="result.sentence_id"
          :loading="context.isLoading(result)" />
      </li>
    </ol>

    <p v-if="searchStore.pageCount > 1" class="mt-6 text-xs text-stone-500">
      {{ t('search.results.showingRange', shownRange) }}
    </p>

    <CorpusPagination
      :page="searchStore.page"
      :page-count="searchStore.pageCount"
      @select="searchStore.goToPage" />
  </section>
</template>
