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
 */

/** What identifies one result's context: the sentence, inside its text. */
function contextKey(result: SearchResult): string {
  return `${result.text_id}:${result.sentence_id}`
}

export function useSentenceContext() {
  const requestAPI = useAPI()

  const sentencesByResult = ref<Record<string, ContextSentence[]>>({})
  const openResults = ref<Record<string, boolean>>({})
  const loadingResults = ref<Record<string, boolean>>({})

  const isOpen = (result: SearchResult) => Boolean(openResults.value[contextKey(result)])

  const isLoading = (result: SearchResult) =>
    Boolean(loadingResults.value[contextKey(result)])

  const sentencesFor = (result: SearchResult): ContextSentence[] =>
    sentencesByResult.value[contextKey(result)] ?? []

  const fetchContext = async (result: SearchResult) => {
    const key = contextKey(result)
    loadingResults.value[key] = true

    try {
      const {data} = await requestAPI<ContextResponse>('sentences/context/', {
        params: {
          text: result.text_id,
          sentence: String(result.sentence_id),
        },
      })

      sentencesByResult.value[key] = data.value?.results ?? []
    } finally {
      loadingResults.value[key] = false
    }
  }

  /** Open a result's context, fetching it the first time it is asked for. */
  const toggleContext = async (result: SearchResult) => {
    const key = contextKey(result)
    openResults.value[key] = !openResults.value[key]

    if (openResults.value[key] && !(key in sentencesByResult.value)) {
      await fetchContext(result)
    }
  }

  return {isOpen, isLoading, sentencesFor, toggleContext}
}
