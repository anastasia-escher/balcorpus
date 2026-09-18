import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useAPI } from '~/composables/useAPI'
import { SEARCH_REQUEST_FIELDS } from '~/features/search/search.constants'
import type {
  SearchInputKey,
  SearchKind,
  SearchResponse,
  SearchResult,
} from '~/features/search/search.types'

const EMPTY_SEARCH_MESSAGE = 'Enter a search value first.'
const SEARCH_FAILURE_MESSAGE = 'The corpus could not be searched. Please try again.'

export const useSearchStore = defineStore('search', () => {
  const activeSearchKind = ref<SearchKind>('text')
  const textQuery = ref('')
  const lemma = ref('')
  const posQuery = ref('')
  const udTag = ref<string | null>(null)
  const parent = ref<string | null>(null)
  const results = ref<SearchResult[]>([])
  const resultCount = ref<number | null>(null)
  const loading = ref(false)
  const searchError = ref('')
  const hasSearched = ref(false)
  const requestAPI = useAPI()

  const searchInputs = {
    textQuery,
    lemma,
    posQuery,
    udTag,
    parent,
  } satisfies Record<SearchInputKey, { value: string | null }>

  function selectSearchKind(kind: SearchKind) {
    activeSearchKind.value = kind
  }

  function resetSearchInput(kind: SearchKind) {
    for (const { inputKey } of SEARCH_REQUEST_FIELDS[kind]) {
      searchInputs[inputKey].value = inputKey === 'udTag' || inputKey === 'parent' ? null : ''
    }
  }

  function clearSearchResults() {
    results.value = []
    resultCount.value = null
    hasSearched.value = false
  }

  function buildSearchParameters(kind: SearchKind) {
    const parameters: Record<string, string> = {}

    for (const { inputKey, parameterName } of SEARCH_REQUEST_FIELDS[kind]) {
      const value = searchInputs[inputKey].value?.trim()
      if (value) {
        parameters[parameterName] = value
      }
    }

    return parameters
  }

  async function submitSearch(kind: SearchKind) {
    const parameters = buildSearchParameters(kind)

    if (!Object.keys(parameters).length) {
      clearSearchResults()
      searchError.value = EMPTY_SEARCH_MESSAGE
      return
    }

    loading.value = true
    searchError.value = ''
    hasSearched.value = false

    const { data, error } = await requestAPI<SearchResponse>('tokens/search/', { params: parameters })
    loading.value = false

    if (error.value || !data.value) {
      clearSearchResults()
      searchError.value = SEARCH_FAILURE_MESSAGE
      return
    }

    results.value = data.value.results
    resultCount.value = data.value.count
    hasSearched.value = true
  }

  return {
    activeSearchKind,
    textQuery,
    lemma,
    posQuery,
    udTag,
    parent,
    results,
    resultCount,
    loading,
    searchError,
    hasSearched,
    selectSearchKind,
    resetSearchInput,
    submitSearch,
  }
})
