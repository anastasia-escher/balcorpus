export const SEARCH_KINDS = ['text', 'lemma', 'tag', 'ud'] as const

export type SearchKind = (typeof SEARCH_KINDS)[number]

export type SearchInputKey = 'textQuery' | 'lemma' | 'udTag' | 'parent'

export interface SearchTab {
  kind: SearchKind
  labelKey: string
}

export interface SearchOption {
  value: string
  labelKey: string
}

export interface SearchRequestField {
  inputKey: SearchInputKey
  parameterName: string
}

/**
 * One distance the nearby word may be looked for at, as the two ends of a
 * window of tokens. A negative number counts words in front of the match.
 *
 * Example: { value: 'exactly2Before', labelKey: '…', offsetFrom: -2, offsetTo: -2 }
 */
export interface ContextDistanceOption {
  value: string
  labelKey: string
  offsetFrom: number
  offsetTo: number
}

/** Where in a sentence a word stands, as [start, end] character positions. */
export type SentenceSpan = [number, number]

export interface SearchResult {
  id: number
  source: string | null
  diplomatic: string | null
  lemma: string | null
  pos_tag: string | null
  ud_type: string | null
  sentence_id: number
  text_id: string
  text_name: string
  speaker_id: string | null
  speaker_name: string | null
  source_sentence: string
  diplomatic_sentence: string
  /** The word found standing near the match, when the search asked for one. */
  context_ud_id: number | null
  context_source: string | null
  /** Where the two words stand in the sentence above, ready to be marked. */
  match_span: SentenceSpan | null
  context_span: SentenceSpan | null
}

export interface SearchResponse {
  count: number
  next: string | null
  previous: string | null
  results: SearchResult[]
}

/** One sentence standing next to a search result. */
export interface ContextSentence {
  sentence_id: number
  speaker_name: string | null
  source_sentence: string
}

export interface ContextResponse {
  sentence_id: number
  results: ContextSentence[]
}
