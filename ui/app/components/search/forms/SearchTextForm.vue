<script setup lang="ts">
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import SearchFormIntro from '~/components/search/SearchFormIntro.vue'
import {useSearchStore} from '~/stores/search'
import {useI18n} from 'vue-i18n'

const searchStore = useSearchStore()
const {t} = useI18n()

const submit = () => {
  searchStore.submitSearch('text')
}
</script>

<template>
  <section>
    <SearchFormIntro :title="t('search.forms.text.title')">
      <p>{{ t('search.forms.text.summary') }}</p>
      <p>{{ t('search.forms.text.description') }}</p>
    </SearchFormIntro>

    <form class="space-y-8" @submit.prevent="submit">
      <UInput
        v-model="searchStore.textQuery"
        class="search-control w-full"
        size="xl"
        :placeholder="t('search.forms.text.placeholder')" />
      <SearchFormActions @reset="searchStore.resetSearchInput('text')" />
    </form>
  </section>
</template>
