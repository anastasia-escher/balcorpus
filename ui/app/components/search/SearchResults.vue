<script setup lang="ts">
import { useSearchStore } from '~/stores/search'
import { useI18n } from 'vue-i18n'

const searchStore = useSearchStore()
const { t } = useI18n()
</script>

<template>
  <div v-if="searchStore.loading" class="mt-10 text-center text-gray-700">
    {{ t('search.results.loading') }}
  </div>
  <p v-else-if="searchStore.searchErrorKey" class="mt-10 rounded bg-red-50 p-4 text-red-800">
    {{ t(searchStore.searchErrorKey) }}
  </p>
  <section v-else-if="searchStore.hasSearched" class="mt-10 border-t border-gray-200 pt-8">
    <h3 class="text-2xl font-bold text-blue-900">
      {{ t('search.results.title', { count: searchStore.resultCount }) }}
    </h3>
    <p v-if="!searchStore.results.length" class="mt-4 text-gray-700">{{ t('search.results.empty') }}</p>
    <ol v-else class="mt-5 space-y-4">
      <li
        v-for="result in searchStore.results"
        :key="result.id"
        class="rounded-lg border border-gray-200 bg-gray-50 p-4"
      >
        <p class="font-semibold text-blue-900">
          {{ result.source || result.diplomatic }}
          <span v-if="result.lemma" class="font-normal text-gray-700"> {{ t('search.results.lemma', { lemma: result.lemma }) }}</span>
          <span v-if="result.pos_tag" class="font-normal text-gray-700"> {{ t('search.results.partOfSpeech', { tag: result.pos_tag }) }}</span>
          <span v-if="result.ud_type" class="font-normal text-gray-700"> {{ t('search.results.ud', { tag: result.ud_type }) }}</span>
        </p>
        <p class="mt-2 text-gray-800">{{ result.source_sentence || result.diplomatic_sentence }}</p>
        <p class="mt-2 text-sm text-gray-600">
          {{ t('search.results.location', {
            textName: result.text_name || t('search.results.fallbackTextName', { textId: result.text_id }),
            sentenceId: result.sentence_id,
          }) }}
          <template v-if="result.speaker_name"> {{ t('search.results.speaker', { speakerName: result.speaker_name }) }}</template>
        </p>
      </li>
    </ol>
    <p v-if="searchStore.resultCount && searchStore.resultCount > searchStore.results.length" class="mt-4 text-sm text-gray-600">
      {{ t('search.results.showingFirst', { count: searchStore.results.length }) }}
    </p>
  </section>
</template>
