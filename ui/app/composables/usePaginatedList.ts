import {computed, ref, type Ref} from 'vue'
import {countPages} from '~/features/pagination/pagination'
import {useAPI} from '~/composables/useAPI'

/**
 * Reading any list the corpus hands out a page at a time.
 *
 * Every list in this interface works the same way: ask for a page, keep what
 * came back, remember which page it was. Only the endpoint, how many fit on a
 * page, and any narrowing of the list differ, so those are what is passed in.
 *
 * Example: usePaginatedList<TextMetadata>('texts/', 25)
 */

/** The shape the corpus answers a list request with. */
interface PaginatedResponse<Item> {
  count: number
  next: string | null
  previous: string | null
  results: Item[]
}

const FIRST_PAGE = 1

export function usePaginatedList<Item>(endpoint: string, pageSize: number) {
  const requestAPI = useAPI()

  const items = ref([]) as Ref<Item[]>
  const itemCount = ref(0)
  const page = ref(FIRST_PAGE)
  const loading = ref(false)
  // The request itself already tells the reader what went wrong through a
  // toast; this only decides whether the list or a message is shown.
  const failed = ref(false)

  // What narrows the list, kept so that turning a page asks for another page
  // of the same list rather than of the whole corpus.
  const query = ref<Record<string, string>>({})

  const pageCount = computed(() => countPages(itemCount.value, pageSize))

  // Requests are numbered so that only the newest one may write its answer.
  // Two searches in quick succession can otherwise finish out of order and
  // leave the newer words in the search box above the older list.
  let latestRequest = 0

  /** Fetch one page. Answers whether this request was still the current one. */
  const fetchPage = async (wantedPage: number, quietNotFound = false): Promise<boolean> => {
    const thisRequest = (latestRequest += 1)

    loading.value = true
    failed.value = false

    try {
      const {data, error} = await requestAPI<PaginatedResponse<Item>>(endpoint, {
        quietNotFound,
        params: {
          ...query.value,
          page: String(wantedPage),
          page_size: String(pageSize),
        },
      })

      // Something newer was asked for while this was in flight, so this
      // answer is no longer the one the reader is waiting for.
      if (thisRequest !== latestRequest) {
        return false
      }

      if (error.value || !data.value) {
        items.value = []
        itemCount.value = 0
        failed.value = true
        return true
      }

      items.value = data.value.results
      itemCount.value = data.value.count
      page.value = wantedPage
      return true
    } finally {
      if (thisRequest === latestRequest) {
        loading.value = false
      }
    }
  }

  /**
   * Start a list, narrowed by the given parameters, at the given page.
   * Answers whether the list on screen is the result of this call.
   *
   * The page is passed in because a reader may arrive on a link that already
   * names one; asking for the first page and then walking to it would fetch
   * twice and flash the wrong content in between.
   */
  const load = async (narrowing: Record<string, string> = {}, startPage = FIRST_PAGE) => {
    query.value = narrowing

    // A link can name a page the list does not have: a bookmark from when the
    // corpus was smaller, or a number typed by hand. That is not worth an
    // error in the reader's face, so the attempt is made quietly and the list
    // simply opens at the beginning instead. The second attempt is loud: if
    // that one fails too, something is genuinely wrong.
    const namesAPage = startPage !== FIRST_PAGE
    const applied = await fetchPage(startPage, namesAPage)

    if (applied && failed.value && namesAPage) {
      return fetchPage(FIRST_PAGE)
    }

    return applied
  }

  /**
   * Move to another page of the list, ignoring a page that does not exist.
   * Answers whether the list on screen is now that page.
   */
  const goToPage = async (wantedPage: number) => {
    if (wantedPage < FIRST_PAGE || wantedPage > pageCount.value || wantedPage === page.value) {
      return false
    }

    return fetchPage(wantedPage)
  }

  return {items, itemCount, page, pageCount, loading, failed, load, goToPage}
}
