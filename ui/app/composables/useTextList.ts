import {TEXTS_PAGE_SIZE} from '~/features/texts/texts.constants'
import {usePaginatedList} from '~/composables/usePaginatedList'
import type {TextMetadata} from '~/features/texts/texts.types'

/** The corpus's catalogue of texts, a page at a time. */
export function useTextList() {
  return usePaginatedList<TextMetadata>('texts/', TEXTS_PAGE_SIZE)
}
