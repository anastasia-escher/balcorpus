<script setup lang="ts">
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import SearchFormIntro from '~/components/search/SearchFormIntro.vue'
import {useSearchStore} from '~/stores/search'
import {useI18n} from 'vue-i18n'

const searchStore = useSearchStore()
const {t} = useI18n()

const submit = () => {
  searchStore.submitSearch('lemma')
}
</script>

<template>
  <section>
    <SearchFormIntro :title="t('search.forms.lemma.title')">
      <p>{{ t('search.forms.lemma.description') }}</p>
    </SearchFormIntro>

    <form class="space-y-6" @submit.prevent="submit">
      <UInput
        v-model="searchStore.lemma"
        class="search-control w-full"
        size="xl"
        :placeholder="t('search.forms.lemma.placeholder')" />
      <SearchFormActions @reset="searchStore.resetSearchInput('lemma')" />
    </form>
  </section>
</template>
