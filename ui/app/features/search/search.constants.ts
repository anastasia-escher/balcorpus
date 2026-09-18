import type { SearchKind, SearchOption, SearchRequestField, SearchTab } from './search.types'

export const SEARCH_TABS: readonly SearchTab[] = [
  { kind: 'text', labelKey: 'search.tabs.text' },
  { kind: 'lemma', labelKey: 'search.tabs.lemma' },
  { kind: 'tag', labelKey: 'search.tabs.tag' },
  { kind: 'ud', labelKey: 'search.tabs.ud' },
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
