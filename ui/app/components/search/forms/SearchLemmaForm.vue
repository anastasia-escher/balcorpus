<script setup lang="ts">
import SearchContextFilter from '~/components/search/SearchContextFilter.vue'
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import SearchFormIntro from '~/components/search/SearchFormIntro.vue'
import MacedonianKeyboard from '~/components/search/MacedonianKeyboard.vue'
import {useSearchStore} from '~/stores/search'
import {useI18n} from 'vue-i18n'
import {useTemplateRef} from 'vue'

const searchStore = useSearchStore()
const {t} = useI18n()
// The keyboard needs the <input> itself to know where the cursor is.
const field = useTemplateRef('field')

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
        ref="field"
        v-model="searchStore.lemma"
        class="search-control w-full"
        size="xl"
        :placeholder="t('search.forms.lemma.placeholder')" />
      <MacedonianKeyboard v-model="searchStore.lemma" :input="field?.inputRef" />
      <SearchContextFilter />

      <SearchFormActions @reset="searchStore.resetSearchInput('lemma')" />
    </form>
  </section>
</template>
