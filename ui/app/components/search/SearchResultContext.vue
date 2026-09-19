<script setup lang="ts">
import {useI18n} from 'vue-i18n'
import type {ContextSentence} from '~/features/search/search.types'

/**
 * The sentences standing around a result, with the result itself set apart
 * so the eye finds it again after reading the ones before it.
 */
defineProps<{
  sentences: ContextSentence[]
  matchedSentenceId: number
  loading: boolean
}>()

const {t} = useI18n()
</script>

<template>
  <div class="mt-3 border-l-2 border-stone-200 pl-4">
    <p v-if="loading" class="text-xs text-stone-500">
      {{ t('search.context.loading') }}
    </p>

    <p v-else-if="!sentences.length" class="text-xs text-stone-500">
      {{ t('search.context.empty') }}
    </p>

    <ol v-else class="space-y-1.5">
      <li
        v-for="sentence in sentences"
        :key="sentence.sentence_id"
        class="font-serif text-sm leading-relaxed"
        :class="
          sentence.sentence_id === matchedSentenceId
            ? 'text-stone-800'
            : 'text-stone-500'
        ">
        <span class="mr-2 font-sans text-xs text-stone-400">{{ sentence.sentence_id }}</span>
        {{ sentence.source_sentence }}
      </li>
    </ol>
  </div>
</template>
