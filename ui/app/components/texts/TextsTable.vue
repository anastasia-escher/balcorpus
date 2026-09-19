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
          <td class="px-3 py-4 font-serif text-base leading-snug">
            <NuxtLink
              class="text-link transition-colors hover:text-link-hover"
              :to="`/texts/${text.text_id}`">
              {{ text.text_name }}
            </NuxtLink>
          </td>
          <td class="px-3 py-4 text-sm text-stone-700">
            <SpeakerNames :speakers="text.authors" />
          </td>
          <td class="px-3 py-4 text-sm whitespace-nowrap text-stone-600">
            {{ text.text_date || MISSING_VALUE }}
          </td>
          <td class="px-3 py-4 text-sm text-stone-600">
            {{ readableList(text.text_genre) }}
          </td>
          <td class="px-3 py-4 text-sm text-stone-600">
            {{ readableList(text.variety) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
