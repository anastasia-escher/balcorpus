<script setup lang="ts">
import { ref } from 'vue'
import TagSearch from '~/components/TagSearch.vue'
import UDSearch from '~/components/UDSearch.vue'
import LemmaSearch from '~/components/LemmaSearch.vue'
import SimpleSearch from '~/components/SimpleSearch.vue'
import { useAPI } from '~/composables/useAPI'

const crumbs = [
   { by: 'text', label: 'By Full Text' },
  { by: 'lemma', label: 'By Lemma' },
  { by: 'tag', label: 'By Tag' },
  { by: 'ud', label: 'By UD Tag' },

]
const activeCrumb = ref(crumbs[0].by)

interface SearchResult {
  id: number
  source: string | null
  diplomatic: string | null
  lemma: string | null
  pos_tag: string | null
  ud_type: string | null
  sentence_id: number
  text_id: number
  text_name: string
  speaker_id: string | null
  speaker_name: string | null
  source_sentence: string
  diplomatic_sentence: string
}

interface SearchResponse {
  count: number
  results: SearchResult[]
}

type SearchKind = 'text' | 'lemma' | 'tag' | 'ud'

const results = ref<SearchResult[]>([])
const resultCount = ref<number | null>(null)
const loading = ref(false)
const searchError = ref('')
const hasSearched = ref(false)
const requestAPI = useAPI()

const search = async (kind: SearchKind, values: Record<string, string | null>) => {
  const params: Record<string, string> = {}

  if (kind === 'text' && values.textQuery?.trim()) params.q = values.textQuery.trim()
  if (kind === 'lemma' && values.lemma?.trim()) params.lemma = values.lemma.trim()
  if (kind === 'tag' && values.posQuery?.trim()) params.pos = values.posQuery.trim()
  if (kind === 'ud' && values.udTag) params.ud = values.udTag
  if (kind === 'ud' && values.parent) params.parent = values.parent

  if (!Object.keys(params).length) {
    searchError.value = 'Enter a search value first.'
    results.value = []
    resultCount.value = null
    hasSearched.value = false
    return
  }

  loading.value = true
  searchError.value = ''
  hasSearched.value = false
  const { data, error } = await requestAPI<SearchResponse>('tokens/search/', { params })
  loading.value = false

  if (error.value || !data.value) {
    results.value = []
    resultCount.value = null
    searchError.value = 'The corpus could not be searched. Please try again.'
    return
  }

  results.value = data.value.results
  resultCount.value = data.value.count
  hasSearched.value = true
}
</script>

<template>
  <section class="pb-24">
    <div class="h-64 lg:h-144">
      <img
        class="w-full h-full object-cover"
        src="/assets/images/mac.jpeg"
        alt="Corpus cover image"
      />
    </div>
    <div class="relative container px-4 mx-auto -mt-24">
      <div class="max-w-8xl px-4 pt-12 lg:pt-20 mx-auto bg-white rounded-2xl shadow-xl pb-24">
        <div class="max-w-2xl mb-12 mx-auto text-center">
          <h2 class="mb-8 text-4xl lg:text-6xl text-blue-800 font-extrabold font-heading tracking-tight">
            Corpus of Macedonian Language
          </h2>
          <div class="flex flex-wrap items-center justify-center mb-8 text-lg font-bold text-blue-700 gap-3 uppercase">
            <template v-for="(crumb, idx) in crumbs" :key="crumb.by">
              <button
                type="button"
                class="hover:bg-blue-100 transition focus:outline-none uppercase p-2 rounded"
                :class="activeCrumb === crumb.by ? 'bg-blue-100 text-blue-900' : ''"
                @click="activeCrumb = crumb.by"
              >
                {{ crumb.label }}
              </button>
              <span
                v-if="idx < crumbs.length - 1"
                class="text-2xl font-black"
              >&rsaquo;</span>
            </template>
          </div>
        </div>
        <div class="max-w-2xl mx-auto -mb-6">
          <div v-if="activeCrumb === 'text'">
            <SimpleSearch @search="search('text', $event)" />
          </div>
          <div v-else-if="activeCrumb === 'lemma'">
            <LemmaSearch @search="search('lemma', $event)" />
          </div>
          <div v-else-if="activeCrumb === 'tag'">
            <TagSearch @search="search('tag', $event)" />
          </div>
          <div v-else-if="activeCrumb === 'ud'">
            <UDSearch @search="search('ud', $event)" />
            </div>

          <div v-if="loading" class="mt-10 text-center text-gray-700">
            Searching the corpus…
          </div>
          <p v-else-if="searchError" class="mt-10 rounded bg-red-50 p-4 text-red-800">
            {{ searchError }}
          </p>
          <section v-else-if="hasSearched" class="mt-10 border-t border-gray-200 pt-8">
            <h3 class="text-2xl font-bold text-blue-900">
              Results <span class="text-base font-normal text-gray-600">({{ resultCount }})</span>
            </h3>
            <p v-if="!results.length" class="mt-4 text-gray-700">No matching tokens were found.</p>
            <ol v-else class="mt-5 space-y-4">
              <li v-for="result in results" :key="result.id" class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                <p class="font-semibold text-blue-900">
                  {{ result.source || result.diplomatic }}
                  <span v-if="result.lemma" class="font-normal text-gray-700"> — lemma: {{ result.lemma }}</span>
                  <span v-if="result.pos_tag" class="font-normal text-gray-700"> · PoS: {{ result.pos_tag }}</span>
                  <span v-if="result.ud_type" class="font-normal text-gray-700"> · UD: {{ result.ud_type }}</span>
                </p>
                <p class="mt-2 text-gray-800">{{ result.source_sentence || result.diplomatic_sentence }}</p>
                <p class="mt-2 text-sm text-gray-600">
                  {{ result.text_name || `Text ${result.text_id}` }}, sentence {{ result.sentence_id }}
                  <template v-if="result.speaker_name"> · {{ result.speaker_name }}</template>
                </p>
              </li>
            </ol>
            <p v-if="resultCount && resultCount > results.length" class="mt-4 text-sm text-gray-600">
              Showing the first {{ results.length }} matches.
            </p>
          </section>
        </div>
      </div>
    </div>
  </section>
</template>
