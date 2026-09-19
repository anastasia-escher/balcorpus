<script setup lang="ts">
import type {TextSentence} from '~/features/texts/texts.types'

/**
 * One sentence of a text, set the way an interlinear edition sets it: the
 * words on a line, and under each word, in grey, what the annotation says
 * about it. Punctuation is a word of its own in the corpus, so it stands in
 * the line like any other.
 */
defineProps<{
  sentence: TextSentence
  // Set only where the speaker changes, so a run of lines by one person is
  // not interrupted by their name over and over.
  showSpeaker: boolean
}>()

/** The word as it is written, whichever reading the corpus recorded. */
const wordForm = (token: {source: string | null; diplomatic: string | null}) =>
  token.source || token.diplomatic || ''
</script>

<template>
  <div class="flex gap-4">
    <!-- The sentence number is a fixed column, so the words of every sentence
         start on the same vertical line down the page. -->
    <span class="w-10 shrink-0 pt-1 text-right text-xs text-stone-400">
      {{ sentence.sentence_id }}
    </span>

    <div class="min-w-0 flex-1">
      <p v-if="showSpeaker && sentence.speaker" class="mb-1 text-xs tracking-[0.08em] text-stone-500 uppercase">
        {{ sentence.speaker.full_name }}
      </p>

      <div class="flex flex-wrap gap-x-3 gap-y-2">
        <span v-for="token in sentence.tokens" :key="token.ud_id" class="inline-flex flex-col">
          <span class="font-serif text-base leading-snug text-stone-900">
            {{ wordForm(token) }}
          </span>
          <span v-if="token.lemma" class="font-serif text-xs leading-tight text-stone-400">
            {{ token.lemma }}
          </span>
          <span v-if="token.pos_tag" class="text-[0.65rem] leading-tight text-stone-400">
            {{ token.pos_tag }}
          </span>
          <span v-if="token.ud_type" class="text-[0.65rem] leading-tight text-stone-400">
            {{ token.ud_type }}
          </span>
        </span>
      </div>
    </div>
  </div>
</template>
