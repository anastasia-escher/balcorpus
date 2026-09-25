import {computed, ref} from 'vue'
import {defineStore} from 'pinia'
import {usePaginatedList} from '~/composables/usePaginatedList'
import {SEARCH_PAGE_SIZE, SEARCH_REQUEST_FIELDS} from '~/features/search/search.constants'
import {createContextCriteria} from '~/features/search/context-criteria'
import {fixLatinLookalikes} from '~/features/search/cyrillic-lookalikes'
import {createMorphologySelection} from '~/features/search/morphology-selection'
import type {SearchInputKey, SearchKind, SearchResult} from '~/features/search/search.types'

const EMPTY_SEARCH_ERROR_KEY = 'search.errors.empty'
const SEARCH_FAILURE_ERROR_KEY = 'search.errors.failed'

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

  // The results arrive a page at a time, like every list of the corpus. The
  // shared list also makes sure that of two searches started one after the
  // other, only the newer one's answer is shown, whatever order they come in.
  const resultList = usePaginatedList<SearchResult>('tokens/search/', SEARCH_PAGE_SIZE)

  // Whether the form was sent empty; the reader is then told to fill it in.
  const submittedEmpty = ref(false)
  const hasSearched = ref(false)
  // The criteria of the search now on screen, for the Excel export link.
  // They are kept apart from the form, which the user may already have
  // changed again.
  const submittedParameters = ref<Record<string, string>>({})

  /** Which message to show instead of results, as an i18n key, or null. */
  const searchErrorKey = computed(() => {
    if (submittedEmpty.value) {
      return EMPTY_SEARCH_ERROR_KEY
    }
    if (resultList.failed.value) {
      return SEARCH_FAILURE_ERROR_KEY
    }
    return null
  })

  const searchInputs = {
    textQuery,
    lemma,
    udTag,
    parent,
  } satisfies Record<SearchInputKey, {value: string | undefined}>

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

  /** Run a new search, starting at its first page. */
  const submitSearch = async (kind: SearchKind) => {
    const parameters = buildSearchParameters(kind)
    hasSearched.value = false

    if (!Object.keys(parameters).length) {
      // clear() also drops a search still on its way, so that it cannot
      // land on top of this message.
      resultList.clear()
      submittedEmpty.value = true
      return
    }

    submittedEmpty.value = false
    submittedParameters.value = parameters

    const applied = await resultList.load(parameters)
    if (applied && !resultList.failed.value) {
      hasSearched.value = true
    }
  }

  /** Move to another page of the search now on screen. */
  const goToPage = async (wantedPage: number) => {
    await resultList.goToPage(wantedPage)
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
    results: resultList.items,
    resultCount: resultList.itemCount,
    loading: resultList.loading,
    searchErrorKey,
    hasSearched,
    page: resultList.page,
    pageCount: resultList.pageCount,
    submittedParameters,
    selectSearchKind,
    resetSearchInput,
    submitSearch,
    goToPage,
  }
})
