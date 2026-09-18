import type { SearchKind, SearchRequestField, SearchTab } from './search.types'

export const SEARCH_TABS: readonly SearchTab[] = [
  { kind: 'text', label: 'By Full Text' },
  { kind: 'lemma', label: 'By Lemma' },
  { kind: 'tag', label: 'By Tag' },
  { kind: 'ud', label: 'By UD Tag' },
]

export const SEARCH_REQUEST_FIELDS: Record<SearchKind, readonly SearchRequestField[]> = {
  text: [{ inputKey: 'textQuery', parameterName: 'q' }],
  lemma: [{ inputKey: 'lemma', parameterName: 'lemma' }],
  tag: [{ inputKey: 'posQuery', parameterName: 'pos' }],
  ud: [
    { inputKey: 'udTag', parameterName: 'ud' },
    { inputKey: 'parent', parameterName: 'parent' },
  ],
}

export const UD_TAG_OPTIONS = [
  { label: 'root: sentence root', value: 'root' },
  { label: 'acl: adnominal clause root', value: 'acl' },
  { label: 'advcl: adverbial clause root', value: 'advcl' },
  { label: 'advmod: adverbial modifier', value: 'advmod' },
  { label: 'amod: adjectival modifier', value: 'amod' },
  { label: 'aux: auxiliary', value: 'aux' },
  { label: 'case: analytic dependency marker', value: 'case' },
  { label: 'cc: coordinating conjunction', value: 'cc' },
  { label: 'cop: copula', value: 'cop' },
  { label: 'det: determiner', value: 'det' },
  { label: 'discourse: discourse marker', value: 'discourse' },
  { label: 'fixed: element of multiple word expression', value: 'fixed' },
  { label: 'mark: subordinating conjunction/marker', value: 'mark' },
  { label: 'nsubj: subject of the main sentence', value: 'nsubj' },
  { label: 'nmod: nominal modifier', value: 'nmod' },
  { label: 'nummod: numeric modifier', value: 'nummod' },
  { label: 'obj: direct object', value: 'obj' },
  { label: 'obl: oblique argument', value: 'obl' },
  { label: 'orphan: orphaned element (no direct head)', value: 'orphan' },
  { label: 'punct: punctuation', value: 'punct' },
  { label: 'reparandum: stricken tokens (reparanda)', value: 'reparandum' },
  { label: 'vocative: vocative element', value: 'vocative' },
] as const
