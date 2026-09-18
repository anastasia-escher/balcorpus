<script setup lang="ts">
import { ref } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'



const lemma = ref('')
const diplomatic = ref(null)
const transcription = ref(null)

const emit = defineEmits(['search'])

const onSubmit = () => {
  emit('search', {
    lemma: lemma.value,
    diplomatic: diplomatic.value,
    transcription: transcription.value,
  })
}

const onReset = () => {
  lemma.value = ''
  diplomatic.value = null
  transcription.value = null
}
</script>

<template>
  <section>
    <div class="mb-8 text-gray-900">
      <p class="font-bold text-lg mb-2">
        Lemma
        <span class="font-normal text-base text-gray-700">
          — search tokens by lemma, i.e. basic or dictionary form of the word. Nouns are usually given in sg.nom (e.g. <em>slovo</em> 'word'), adjectives in m.sg.nom (e.g. <em>nov</em> 'new'), verbs in 1sg.prs (e.g. <em>stana</em> 'stand up').
        </span>
      </p>
    </div>

    <form class="space-y-8" @submit.prevent="onSubmit">
      <div>
        <InputText
          v-model="lemma"
          class="w-full border-0 border-b-2 border-gray-300 focus:border-blue-700 p-3 text-lg"
          placeholder="Enter a lemma"
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
