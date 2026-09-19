<script setup lang="ts">
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

/** What is printed when the metadata simply has no value for a column. */
const MISSING_VALUE = '—'

/**
 * Some columns hold several values in one cell, separated by a semicolon:
 * "drama;prose", "standard;dialectal". They read better spaced out.
 *
 * Example: readable('drama;prose') -> 'drama, prose'
 */
const readable = (value: string | null) =>
  value ? value.split(';').map(part => part.trim()).filter(Boolean).join(', ') : MISSING_VALUE

/** The authors of a text, as one line. Every text so far has exactly one. */
const authorNames = (text: TextMetadata) =>
  text.authors.map(author => author.full_name).join(', ') || MISSING_VALUE
</script>

<template>
  <!-- A table does not fold, so on a narrow screen it scrolls sideways
       instead of squeezing the titles into single letters. -->
  <div class="overflow-x-auto">
    <table class="w-full min-w-3xl border-collapse text-left">
      <thead>
        <tr class="border-b border-stone-300">
          <th class="px-3 py-3 text-xs font-medium tracking-[0.08em] text-stone-500 uppercase">
            {{ t('texts.columns.title') }}
          </th>
          <th class="px-3 py-3 text-xs font-medium tracking-[0.08em] text-stone-500 uppercase">
            {{ t('texts.columns.author') }}
          </th>
          <th class="px-3 py-3 text-xs font-medium tracking-[0.08em] text-stone-500 uppercase">
            {{ t('texts.columns.year') }}
          </th>
          <th class="px-3 py-3 text-xs font-medium tracking-[0.08em] text-stone-500 uppercase">
            {{ t('texts.columns.genre') }}
          </th>
          <th class="px-3 py-3 text-xs font-medium tracking-[0.08em] text-stone-500 uppercase">
            {{ t('texts.columns.variety') }}
          </th>
        </tr>
      </thead>

      <tbody class="divide-y divide-stone-200">
        <tr v-for="text in texts" :key="text.text_id" class="transition-colors hover:bg-paper-dark">
          <td class="px-3 py-4 font-serif text-base leading-snug text-stone-900">
            {{ text.text_name }}
          </td>
          <td class="px-3 py-4 text-sm text-stone-700">
            {{ authorNames(text) }}
          </td>
          <td class="px-3 py-4 text-sm whitespace-nowrap text-stone-600">
            {{ text.text_date || MISSING_VALUE }}
          </td>
          <td class="px-3 py-4 text-sm text-stone-600">
            {{ readable(text.text_genre) }}
          </td>
          <td class="px-3 py-4 text-sm text-stone-600">
            {{ readable(text.variety) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
