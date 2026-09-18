<script setup lang="ts">
import InputText from 'primevue/inputtext'
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import { useSearchStore } from '~/stores/search'

const searchStore = useSearchStore()

function submit() {
  searchStore.submitSearch('lemma')
}
</script>

<template>
  <section>
    <div class="mb-8 text-gray-900">
      <p class="font-bold text-lg mb-2">
        Lemma
        <span class="font-normal text-base text-gray-700">
          — search tokens by lemma, i.e. basic or dictionary form of the word. Nouns are usually given in sg.nom
          (e.g. <em>slovo</em> 'word'), adjectives in m.sg.nom (e.g. <em>nov</em> 'new'), verbs in 1sg.prs
          (e.g. <em>stana</em> 'stand up').
        </span>
      </p>
    </div>

    <form class="space-y-8" @submit.prevent="submit">
      <InputText
        v-model="searchStore.lemma"
        class="w-full border-0 border-b-2 border-gray-300 focus:border-blue-700 p-3 text-lg"
        placeholder="Enter a lemma"
      />
      <SearchFormActions @reset="searchStore.resetSearchInput('lemma')" />
    </form>
  </section>
</template>
