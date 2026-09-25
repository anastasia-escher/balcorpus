import {beforeEach, describe, expect, it, vi} from 'vitest'
import type {SearchResult} from '~/features/search/search.types'

/**
 * A corpus that answers the context request on a script: it either gives two
 * sentences back or fails, and counts how often it was asked.
 */
const corpus = vi.hoisted(() => ({
  fails: false,
  requests: 0,
}))

vi.mock('~/composables/useAPI', () => ({
  useAPI: () => async () => {
    corpus.requests += 1

    if (corpus.fails) {
      return {data: {value: null}, error: {value: new Error('500')}}
    }

    return {
      data: {
        value: {
          sentence_id: 42,
          results: [
            {sentence_id: 41, speaker_name: null, source_sentence: 'Пред тоа.'},
            {sentence_id: 42, speaker_name: null, source_sentence: 'Самата реченица.'},
          ],
        },
      },
      error: {value: null},
    }
  },
}))

const {useSentenceContext} = await import('~/composables/useSentenceContext')

/** A result of sentence 42 of Печалбари; only what the context reads is filled in. */
const resultInSentence42 = (id: number) =>
  ({id, text_id: 'panov_pechalbari_1936', sentence_id: 42}) as SearchResult

describe('useSentenceContext', () => {
  beforeEach(() => {
    corpus.fails = false
    corpus.requests = 0
  })

  it('opens one result, not every result of the same sentence', async () => {
    const context = useSentenceContext()
    const first = resultInSentence42(1)
    const second = resultInSentence42(2)

    await context.toggleContext(first)

    expect(context.isOpen(first)).toBe(true)
    expect(context.isOpen(second)).toBe(false)
  })

  it('asks for the sentences of one sentence only once', async () => {
    const context = useSentenceContext()

    await context.toggleContext(resultInSentence42(1))
    await context.toggleContext(resultInSentence42(2))

    expect(corpus.requests).toBe(1)
    expect(context.sentencesFor(resultInSentence42(2))).toHaveLength(2)
  })

  it('closes everything for a new list, but keeps what it fetched', async () => {
    const context = useSentenceContext()
    const result = resultInSentence42(1)
    await context.toggleContext(result)

    context.closeAll()
    expect(context.isOpen(result)).toBe(false)

    await context.toggleContext(result)
    expect(corpus.requests).toBe(1)
  })

  it('closes the context again when the request fails, and tries again on the next click', async () => {
    const context = useSentenceContext()
    const result = resultInSentence42(1)

    corpus.fails = true
    await context.toggleContext(result)
    expect(context.isOpen(result)).toBe(false)

    corpus.fails = false
    await context.toggleContext(result)
    expect(context.isOpen(result)).toBe(true)
    expect(corpus.requests).toBe(2)
  })
})
