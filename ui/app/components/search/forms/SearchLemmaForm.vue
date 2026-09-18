<script setup lang="ts">
import InputText from 'primevue/inputtext'
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import { useSearchStore } from '~/stores/search'
import { useI18n } from 'vue-i18n'

const searchStore = useSearchStore()
const { t } = useI18n()

const submit = () => {
  searchStore.submitSearch('lemma')
}
</script>

<template>
  <section>
    <div class="mb-8 text-gray-900">
      <p class="font-bold text-lg mb-2">
        {{ t('search.forms.lemma.title') }}
        <span class="font-normal text-base text-gray-700">
          — {{ t('search.forms.lemma.description') }}
        </span>
      </p>
    </div>

    <form class="space-y-8" @submit.prevent="submit">
      <InputText
        v-model="searchStore.lemma"
        class="w-full border-0 border-b-2 border-gray-300 focus:border-blue-700 p-3 text-lg"
        :placeholder="t('search.forms.lemma.placeholder')"
      />
      <SearchFormActions @reset="searchStore.resetSearchInput('lemma')" />
    </form>
  </section>
</template>
