export const SEARCH_KINDS = ['text', 'lemma', 'tag', 'ud'] as const

export type SearchKind = (typeof SEARCH_KINDS)[number]

export type SearchInputKey = 'textQuery' | 'lemma' | 'posQuery' | 'udTag' | 'parent'

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
