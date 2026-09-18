<script setup lang="ts">
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import { UD_TAG_OPTIONS } from '~/features/search/search.constants'
import { useSearchStore } from '~/stores/search'

const searchStore = useSearchStore()

function submit() {
  searchStore.submitSearch('ud')
}
</script>

<template>
  <section>
    <div class="mb-8 text-gray-900">
      <p class="font-bold text-lg mb-2">
        UD Tag
        <span class="font-normal text-base text-gray-700">— search tokens by syntactic annotation.</span>
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
    <form class="search-form space-y-8" @submit.prevent="submit">
      <Dropdown
        v-model="searchStore.udTag"
        :options="UD_TAG_OPTIONS"
        option-label="label"
        option-value="value"
        placeholder="Select an UD tag"
        class="w-full border-0 border-b-2 border-gray-300 focus:border-blue-700 p-3 text-lg"
      />
      <Dropdown
        v-model="searchStore.parent"
        :options="UD_TAG_OPTIONS"
        option-label="label"
        option-value="value"
        placeholder="UD of parent (optional)"
        class="w-full border-0 border-b-2 border-gray-300 focus:border-blue-700 p-3 text-lg"
      />
      <SearchFormActions @reset="searchStore.resetSearchInput('ud')" />
    </form>
  </section>
</template>
