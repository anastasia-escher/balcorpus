import type { ContextDistanceOption, SearchKind, SearchOption, SearchRequestField, SearchTab } from './search.types'

/** How many matches one page of results holds. */
export const SEARCH_PAGE_SIZE = 25

/**
 * The most matches the corpus puts into one Excel file. A copy of MAX_ROWS in
 * api/app/core/processing/search_export/search_xlsx.py: above it the server
 * refuses, so the page asks for a narrower search instead of offering a link.
 */
export const SEARCH_EXPORT_MAX_ROWS = 10_000

// The linguistic searches come first, the plain word search last.
export const SEARCH_TABS: readonly SearchTab[] = [
  { kind: 'lemma', labelKey: 'search.tabs.lemma' },
  { kind: 'tag', labelKey: 'search.tabs.tag' },
  { kind: 'ud', labelKey: 'search.tabs.ud' },
  { kind: 'text', labelKey: 'search.tabs.text' },
]

export const SEARCH_REQUEST_FIELDS: Record<SearchKind, readonly SearchRequestField[]> = {
  text: [{ inputKey: 'textQuery', parameterName: 'q' }],
  lemma: [{ inputKey: 'lemma', parameterName: 'lemma' }],
  // The morphology search has no field to read: it holds a part of speech and
  // the properties chosen under it, and the store turns those into the 'pos'
  // parameter itself. See buildSearchParameters.
  tag: [],
  ud: [
    { inputKey: 'udTag', parameterName: 'ud' },
    { inputKey: 'parent', parameterName: 'parent' },
  ],
}

/**
 * The parameter each way of describing a word is sent under when it describes
 * the *nearby* word rather than the searched one.
 */
export const CONTEXT_PARAMETER_BY_KIND: Record<SearchKind, string> = {
  text: 'near_q',
  lemma: 'near_lemma',
  tag: 'near_pos',
  ud: 'near_ud',
}

/**
 * How far from the match the nearby word may stand. The corpus looks at most
 * three words to either side, so these are all the distances there are.
 */
export const CONTEXT_DISTANCES: readonly ContextDistanceOption[] = [
  {value: 'anywhereNear', labelKey: 'search.nearbyWord.distances.anywhereNear', offsetFrom: -3, offsetTo: 3},
  {value: 'anywhereBefore', labelKey: 'search.nearbyWord.distances.anywhereBefore', offsetFrom: -3, offsetTo: -1},
  {value: 'exactly1Before', labelKey: 'search.nearbyWord.distances.exactly1Before', offsetFrom: -1, offsetTo: -1},
  {value: 'exactly2Before', labelKey: 'search.nearbyWord.distances.exactly2Before', offsetFrom: -2, offsetTo: -2},
  {value: 'exactly3Before', labelKey: 'search.nearbyWord.distances.exactly3Before', offsetFrom: -3, offsetTo: -3},
  {value: 'anywhereAfter', labelKey: 'search.nearbyWord.distances.anywhereAfter', offsetFrom: 1, offsetTo: 3},
  {value: 'exactly1After', labelKey: 'search.nearbyWord.distances.exactly1After', offsetFrom: 1, offsetTo: 1},
  {value: 'exactly2After', labelKey: 'search.nearbyWord.distances.exactly2After', offsetFrom: 2, offsetTo: 2},
  {value: 'exactly3After', labelKey: 'search.nearbyWord.distances.exactly3After', offsetFrom: 3, offsetTo: 3},
]

/** The distance a context condition starts out with: anywhere close by. */
export const DEFAULT_CONTEXT_DISTANCE = 'anywhereNear'

export const findContextDistance = (value: string): ContextDistanceOption | undefined =>
  CONTEXT_DISTANCES.find(distance => distance.value === value)

export const UD_TAG_OPTIONS: readonly SearchOption[] = [
  { labelKey: 'search.udTags.root', value: 'root' },
  { labelKey: 'search.udTags.acl', value: 'acl' },
  { labelKey: 'search.udTags.advcl', value: 'advcl' },
  { labelKey: 'search.udTags.advmod', value: 'advmod' },
  { labelKey: 'search.udTags.amod', value: 'amod' },
  { labelKey: 'search.udTags.aux', value: 'aux' },
  { labelKey: 'search.udTags.case', value: 'case' },
  { labelKey: 'search.udTags.cc', value: 'cc' },
  { labelKey: 'search.udTags.cop', value: 'cop' },
  { labelKey: 'search.udTags.det', value: 'det' },
  { labelKey: 'search.udTags.discourse', value: 'discourse' },
  { labelKey: 'search.udTags.fixed', value: 'fixed' },
  { labelKey: 'search.udTags.mark', value: 'mark' },
  { labelKey: 'search.udTags.nsubj', value: 'nsubj' },
  { labelKey: 'search.udTags.nmod', value: 'nmod' },
  { labelKey: 'search.udTags.nummod', value: 'nummod' },
  { labelKey: 'search.udTags.obj', value: 'obj' },
  { labelKey: 'search.udTags.obl', value: 'obl' },
  { labelKey: 'search.udTags.orphan', value: 'orphan' },
  { labelKey: 'search.udTags.punct', value: 'punct' },
  { labelKey: 'search.udTags.reparandum', value: 'reparandum' },
  { labelKey: 'search.udTags.vocative', value: 'vocative' },
]
