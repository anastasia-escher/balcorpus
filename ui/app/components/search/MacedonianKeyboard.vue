<script setup lang="ts">
/**
 * An on-screen keyboard with the Cyrillic letters of the corpus, and a warning
 * about letters that only look Cyrillic: "тој" with a Cyrillic ј and "тоj"
 * with a Latin j look the same, but are different words to the computer.
 *
 * Clicking a key sends the letter up with `insert`; the form decides where it
 * goes.
 */
import {useI18n} from 'vue-i18n'

const {t} = useI18n()
const emit = defineEmits<{
  insert: [letter: string]
}>()

// The Macedonian alphabet in its usual order, with ѐ and ѝ after е and и:
// they are written with their own characters, so a plain е or и won't
// find them. Only lowercase: the search ignores case.
const LETTERS = [
  'а', 'б', 'в', 'г', 'д', 'ѓ', 'е', 'ѐ', 'ж', 'з', 'ѕ', 'и', 'ѝ', 'ј', 'к', 'л', 'љ',
  'м', 'н', 'њ', 'о', 'п', 'р', 'с', 'т', 'ќ', 'у', 'ф', 'х', 'ц', 'ч', 'џ', 'ш',
]
</script>

<template>
  <div>
    <p class="text-xs leading-relaxed text-stone-500">{{ t('search.keyboard.disclaimer') }}</p>
    <!-- mousedown.prevent stops a key from taking the focus, so the cursor
         stays in the search field and typing can go on after a click. -->
    <div class="mt-3 flex flex-wrap gap-1.5">
      <button
        v-for="letter in LETTERS"
        :key="letter"
        type="button"
        class="h-9 w-9 rounded border border-stone-300 bg-white text-base text-stone-800 transition-colors hover:border-terracotta-600 hover:text-terracotta-700"
        @mousedown.prevent
        @click="emit('insert', letter)">
        {{ letter }}
      </button>
    </div>
  </div>
</template>
