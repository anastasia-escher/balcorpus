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

  const fetchPage = async (wantedPage: number) => {
    loading.value = true
    failed.value = false

    try {
      const {data, error} = await requestAPI<PaginatedResponse<Item>>(endpoint, {
        params: {
          ...query.value,
          page: String(wantedPage),
          page_size: String(pageSize),
        },
      })

      if (error.value || !data.value) {
        items.value = []
        itemCount.value = 0
        failed.value = true
        return
      }

      items.value = data.value.results
      itemCount.value = data.value.count
      page.value = wantedPage
    } finally {
      loading.value = false
    }
  }

  /** Start a list from its first page, narrowed by the given parameters. */
  const load = async (narrowing: Record<string, string> = {}) => {
    query.value = narrowing
    await fetchPage(FIRST_PAGE)
  }

  /** Move to another page of the list, ignoring a page that does not exist. */
  const goToPage = async (wantedPage: number) => {
    if (wantedPage < FIRST_PAGE || wantedPage > pageCount.value || wantedPage === page.value) {
      return
    }

    await fetchPage(wantedPage)
  }

  return {items, itemCount, page, pageCount, loading, failed, load, goToPage}
}
