<script setup lang="ts">
/**
 * An on-screen keyboard with the Cyrillic letters of the corpus, and a warning
 * about letters that only look Cyrillic: "тој" with a Cyrillic ј and "тоj"
 * with a Latin j look the same, but are different words to the computer.
 *
 * The form binds its word with v-model and hands over its <input> element,
 * so a clicked letter lands where the cursor is, not always at the end.
 */
import {nextTick} from 'vue'
import {useI18n} from 'vue-i18n'

const {t} = useI18n()
const word = defineModel<string>({required: true})
// withoutDisclaimer: for a second keyboard on the same form, where the
// warning is already shown above the first one.
const props = defineProps<{
  input: HTMLInputElement | null | undefined
  withoutDisclaimer?: boolean
}>()

// The Macedonian alphabet in its usual order, with ѐ and ѝ after е and и:
// they are written with their own characters, so a plain е or и won't
// find them. Only lowercase: the search ignores case.
const LETTERS = [
  'а', 'б', 'в', 'г', 'д', 'ѓ', 'е', 'ѐ', 'ж', 'з', 'ѕ', 'и', 'ѝ', 'ј', 'к', 'л', 'љ',
  'м', 'н', 'њ', 'о', 'п', 'р', 'с', 'т', 'ќ', 'у', 'ф', 'х', 'ц', 'ч', 'џ', 'ш',
]

/**
 * Put the letter where the cursor is, replacing any selected text, and move
 * the cursor to just after it. Without the input element there is no cursor
 * to read, so the letter goes to the end.
 *
 * Example: word "тоа" with the cursor after "то", key ј → "тоја",
 * cursor after the ј.
 */
const insertLetter = async (letter: string) => {
  const start = props.input?.selectionStart ?? word.value.length
  const end = props.input?.selectionEnd ?? word.value.length

  word.value = word.value.slice(0, start) + letter + word.value.slice(end)

  // The field shows the new word only after Vue has redrawn it, and setting
  // its value puts the cursor at the end; so the cursor is moved afterwards.
  await nextTick()
  props.input?.setSelectionRange(start + 1, start + 1)
}
</script>

<template>
  <div>
    <p v-if="!withoutDisclaimer" class="mb-3 text-xs leading-relaxed text-stone-500">
      {{ t('search.keyboard.disclaimer') }}
    </p>
    <!-- mousedown.prevent stops a key from taking the focus, so the cursor
         stays in the search field and typing can go on after a click. -->
    <div class="flex flex-wrap gap-1.5">
      <button
        v-for="letter in LETTERS"
        :key="letter"
        type="button"
        class="h-9 w-9 rounded border border-stone-300 bg-white text-base text-stone-800 transition-colors hover:border-terracotta-600 hover:text-terracotta-700"
        @mousedown.prevent
        @click="insertLetter(letter)">
        {{ letter }}
      </button>
    </div>
  </div>
</template>
