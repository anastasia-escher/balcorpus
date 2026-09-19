<script setup lang="ts">
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import SearchFormIntro from '~/components/search/SearchFormIntro.vue'
import {useSearchStore} from '~/stores/search'
import {useI18n} from 'vue-i18n'

const searchStore = useSearchStore()
const {t} = useI18n()

const submit = () => {
  searchStore.submitSearch('tag')
}
</script>

<template>
  <section>
    <SearchFormIntro :title="t('search.forms.tag.title')">
      <p>{{ t('search.forms.tag.summary') }}</p>
      <p>
        {{ t('search.forms.tag.descriptionOneBefore') }}
        <a
          class="text-terracotta-700 underline underline-offset-2 transition-colors hover:text-terracotta-800"
          href="http://nl.ijs.si/ME/V3/msd/html/msd-mk.html"
          target="_blank"
          rel="noopener">
          {{ t('search.forms.tag.multtextEast') }}
        </a>
        {{ t('search.forms.tag.descriptionOneAfter') }}
      </p>
      <p>{{ t('search.forms.tag.descriptionTwo') }}</p>
      <p>{{ t('search.forms.tag.descriptionThree') }}</p>
    </SearchFormIntro>

    <form class="space-y-6" @submit.prevent="submit">
      <UInput
        v-model="searchStore.posQuery"
        class="search-control w-full"
        size="xl"
        :placeholder="t('search.forms.tag.placeholder')" />
      <SearchFormActions @reset="searchStore.resetSearchInput('tag')" />
    </form>
  </section>
</template>
