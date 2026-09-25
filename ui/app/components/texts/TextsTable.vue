<script setup lang="ts">
import SpeakerNames from '~/components/texts/SpeakerNames.vue'
import {MISSING_VALUE, readableList} from '~/features/texts/text-metadata'
import {useI18n} from 'vue-i18n'
import type {TextMetadata} from '~/features/texts/texts.types'

/**
 * The corpus's texts as a table of their metadata, set like a printed
 * catalogue: hairline rules between rows, no vertical lines, plenty of air.
 */
defineProps<{
  texts: TextMetadata[]
}>()

const {t} = useI18n()

/** The column headings, in order, as keys under texts.columns. */
const COLUMNS = ['title', 'author', 'year', 'genre', 'variety']
</script>

<template>
  <!-- A table does not fold, so on a narrow screen it scrolls sideways
       instead of squeezing the titles into single letters. -->
  <div class="overflow-x-auto">
    <table class="w-full min-w-3xl border-collapse text-left">
      <thead>
        <tr class="border-b border-stone-300">
          <th
            v-for="column in COLUMNS"
            :key="column"
            class="px-3 py-3 text-xs font-medium tracking-[0.08em] text-stone-500 uppercase">
            {{ t(`texts.columns.${column}`) }}
          </th>
        </tr>
      </thead>

      <tbody class="divide-y divide-stone-200">
        <tr v-for="text in texts" :key="text.text_id" class="transition-colors hover:bg-paper-dark">
          <td class="px-3 py-4 font-serif text-base leading-snug text-stone-900">
            {{ text.text_name }}
            <!-- Only the annotated texts can be searched, and today that is
                 one text in a hundred, so the mark goes on those. -->
            <span
              v-if="text.is_annotated"
              class="ml-2 rounded-sm bg-terracotta-50 px-1.5 py-0.5 align-middle font-sans text-[0.625rem] tracking-[0.08em] text-terracotta-700 uppercase">
              {{ t('texts.annotated') }}
            </span>
          </td>
          <td class="px-3 py-4 text-sm text-stone-700">
            <SpeakerNames :speakers="text.authors" />
          </td>
          <td class="px-3 py-4 text-sm whitespace-nowrap text-stone-600">
            {{ text.text_date || MISSING_VALUE }}
          </td>
          <td class="px-3 py-4 text-sm text-stone-600">
            {{ readableList(text.text_genre) || MISSING_VALUE }}
          </td>
          <td class="px-3 py-4 text-sm text-stone-600">
            {{ readableList(text.variety) || MISSING_VALUE }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
