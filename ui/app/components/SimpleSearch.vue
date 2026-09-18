<script setup lang="ts">
import { ref } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'


const textQuery = ref('')
const diplomatic = ref(null)
const transcription = ref(null)

const emit = defineEmits(['search'])

const onSubmit = () => {
  emit('search', {
    textQuery: textQuery.value,
    diplomatic: diplomatic.value,
    transcription: transcription.value,
  })
}
const onReset = () => {
  textQuery.value = ''
  diplomatic.value = null
  transcription.value = null
}
</script>

<template>
  <section>
    <div class="mb-8 text-gray-900">
      <p class="font-bold text-lg mb-2">
        Text Search
        <span class="font-normal text-base text-gray-700">
          — search corpus by content or metadata.
        </span>
      </p>
      <p class="mb-2">
        Enter any phrase, sentence, or keyword to find matching text passages in the Macedonian Corpus. You may also filter by transcription or diplomatic version.
      </p>
    </div>

    <form class="space-y-8" @submit.prevent="onSubmit">
      <div>
        <InputText
          v-model="textQuery"
          class="w-full border-0 border-b-2 border-gray-300 focus:border-blue-700 p-3 text-lg"
          placeholder="Enter a word, phrase, or sentence…"
        />
      </div>

      <div class="flex gap-4 mt-8">
        <Button
          type="submit"
          label="SUBMIT"
          class="px-6"
          severity="info"
        />
        <Button
          type="button"
          label="RESET"
          class="px-6"
          severity="secondary"
          outlined
          @click="onReset"
        />
      </div>
    </form>
  </section>
</template>

<style scoped>
form :deep(.p-dropdown) {
  border-radius: 0;
  border: none;
  border-bottom: 2px solid #d1d5db;
  box-shadow: none;
  min-height: 3rem;
  font-size: 1.125rem;
}
form :deep(.p-dropdown.p-focus) {
  border-bottom-color: #2563eb;
}
</style>
