<script setup lang="ts">
/**
 * How much of the catalogue the search can actually reach.
 *
 * The corpus is annotated one text at a time, so a search that finds nothing
 * may simply have looked at one text out of a hundred. Without this line a
 * reader would take an empty answer for "the word is not in the corpus".
 */
import {onMounted, ref} from 'vue'
import {useAPI} from '~/composables/useAPI'
import {useI18n} from 'vue-i18n'

/** Example: { total: 104, annotated: 1 } */
interface Coverage {
  total: number
  annotated: number
}

const {t} = useI18n()
const requestAPI = useAPI()

// Nothing is said until the numbers are known: a half-written sentence would
// be worse than none.
const coverage = ref<Coverage | null>(null)

onMounted(async () => {
  const {data} = await requestAPI<Coverage>('texts/coverage/')
  coverage.value = data.value
})
</script>

<template>
  <p v-if="coverage" class="mt-4 text-center text-xs text-stone-500">
    {{ t('search.coverage', {annotated: coverage.annotated, total: coverage.total}) }}
  </p>
</template>
