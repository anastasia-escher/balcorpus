<script setup lang="ts">
import SpeakerNames from '~/components/texts/SpeakerNames.vue'
import {readableList} from '~/features/texts/text-metadata'
import {computed} from 'vue'
import {useI18n} from 'vue-i18n'
import type {TextMetadata} from '~/features/texts/texts.types'

/** A text's title and metadata, standing at the head of the text itself. */
const props = defineProps<{
  text: TextMetadata
}>()

const {t} = useI18n()

/** The metadata as label/value pairs, leaving out what was never recorded. */
const facts = computed(() =>
  [
    {label: t('texts.columns.year'), value: props.text.text_date},
    {label: t('texts.columns.genre'), value: readableList(props.text.text_genre)},
    {label: t('texts.columns.variety'), value: readableList(props.text.variety)},
  ].filter(fact => Boolean(fact.value))
)
</script>

<template>
  <header class="border-b border-stone-200 pb-8">
    <h1 class="font-serif text-3xl leading-tight text-stone-900">{{ text.text_name }}</h1>

    <p class="mt-3 text-sm text-stone-700">
      <SpeakerNames :speakers="text.authors" />
    </p>

    <dl class="mt-4 flex flex-wrap gap-x-8 gap-y-2 text-xs text-stone-500">
      <div v-for="fact in facts" :key="fact.label" class="flex gap-2">
        <dt class="tracking-[0.08em] uppercase">{{ fact.label }}</dt>
        <dd class="text-stone-700">{{ fact.value }}</dd>
      </div>
    </dl>

    <p v-if="text.short_description" class="mt-4 max-w-2xl text-sm text-stone-600">
      {{ text.short_description }}
    </p>
  </header>
</template>
