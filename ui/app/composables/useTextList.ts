import {computed, ref} from 'vue'
import {useAPI} from '~/composables/useAPI'
import {countPages} from '~/features/search/pagination'
import type {TextListResponse, TextMetadata} from '~/features/texts/texts.types'

/**
 * Reading the corpus's list of texts, one page at a time.
 *
 * The corpus holds about a hundred texts and paginates them itself, so the
 * page on screen only ever knows how many there are in total and which page
 * it is looking at. Everything a pager needs follows from those two numbers.
 */

/** How many texts one page of the list holds. */
export const TEXTS_PAGE_SIZE = 25

const FIRST_PAGE = 1

export function useTextList() {
  const requestAPI = useAPI()

  const texts = ref<TextMetadata[]>([])
  const textCount = ref(0)
  const page = ref(FIRST_PAGE)
  const loading = ref(false)
  // The request itself already tells the reader what went wrong through a
  // toast; this only decides whether the table or a message is shown.
  const failed = ref(false)

  const pageCount = computed(() => countPages(textCount.value, TEXTS_PAGE_SIZE))

  const fetchPage = async (wantedPage: number) => {
    loading.value = true
    failed.value = false

    try {
      const {data, error} = await requestAPI<TextListResponse>('texts/', {
        params: {
          page: String(wantedPage),
          page_size: String(TEXTS_PAGE_SIZE),
        },
      })

      if (error.value || !data.value) {
        texts.value = []
        textCount.value = 0
        failed.value = true
        return
      }

      texts.value = data.value.results
      textCount.value = data.value.count
      page.value = wantedPage
    } finally {
      loading.value = false
    }
  }

  /** Move to another page of the list, ignoring a page that does not exist. */
  const goToPage = async (wantedPage: number) => {
    if (wantedPage < FIRST_PAGE || wantedPage > pageCount.value || wantedPage === page.value) {
      return
    }

    await fetchPage(wantedPage)
  }

  const loadFirstPage = () => fetchPage(FIRST_PAGE)

  return {texts, textCount, page, pageCount, loading, failed, loadFirstPage, goToPage}
}
