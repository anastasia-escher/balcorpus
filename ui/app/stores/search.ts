import {computed, ref} from 'vue'
import {defineStore} from 'pinia'
import {useAPI} from '~/composables/useAPI'
import {SEARCH_REQUEST_FIELDS} from '~/features/search/search.constants'
import {PAGE_SIZE, countPages} from '~/features/search/pagination'
import type {
  SearchInputKey,
  SearchKind,
  SearchResponse,
  SearchResult,
} from '~/features/search/search.types'

const EMPTY_SEARCH_ERROR_KEY = 'search.errors.empty'
const SEARCH_FAILURE_ERROR_KEY = 'search.errors.failed'

const FIRST_PAGE = 1

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

  // The corpus sends one page at a time, so the page being looked at is part
  // of the search rather than something the interface does on its own.
  const page = ref(FIRST_PAGE)
  // The criteria of the search now on screen. Paging asks for another page of
  // the same search, so it must not read the form again: the user may have
  // typed something new into it in the meantime.
  const submittedParameters = ref<Record<string, string>>({})

  const requestAPI = useAPI()

  const searchInputs = {
    textQuery,
    lemma,
    posQuery,
    udTag,
    parent,
  } satisfies Record<SearchInputKey, {value: string | null}>

  const pageCount = computed(() => countPages(resultCount.value ?? 0))

  const selectSearchKind = (kind: SearchKind) => {
    activeSearchKind.value = kind
  }

  const resetSearchInput = (kind: SearchKind) => {
    for (const {inputKey} of SEARCH_REQUEST_FIELDS[kind]) {
      searchInputs[inputKey].value = inputKey === 'udTag' || inputKey === 'parent' ? null : ''
    }
  }

  const clearSearchResults = () => {
    results.value = []
    resultCount.value = null
    hasSearched.value = false
    page.value = FIRST_PAGE
  }

  const buildSearchParameters = (kind: SearchKind) => {
    const parameters: Record<string, string> = {}

    for (const {inputKey, parameterName} of SEARCH_REQUEST_FIELDS[kind]) {
      const value = searchInputs[inputKey].value?.trim()
      if (value) {
        parameters[parameterName] = value
      }
    }

    return parameters
  }

  /** Ask the corpus for one page of the search that is already on screen. */
  const fetchPage = async (wantedPage: number) => {
    loading.value = true
    searchErrorKey.value = null

    try {
      const {data, error} = await requestAPI<SearchResponse>('tokens/search/', {
        params: {
          ...submittedParameters.value,
          page: String(wantedPage),
          page_size: String(PAGE_SIZE),
        },
      })

      if (error.value || !data.value) {
        clearSearchResults()
        searchErrorKey.value = SEARCH_FAILURE_ERROR_KEY
        return
      }

      results.value = data.value.results
      resultCount.value = data.value.count
      page.value = wantedPage
      hasSearched.value = true
    } finally {
      loading.value = false
    }
  }

  /** Run a new search, starting at its first page. */
  const submitSearch = async (kind: SearchKind) => {
    const parameters = buildSearchParameters(kind)

    if (!Object.keys(parameters).length) {
      clearSearchResults()
      searchErrorKey.value = EMPTY_SEARCH_ERROR_KEY
      return
    }

    submittedParameters.value = parameters
    hasSearched.value = false
    await fetchPage(FIRST_PAGE)
  }

  /** Move to another page of the search now on screen. */
  const goToPage = async (wantedPage: number) => {
    if (wantedPage < FIRST_PAGE || wantedPage > pageCount.value || wantedPage === page.value) {
      return
    }

    await fetchPage(wantedPage)
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
    page,
    pageCount,
    selectSearchKind,
    resetSearchInput,
    submitSearch,
    goToPage,
  }
})
