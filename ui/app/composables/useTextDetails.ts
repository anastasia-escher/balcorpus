import {ref} from 'vue'
import {useAPI} from '~/composables/useAPI'
import type {TextMetadata} from '~/features/texts/texts.types'

/**
 * The metadata of one text: its title, who wrote it, when, in what variety.
 *
 * This is a single record fetched once, which is why it is not the same job
 * as reading the text's sentences.
 */
export function useTextDetails() {
  const requestAPI = useAPI()

  const text = ref<TextMetadata | null>(null)
  const loading = ref(false)
  // A text_id the corpus does not have: a typo in the address bar, or a link
  // from before the text was renamed. The page has to say so, because an
  // empty text and a text that does not exist look the same otherwise.
  const missing = ref(false)

  const loadText = async (textId: string) => {
    loading.value = true
    missing.value = false

    try {
      const {data, error} = await requestAPI<TextMetadata>(`texts/${textId}/`, {
        quietNotFound: true,
      })

      if (error.value || !data.value) {
        text.value = null
        missing.value = true
        return
      }

      text.value = data.value
    } finally {
      loading.value = false
    }
  }

  return {text, loading, missing, loadText}
}
