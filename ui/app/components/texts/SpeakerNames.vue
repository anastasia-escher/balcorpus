<script setup lang="ts">
import SpeakerDetailsModal from '~/components/texts/SpeakerDetailsModal.vue'
import {MISSING_VALUE} from '~/features/texts/text-metadata'
import {hasSpeakerDetails} from '~/features/texts/speaker'
import {ref} from 'vue'
import type {SpeakerDetails} from '~/features/texts/texts.types'

/**
 * A text's people, each name opening what the corpus records about them.
 *
 * Both the catalogue and a text's own page print the same names and want the
 * same window behind them, so the pair lives here once.
 */
defineProps<{
  speakers: SpeakerDetails[]
}>()

// Whose details the window is showing; null while it is closed.
const selectedSpeaker = ref<SpeakerDetails | null>(null)
</script>

<template>
  <span>
    <span v-if="!speakers.length">{{ MISSING_VALUE }}</span>

    <!-- A name is only worth clicking when the corpus records something about
         the person besides the name itself. -->
    <template v-for="(speaker, position) in speakers" :key="speaker.speaker_id">
      <span v-if="position > 0">, </span>
      <button
        v-if="hasSpeakerDetails(speaker)"
        type="button"
        class="text-link transition-colors hover:text-link-hover"
        @click="selectedSpeaker = speaker">
        {{ speaker.full_name }}
      </button>
      <span v-else>{{ speaker.full_name }}</span>
    </template>

    <SpeakerDetailsModal :speaker="selectedSpeaker" @close="selectedSpeaker = null" />
  </span>
</template>
