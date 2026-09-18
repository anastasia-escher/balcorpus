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

const EMPTY_SEARCH_ERROR_KEY = 'search.errors.empty'
const SEARCH_FAILURE_ERROR_KEY = 'search.errors.failed'

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
  const searchErrorKey = ref<string | null>(null)
  const hasSearched = ref(false)
  const requestAPI = useAPI()

  const searchInputs = {
    textQuery,
    lemma,
    posQuery,
    udTag,
    parent,
  } satisfies Record<SearchInputKey, { value: string | null }>

  const selectSearchKind = (kind: SearchKind) => {
    activeSearchKind.value = kind
  }

  const resetSearchInput = (kind: SearchKind) => {
    for (const { inputKey } of SEARCH_REQUEST_FIELDS[kind]) {
      searchInputs[inputKey].value = inputKey === 'udTag' || inputKey === 'parent' ? null : ''
    }
  }

  const clearSearchResults = () => {
    results.value = []
    resultCount.value = null
    hasSearched.value = false
  }

  const buildSearchParameters = (kind: SearchKind) => {
    const parameters: Record<string, string> = {}

    for (const { inputKey, parameterName } of SEARCH_REQUEST_FIELDS[kind]) {
      const value = searchInputs[inputKey].value?.trim()
      if (value) {
        parameters[parameterName] = value
      }
    }

    return parameters
  }

  const submitSearch = async (kind: SearchKind) => {
    const parameters = buildSearchParameters(kind)

    if (!Object.keys(parameters).length) {
      clearSearchResults()
      searchErrorKey.value = EMPTY_SEARCH_ERROR_KEY
      return
    }

    loading.value = true
    searchErrorKey.value = null
    hasSearched.value = false

    try {
      const { data, error } = await requestAPI<SearchResponse>('tokens/search/', { params: parameters })

      if (error.value || !data.value) {
        clearSearchResults()
        searchErrorKey.value = SEARCH_FAILURE_ERROR_KEY
        return
      }

      results.value = data.value.results
      resultCount.value = data.value.count
      hasSearched.value = true
    } finally {
      loading.value = false
    }
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
    searchErrorKey,
    hasSearched,
    selectSearchKind,
    resetSearchInput,
    submitSearch,
  }
})
