import {computed, ref} from 'vue'
import {defineStore} from 'pinia'
import {useAPI} from '~/composables/useAPI'
import {SEARCH_PAGE_SIZE, SEARCH_REQUEST_FIELDS} from '~/features/search/search.constants'
import {createContextCriteria} from '~/features/search/context-criteria'
import {fixLatinLookalikes} from '~/features/search/cyrillic-lookalikes'
import {createMorphologySelection} from '~/features/search/morphology-selection'
import {countPages} from '~/features/pagination/pagination'
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
  // The page opens on the first tab.
  const activeSearchKind = ref<SearchKind>('lemma')
  const textQuery = ref('')
  const lemma = ref('')
  // The morphology search: a part of speech, and the values chosen for its
  // properties. The tag pattern the corpus receives follows from these two, so
  // it is computed rather than stored next to them.
  const morphology = createMorphologySelection()
  // A word that has to stand near the match. It belongs to the search as a
  // whole and not to one tab, because every tab offers it.
  const context = createContextCriteria()
  // Whether the free-text search also matches inside longer words. Off by
  // default: someone looking for a word form wants that form.
  const partialText = ref(false)
  const udTag = ref<string | undefined>()
  const parent = ref<string | undefined>()
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
  // Searches are counted so that only the newest one may show its answer. Two
  // of them started shortly after one another come back in whatever order the
  // corpus happens to answer in, and a slow first answer would otherwise
  // overwrite the fast second one: the list would then show a search the form
  // no longer describes.
  let newestRequest = 0

  const requestAPI = useAPI()

  const searchInputs = {
    textQuery,
    lemma,
    udTag,
    parent,
  } satisfies Record<SearchInputKey, {value: string | undefined}>

  const pageCount = computed(() => countPages(resultCount.value ?? 0, SEARCH_PAGE_SIZE))

  const selectSearchKind = (kind: SearchKind) => {
    activeSearchKind.value = kind
  }

  /** Empty the form of one tab, the nearby word it asks about included. */
  const resetSearchInput = (kind: SearchKind) => {
    context.reset()

    if (kind === 'tag') {
      // Dropping the part of speech drops the properties chosen under it.
      morphology.reset()
      return
    }

    for (const {inputKey} of SEARCH_REQUEST_FIELDS[kind]) {
      searchInputs[inputKey].value =
        inputKey === 'udTag' || inputKey === 'parent' ? undefined : ''
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
      // A Latin j typed into a Cyrillic word would match nothing. The fixed
      // word is written back, so the field shows what was really searched.
      if (inputKey === 'textQuery' || inputKey === 'lemma') {
        searchInputs[inputKey].value = fixLatinLookalikes(searchInputs[inputKey].value)
      }

      const value = searchInputs[inputKey].value?.trim()
      if (value) {
        parameters[parameterName] = value
      }
    }

    // 'parent' only narrows another criterion down further: on its own it
    // asks for every token in the corpus, which the corpus refuses. Dropping
    // it here leaves an empty form, so the reader is told to enter something
    // rather than shown a failed request.
    if (parameters.parent && !parameters.ud) {
      delete parameters.parent
    }

    // Built from the chosen part of speech and properties rather than read
    // from a field, which is why it is not part of SEARCH_REQUEST_FIELDS.
    if (kind === 'tag' && morphology.pattern.value) {
      parameters.pos = morphology.pattern.value
    }

    // The nearby word, when one was described. It rides along with every tab,
    // and on its own it is not a search: the corpus needs a word to look for
    // before it can ask what stands next to it.
    if (Object.keys(parameters).length) {
      // The nearby word gets the same Latin look-alike fix as the main field.
      context.textQuery.value = fixLatinLookalikes(context.textQuery.value)
      context.lemma.value = fixLatinLookalikes(context.lemma.value)
      Object.assign(parameters, context.toParameters())
    }

    // A flag rather than a value, so it is not part of SEARCH_REQUEST_FIELDS.
    // It only rides along with a query: on its own it is not a search, and
    // adding it would turn an empty form into a request the corpus refuses.
    if (kind === 'text' && partialText.value && parameters.q) {
      parameters.partial = 'true'
    }

    return parameters
  }

  /** Ask the corpus for one page of the search that is already on screen. */
  const fetchPage = async (wantedPage: number) => {
    const thisRequest = (newestRequest += 1)

    loading.value = true
    searchErrorKey.value = null

    try {
      const {data, error} = await requestAPI<SearchResponse>('tokens/search/', {
        params: {
          ...submittedParameters.value,
          page: String(wantedPage),
          page_size: String(SEARCH_PAGE_SIZE),
        },
      })

      // Another search was started while this one was on its way, so this
      // answer is no longer the one on screen and is dropped.
      if (thisRequest !== newestRequest) {
        return
      }

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
      if (thisRequest === newestRequest) {
        loading.value = false
      }
    }
  }

  /** Run a new search, starting at its first page. */
  const submitSearch = async (kind: SearchKind) => {
    const parameters = buildSearchParameters(kind)

    if (!Object.keys(parameters).length) {
      // A search still on its way must not land on top of this message,
      // so it is made out of date, the same way a new search would.
      newestRequest += 1
      loading.value = false
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
    // The morphology chooser is spread flat, so a component reads
    // searchStore.morphologyPattern rather than reaching through an object.
    morphologyCategoryCode: morphology.categoryCode,
    morphologySelection: morphology.selection,
    morphologyPattern: morphology.pattern,
    selectMorphologyCategory: morphology.selectCategory,
    setMorphologyValue: morphology.setValue,
    // The nearby word keeps its own object: it holds a whole small form of
    // its own, and one prefix per field would read worse than context.lemma.
    context,
    partialText,
    udTag,
    parent,
    results,
    resultCount,
    loading,
    searchErrorKey,
    hasSearched,
    page,
    pageCount,
    submittedParameters,
    selectSearchKind,
    resetSearchInput,
    submitSearch,
    goToPage,
  }
})
