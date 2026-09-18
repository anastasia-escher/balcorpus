import {computed} from 'vue'
import {useI18n} from 'vue-i18n'

export function useLang() {
  const {locale} = useI18n()
  const isRu = computed(() => locale.value === 'ru')
  const isEn = computed(() => locale.value === 'en')
  return {current: locale, isRu, isEn}
}
