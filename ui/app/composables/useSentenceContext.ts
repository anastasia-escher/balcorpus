import {ref} from 'vue'
import {useAPI} from '~/composables/useAPI'
import type {ContextResponse, ContextSentence, SearchResult} from '~/features/search/search.types'

/**
 * Reading the sentences that stand around a search result.
 *
 * A concordance line often does not settle what a form is doing, so each
 * result can be opened to show what came before and after it. The sentences
 * are fetched when they are first asked for and then kept, so closing and
 * opening a result again costs nothing.
 *
 * Two things are kept apart here. Whether a context is open belongs to one
 * result; the sentences belong to the sentence the result stands in. Three
 * nouns of sentence 42 are three results that open one by one, but they share
 * one request for the sentences around 42.
 */

/** What identifies one result's context: the sentence, inside its text. */
function contextKey(result: SearchResult): string {
  return `${result.text_id}:${result.sentence_id}`
}

export function useSentenceContext() {
  const requestAPI = useAPI()

  const sentencesByContext = ref<Record<string, ContextSentence[]>>({})
  const loadingContexts = ref<Record<string, boolean>>({})
  // The open results, as {result id: its context key}, e.g. {596987: 'panov_pechalbari_1936:42'}.
  // The key is kept so that a failed request can close every result waiting for it.
  const openResults = ref<Record<number, string>>({})

  const isOpen = (result: SearchResult) => result.id in openResults.value

  const isLoading = (result: SearchResult) =>
    Boolean(loadingContexts.value[contextKey(result)])

  const sentencesFor = (result: SearchResult): ContextSentence[] =>
    sentencesByContext.value[contextKey(result)] ?? []

  /** Close the context of every result waiting for this sentence. */
  const closeResultsOf = (key: string) => {
    for (const [resultId, resultKey] of Object.entries(openResults.value)) {
      if (resultKey === key) {
        delete openResults.value[Number(resultId)]
      }
    }
  }

  const fetchContext = async (result: SearchResult) => {
    const key = contextKey(result)
    loadingContexts.value[key] = true

    try {
      const {data, error} = await requestAPI<ContextResponse>('sentences/context/', {
        params: {
          text: result.text_id,
          sentence: String(result.sentence_id),
        },
      })

      // A failed request is not remembered, and the context is closed again:
      // left open, it would read as "no sentences around this one". The error
      // itself has already been shown, and opening the result tries once more.
      if (error.value || !data.value) {
        closeResultsOf(key)
        return
      }

      sentencesByContext.value[key] = data.value.results
    } finally {
      loadingContexts.value[key] = false
    }
  }

  /** Open a result's context, fetching it the first time it is asked for. */
  const toggleContext = async (result: SearchResult) => {
    if (isOpen(result)) {
      delete openResults.value[result.id]
      return
    }

    const key = contextKey(result)
    openResults.value[result.id] = key

    const alreadyFetched = key in sentencesByContext.value
    const alreadyLoading = Boolean(loadingContexts.value[key])

    if (!alreadyFetched && !alreadyLoading) {
      await fetchContext(result)
    }
  }

  /**
   * Close every context, for a new search or a new page.
   *
   * The fetched sentences are kept: they are still right, and a result that
   * turns up again opens without another request.
   */
  const closeAll = () => {
    openResults.value = {}
  }

  return {isOpen, isLoading, sentencesFor, toggleContext, closeAll}
}
