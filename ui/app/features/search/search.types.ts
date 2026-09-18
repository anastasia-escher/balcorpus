export const SEARCH_KINDS = ['text', 'lemma', 'tag', 'ud'] as const

export type SearchKind = (typeof SEARCH_KINDS)[number]

export type SearchInputKey = 'textQuery' | 'lemma' | 'posQuery' | 'udTag' | 'parent'

export interface SearchTab {
  kind: SearchKind
  label: string
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
  text_id: number
  text_name: string
  speaker_id: string | null
  speaker_name: string | null
  source_sentence: string
  diplomatic_sentence: string
}

export interface SearchResponse {
  count: number
  results: SearchResult[]
}
