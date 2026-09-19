import {TEXT_SENTENCES_PAGE_SIZE} from '~/features/texts/texts.constants'
import {usePaginatedList} from '~/composables/usePaginatedList'
import type {TextSentence} from '~/features/texts/texts.types'

/**
 * One text, read a page of sentences at a time.
 *
 * A text of average length runs to thousands of tokens, so it never arrives
 * in one piece; the page number is how far into the text the reader is.
 */
export function useTextSentences() {
  const sentences = usePaginatedList<TextSentence>('sentences/', TEXT_SENTENCES_PAGE_SIZE)

  /** Open a text, at its beginning unless a page is named. */
  const openText = (textId: string, startPage?: number) => sentences.load({text: textId}, startPage)

  return {...sentences, openText}
}
