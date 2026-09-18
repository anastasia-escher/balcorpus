<script setup lang="ts">
import InputText from 'primevue/inputtext'
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import { useSearchStore } from '~/stores/search'

const searchStore = useSearchStore()

function submit() {
  searchStore.submitSearch('tag')
}
</script>

<template>
  <section>
    <div class="mb-8 text-gray-900">
      <p class="font-bold text-lg mb-2">
        PoS Tag
        <span class="font-normal text-base text-gray-700">
          — search tokens by tags reflecting part-of-speech category and morphological properties.
        </span>
      </p>
      <p class="mb-2">
        Morphological annotation follows the
        <a class="text-blue-700 underline" href="http://nl.ijs.si/ME/V3/msd/html/msd-mk.html" target="_blank" rel="noopener">MULTEXT-East</a>
        standard with minor modifications. The information is provided by a string of characters, reflecting the part-of-speech category (capital) and information marked by the inflection.
      </p>
      <p class="mb-2">
        The strings are specific for each part-of-speech category. For example, <em>slovesa</em> 'words' would be annotated as <strong>Nnpn</strong>, denoting category as "noun" and inflection (neutral gender, plural number, default/nominative case, not animated).
      </p>
      <p class="mb-2">
        It is possible to search for a full tag and for a part: for example, the query <strong>N</strong> will find all the nouns and the query <strong>Nf</strong> — all the feminine nouns. Also, you can replace a category tag with '?' in order to get any value, e.g. <strong>N?sny</strong> will return singular animate nouns in nominative of all genders.
      </p>
    </div>

    <form class="space-y-8" @submit.prevent="submit">
      <InputText
        v-model="searchStore.posQuery"
        class="w-full border-0 border-b-2 border-gray-300 focus:border-blue-700 p-3 text-lg"
        placeholder="Enter a PoS query (e. g. 'Nmnsny')"
      />
      <SearchFormActions @reset="searchStore.resetSearchInput('tag')" />
    </form>
  </section>
</template>
