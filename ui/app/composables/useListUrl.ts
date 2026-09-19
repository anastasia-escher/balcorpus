import {useRoute, useRouter} from 'vue-router'

/**
 * Keeping a list's state in the address bar.
 *
 * Which page is being read, and what the list was narrowed to, are things a
 * reader expects to survive a reload and to travel in a shared link. They
 * belong in the address rather than only in memory.
 *
 * Defaults are left out, so the address stays short: /texts, not
 * /texts?q=&page=1.
 */

const FIRST_PAGE = 1

export function useListUrl() {
  const route = useRoute()
  const router = useRouter()

  /** The page number written in the address, or the first page. */
  const pageInUrl = (): number => {
    const page = Number(route.query.page)
    return Number.isInteger(page) && page >= FIRST_PAGE ? page : FIRST_PAGE
  }

  /** The search written in the address, or an empty string. */
  const searchInUrl = (): string => String(route.query.q ?? '').trim()

  /**
   * Write what is being looked at into the address, without adding a step to
   * the browser's history: paging through a list is not somewhere the back
   * button should have to walk back through one page at a time.
   */
  const writeToUrl = (state: {page: number; search?: string}) => {
    const query: Record<string, string> = {}

    if (state.search) {
      query.q = state.search
    }

    if (state.page > FIRST_PAGE) {
      query.page = String(state.page)
    }

    router.replace({query})
  }

  return {pageInUrl, searchInUrl, writeToUrl}
}
