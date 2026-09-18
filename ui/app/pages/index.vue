<script setup lang="ts">
import SearchResults from '~/components/search/SearchResults.vue'
import SearchTabs from '~/components/search/SearchTabs.vue'
import SearchLemmaForm from '~/components/search/forms/SearchLemmaForm.vue'
import SearchPosForm from '~/components/search/forms/SearchPosForm.vue'
import SearchTextForm from '~/components/search/forms/SearchTextForm.vue'
import SearchUdForm from '~/components/search/forms/SearchUdForm.vue'
import { useSearchStore } from '~/stores/search'

const searchStore = useSearchStore()
</script>

<template>
  <section class="pb-24">
    <div class="h-64 lg:h-144">
      <img
        class="w-full h-full object-cover"
        src="/assets/images/mac.jpeg"
        alt="Corpus cover image"
      />
    </div>
    <div class="relative container px-4 mx-auto -mt-24">
      <div class="max-w-8xl px-4 pt-12 lg:pt-20 mx-auto bg-white rounded-2xl shadow-xl pb-24">
        <div class="max-w-2xl mb-12 mx-auto text-center">
          <h1 class="mb-8 text-4xl lg:text-6xl text-blue-800 font-extrabold font-heading tracking-tight">
            Corpus of Macedonian Language
          </h1>
          <SearchTabs />
        </div>
        <div class="max-w-2xl mx-auto -mb-6">
          <SearchTextForm v-if="searchStore.activeSearchKind === 'text'" />
          <SearchLemmaForm v-else-if="searchStore.activeSearchKind === 'lemma'" />
          <SearchPosForm v-else-if="searchStore.activeSearchKind === 'tag'" />
          <SearchUdForm v-else />
          <SearchResults />
        </div>
      </div>
    </div>
  </section>
</template>
