<script setup lang="ts">
import InputText from 'primevue/inputtext'
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import { useSearchStore } from '~/stores/search'

const searchStore = useSearchStore()

function submit() {
  searchStore.submitSearch('text')
}
</script>

<template>
  <section>
    <div class="mb-8 text-gray-900">
      <p class="font-bold text-lg mb-2">
        Text Search
        <span class="font-normal text-base text-gray-700">— search corpus by content or metadata.</span>
      </p>
      <p class="mb-2">
        Enter any phrase, sentence, or keyword to find matching text passages in the Macedonian Corpus.
      </p>
    </div>

    <form class="space-y-8" @submit.prevent="submit">
      <InputText
        v-model="searchStore.textQuery"
        class="w-full border-0 border-b-2 border-gray-300 focus:border-blue-700 p-3 text-lg"
        placeholder="Enter a word, phrase, or sentence…"
      />
      <SearchFormActions @reset="searchStore.resetSearchInput('text')" />
    </form>
  </section>
</template>
