<script setup lang="ts">
import InputText from 'primevue/inputtext'
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import { useSearchStore } from '~/stores/search'
import { useI18n } from 'vue-i18n'

const searchStore = useSearchStore()
const { t } = useI18n()

const submit = () => {
  searchStore.submitSearch('tag')
}
</script>

<template>
  <section>
    <div class="mb-8 text-gray-900">
      <p class="font-bold text-lg mb-2">
        {{ t('search.forms.tag.title') }}
        <span class="font-normal text-base text-gray-700">
          — {{ t('search.forms.tag.summary') }}
        </span>
      </p>
      <p class="mb-2">
        {{ t('search.forms.tag.descriptionOneBefore') }}
        <a class="text-blue-700 underline" href="http://nl.ijs.si/ME/V3/msd/html/msd-mk.html" target="_blank" rel="noopener">{{ t('search.forms.tag.multtextEast') }}</a>
        {{ t('search.forms.tag.descriptionOneAfter') }}
      </p>
      <p class="mb-2">
        {{ t('search.forms.tag.descriptionTwo') }}
      </p>
      <p class="mb-2">
        {{ t('search.forms.tag.descriptionThree') }}
      </p>
    </div>

    <form class="space-y-8" @submit.prevent="submit">
      <InputText
        v-model="searchStore.posQuery"
        class="w-full border-0 border-b-2 border-gray-300 focus:border-blue-700 p-3 text-lg"
        :placeholder="t('search.forms.tag.placeholder')"
      />
      <SearchFormActions @reset="searchStore.resetSearchInput('tag')" />
    </form>
  </section>
</template>
