import {computed} from 'vue'
import {useI18n} from 'vue-i18n'
import {UD_TAG_OPTIONS} from '~/features/search/search.constants'

/**
 * The Universal Dependencies relations as choices for a select, with their
 * labels in the reader's language.
 *
 * Example: [{label: 'nominal subject', value: 'nsubj'}, ...]
 */
export function useUdTagOptions() {
  const {t} = useI18n()

  return computed(() =>
    UD_TAG_OPTIONS.map(option => ({
      label: t(option.labelKey),
      value: option.value,
    }))
  )
}
