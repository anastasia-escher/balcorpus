<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'

const udTagOptions = [
  { label: 'root: sentence root', value: 'root' },
  { label: 'acl: adnominal clause root', value: 'acl' },
  { label: 'advcl: adverbial clause root', value: 'advcl' },
  { label: 'advmod: adverbial modifier', value: 'advmod' },
  { label: 'amod: adjectival modifier', value: 'amod' },
  { label: 'aux: auxiliary', value: 'aux' },
  { label: 'case: analytic dependency marker', value: 'case' },
  { label: 'cc: coordinating conjunction', value: 'cc' },
  { label: 'cop: copula', value: 'cop' },
  { label: 'det: determiner', value: 'det' },
  { label: 'discourse: discourse marker', value: 'discourse' },
  { label: 'fixed: element of multiple word expression', value: 'fixed' },
  { label: 'mark: subordinating conjunction/marker', value: 'mark' },
  { label: 'nsubj: subject of the main sentence', value: 'nsubj' },
  { label: 'nmod: nominal modifier', value: 'nmod' },
  { label: 'nummod: numeric modifier', value: 'nummod' },
  { label: 'obj: direct object', value: 'obj' },
  { label: 'obl: oblique argument', value: 'obl' },
  { label: 'orphan: orphaned element (no direct head)', value: 'orphan' },
  { label: 'punct: punctuation', value: 'punct' },
  { label: 'reparandum: stricken tokens (reparanda)', value: 'reparandum' },
  { label: 'vocative: vocative element', value: 'vocative' },
]

const udTag = ref(null)
const parent = ref(null)
const diplomatic = ref(null)
const transcription = ref(null)

const emit = defineEmits(['search'])

const onSubmit = () => {
  emit('search', {
    udTag: udTag.value,
    parent: parent.value,
    diplomatic: diplomatic.value,
    transcription: transcription.value,
  })
}
const onReset = () => {
  udTag.value = null
  parent.value = null
  diplomatic.value = null
  transcription.value = null
}
</script>

<template>
  <section>
    <div class="mb-8 text-gray-900">
      <p class="font-bold text-lg mb-2">
        UD Tag
        <span class="font-normal text-base text-gray-700">
          — search tokens by syntactic annotation.
        </span>
      </p>
      <p class="mb-2">
        Each sentence is syntactically annotated by the
        <a class="text-blue-700 underline" href="https://universaldependencies.org/" target="_blank" rel="noopener">Universal Dependencies</a>
        standard.<br />
        Each token is given an ID according to the position in the sentence.
      </p>
      <p class="mb-2">
        For each token, a dependency on other elements within the sentence is declared by these ids, as well as by the character of the dependency.
      </p>
      <p class="mb-2">
        One token in each sentence is marked as its root, usually representing the most verbal element.
      </p>
    </div>
    <form class="space-y-8" @submit.prevent="onSubmit">
      <div>
        <Dropdown
          v-model="udTag"
          :options="udTagOptions"
          option-label="label"
          option-value="value"
          placeholder="Select an UD tag"
             class="w-full border-0 border-b-2 border-gray-300 focus:border-blue-700 p-3 text-lg"
        />
      </div>
      <div>
        <Dropdown
          v-model="parent"
          :options="udTagOptions"
          option-label="label"
          option-value="value"
          placeholder="UD of parent (optional)"
            class="w-full border-0 border-b-2 border-gray-300 focus:border-blue-700 p-3 text-lg"
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
