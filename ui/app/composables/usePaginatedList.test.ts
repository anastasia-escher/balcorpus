import {beforeEach, describe, expect, it, vi} from 'vitest'

/**
 * A corpus that fails every page but the first with a chosen status, and
 * notes which pages it was asked for.
 */
const corpus = vi.hoisted(() => ({
  failureStatus: 404,
  askedPages: [] as (string | undefined)[],
}))

vi.mock('~/composables/useAPI', () => ({
  useAPI: () => async (_endpoint: string, options: {params: Record<string, string>}) => {
    corpus.askedPages.push(options.params.page)

    if (options.params.page !== '1') {
      return {data: {value: null}, error: {value: {status: corpus.failureStatus}}}
    }

    return {
      data: {value: {count: 1, next: null, previous: null, results: ['Печалбари']}},
      error: {value: null},
    }
  },
}))

const {usePaginatedList} = await import('~/composables/usePaginatedList')

describe('usePaginatedList.load with a page named in the link', () => {
  beforeEach(() => {
    corpus.askedPages = []
  })

  it('opens at the first page when the named page does not exist', async () => {
    corpus.failureStatus = 404
    const list = usePaginatedList<string>('texts/', 25)

    await list.load({}, 3)

    expect(corpus.askedPages).toEqual(['3', '1'])
    expect(list.failed.value).toBe(false)
    expect(list.items.value).toEqual(['Печалбари'])
  })

  it('does not ask again when the server fails', async () => {
    corpus.failureStatus = 500
    const list = usePaginatedList<string>('texts/', 25)

    await list.load({}, 3)

    expect(corpus.askedPages).toEqual(['3'])
    expect(list.failed.value).toBe(true)
  })
})
