<script setup lang="ts">
import {birthplace, education, languages} from '~/features/texts/speaker'
import {computed} from 'vue'
import {useI18n} from 'vue-i18n'
import type {SpeakerDetails} from '~/features/texts/texts.types'

/**
 * What the corpus records about one person, in a window over the table.
 *
 * The window is open exactly when it has been handed a speaker, so the table
 * only has to say whose details it wants to see.
 */
const props = defineProps<{
  speaker: SpeakerDetails | null
}>()

const emit = defineEmits<{close: []}>()

const {t} = useI18n()

const open = computed({
  get: () => props.speaker !== null,
  set: (wanted: boolean) => {
    if (!wanted) {
      emit('close')
    }
  },
})

/** The recorded fields as label/value pairs, leaving out what is empty. */
const details = computed(() => {
  const speaker = props.speaker
  if (!speaker) {
    return []
  }

  return [
    {label: t('speaker.labels.birthName'), value: speaker.birth_name},
    {label: t('speaker.labels.birthyear'), value: speaker.birthyear},
    {label: t('speaker.labels.gender'), value: speaker.gender},
    {label: t('speaker.labels.placeOfBirth'), value: birthplace(speaker)},
    {label: t('speaker.labels.municipality'), value: speaker.municipality},
    {label: t('speaker.labels.dialectRegion'), value: speaker.dialect_region},
    {label: t('speaker.labels.education'), value: education(speaker)},
    {label: t('speaker.labels.languages'), value: languages(speaker)},
    {label: t('speaker.labels.notes'), value: speaker.notes},
  ].filter(entry => Boolean(entry.value))
})
</script>

<template>
  <UModal v-model:open="open" :title="speaker?.full_name ?? ''">
    <template #body>
      <dl v-if="details.length" class="divide-y divide-stone-200">
        <div v-for="entry in details" :key="entry.label" class="flex gap-4 py-2.5 first:pt-0">
          <dt class="w-40 shrink-0 text-xs tracking-[0.08em] text-stone-500 uppercase">
            {{ entry.label }}
          </dt>
          <dd class="text-sm text-stone-800">{{ entry.value }}</dd>
        </div>
      </dl>

      <p v-else class="text-sm text-stone-600">{{ t('speaker.empty') }}</p>
    </template>
  </UModal>
</template>
