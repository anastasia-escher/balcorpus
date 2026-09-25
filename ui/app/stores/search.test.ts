import {beforeEach, describe, expect, it, vi} from 'vitest'
import {createPinia, setActivePinia} from 'pinia'

/**
 * A corpus that answers on a script: the broad search is slow, the narrow one
 * is quick. Started one after the other, they therefore come back the wrong
 * way round, which is the situation the store has to survive.
 *
 * ``vi.hoisted`` is what lets the mock below reach this, because vi.mock is
 * moved above the imports.
 */
const corpus = vi.hoisted(() => ({
  answers: {
    'Z*': {delay: 30, count: 3968}, // punctuation: many matches, slow
    'I*': {delay: 1, count: 106}, // interjections: few, quick
  } as Record<string, {delay: number; count: number}>,
  answered: [] as string[],
}))

vi.mock('~/composables/useAPI', () => ({
  useAPI: () => async (_endpoint: string, options: {params: Record<string, string>}) => {
    const pos = String(options.params.pos)
    const answer = corpus.answers[pos]
    if (!answer) {
      throw new Error(`The test corpus has no answer for pos=${pos}`)
    }
    const {delay, count} = answer

    await new Promise(resolve => setTimeout(resolve, delay))
    corpus.answered.push(pos)

    return {
      data: {value: {count, next: null, previous: null, results: []}},
      error: {value: null},
    }
  },
}))

const {useSearchStore} = await import('~/stores/search')

describe('useSearchStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    corpus.answered.length = 0
  })

  it('shows the search that was asked for last, however the answers arrive', async () => {
    const store = useSearchStore()

    store.selectMorphologyCategory('Z')
    const broadSearch = store.submitSearch('tag')
    store.selectMorphologyCategory('I')
    const narrowSearch = store.submitSearch('tag')

    await Promise.all([broadSearch, narrowSearch])

    // The first search answered last; its answer must not be the one on screen.
    expect(corpus.answered).toEqual(['I*', 'Z*'])
    expect(store.resultCount).toBe(106)
    expect(store.loading).toBe(false)
  })

  it('does not let a search still on its way fill in an emptied form', async () => {
    const store = useSearchStore()

    store.selectMorphologyCategory('Z')
    const slowSearch = store.submitSearch('tag')
    store.resetSearchInput('tag')
    await store.submitSearch('tag')
    await slowSearch

    expect(store.searchErrorKey).toBe('search.errors.empty')
    expect(store.resultCount).toBe(0)
    expect(store.hasSearched).toBe(false)
    expect(store.loading).toBe(false)
  })

  it('unticks "match inside words" on reset of the text tab', () => {
    const store = useSearchStore()

    store.textQuery = 'ица'
    store.partialText = true
    store.resetSearchInput('text')

    expect(store.textQuery).toBe('')
    expect(store.partialText).toBe(false)
  })
})
