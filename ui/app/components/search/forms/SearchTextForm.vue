<script setup lang="ts">
import SearchFormActions from '~/components/search/SearchFormActions.vue'
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
    <div class="mb-8 text-gray-900">
      <p class="font-bold text-lg mb-2">
        {{ t('search.forms.text.title') }}
        <span class="font-normal text-base text-gray-700">— {{ t('search.forms.text.summary') }}</span>
      </p>
      <p class="mb-2">
        {{ t('search.forms.text.description') }}
      </p>
    </div>

    <form class="space-y-8" @submit.prevent="submit">
      <UInput
        v-model="searchStore.textQuery"
        class="w-full"
        size="xl"
        :placeholder="t('search.forms.text.placeholder')" />
      <SearchFormActions @reset="searchStore.resetSearchInput('text')" />
    </form>
  </section>
</template>
