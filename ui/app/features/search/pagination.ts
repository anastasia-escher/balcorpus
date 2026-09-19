/**
 * Working out what a pager should show.
 *
 * The corpus answers with one page at a time, so the interface only ever
 * knows how many matches there are in total and which page it is looking at.
 * Everything a pager needs follows from those two numbers.
 */

/** How many matches one page of results holds. */
export const PAGE_SIZE = 25

/** How many page numbers are shown on either side of the current one. */
const NEIGHBOURS = 1

/** What a gap in the list of page numbers is called. */
export const ELLIPSIS = 'ellipsis'

export type PageItem = number | typeof ELLIPSIS

/**
 * How many pages the matches are spread over.
 *
 * Example: countPages(60, 25) -> 3
 */
export function countPages(totalResults: number, pageSize = PAGE_SIZE): number {
  if (totalResults <= 0 || pageSize <= 0) {
    return 0
  }

  return Math.ceil(totalResults / pageSize)
}

/**
 * The first and last match shown on a page, counting from one.
 *
 * Example: pageRange(3, 60, 25) -> { first: 51, last: 60 }
 */
export function pageRange(page: number, totalResults: number, pageSize = PAGE_SIZE) {
  const first = (page - 1) * pageSize + 1
  const last = Math.min(page * pageSize, totalResults)
  return {first, last}
}

/**
 * The page numbers to put in the pager, with gaps where numbers are left out.
 *
 * The first and last page are always there, so the ends of the results stay
 * one click away however long the list is.
 *
 * Example: pageItems(5, 10) -> [1, 'ellipsis', 4, 5, 6, 'ellipsis', 10]
 */
export function pageItems(currentPage: number, totalPages: number): PageItem[] {
  if (totalPages <= 1) {
    return totalPages === 1 ? [1] : []
  }

  const shown = new Set<number>([1, totalPages])
  for (let page = currentPage - NEIGHBOURS; page <= currentPage + NEIGHBOURS; page++) {
    if (page >= 1 && page <= totalPages) {
      shown.add(page)
    }
  }

  const pages = [...shown].sort((one, other) => one - other)

  const items: PageItem[] = []
  let previous = 0
  for (const page of pages) {
    if (previous && page - previous > 1) {
      items.push(ELLIPSIS)
    }
    items.push(page)
    previous = page
  }

  return items
}
