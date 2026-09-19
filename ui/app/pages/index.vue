<script setup lang="ts">
import SearchResults from '~/components/search/SearchResults.vue'
import SearchTabs from '~/components/search/SearchTabs.vue'
import SearchLemmaForm from '~/components/search/forms/SearchLemmaForm.vue'
import SearchPosForm from '~/components/search/forms/SearchPosForm.vue'
import SearchTextForm from '~/components/search/forms/SearchTextForm.vue'
import SearchUdForm from '~/components/search/forms/SearchUdForm.vue'
import {useSearchStore} from '~/stores/search'
import {useI18n} from 'vue-i18n'

const searchStore = useSearchStore()
const {t} = useI18n()
</script>

<template>
  <article class="pb-24">
    <div class="relative h-80 overflow-hidden md:h-[26rem]">
      <img class="h-full w-full object-cover" src="/assets/images/mac.jpeg" :alt="t('home.coverAlt')" />
      <!-- A warm veil keeps the photograph quiet and the title readable on it. -->
      <div class="absolute inset-0 bg-terracotta-950/55" />
      <div class="absolute inset-0 flex flex-col items-center justify-center px-6 pt-14 text-center">
        <h1 class="font-serif text-3xl leading-tight text-paper md:text-5xl">
          {{ t('home.title') }}
        </h1>
        <p class="mt-4 max-w-xl text-sm text-stone-200 md:text-base">
          {{ t('home.subtitle') }}
        </p>
      </div>
    </div>

    <div class="mx-auto max-w-3xl px-6">
      <!-- z-10 keeps the panel above the cover photograph it overlaps. -->
      <div
        class="relative z-10 -mt-10 rounded-sm border border-stone-200 bg-white px-6 py-8 shadow-sm md:px-10 md:py-10">
        <SearchTabs />
        <div class="mt-8">
          <SearchTextForm v-if="searchStore.activeSearchKind === 'text'" />
          <SearchLemmaForm v-else-if="searchStore.activeSearchKind === 'lemma'" />
          <SearchPosForm v-else-if="searchStore.activeSearchKind === 'tag'" />
          <SearchUdForm v-else />
        </div>
      </div>

      <SearchResults />
    </div>
  </article>
</template>
