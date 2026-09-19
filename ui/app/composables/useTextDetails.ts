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

  const loadText = async (textId: string) => {
    loading.value = true

    try {
      const {data} = await requestAPI<TextMetadata>(`texts/${textId}/`)
      text.value = data.value
    } finally {
      loading.value = false
    }
  }

  return {text, loading, loadText}
}
