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

    <form class="space-y-6" @submit.prevent="submit">
      <UInput
        v-model="searchStore.textQuery"
        class="search-control w-full"
        size="xl"
        :placeholder="t('search.forms.text.placeholder')" />
      <label class="flex cursor-pointer items-start gap-2 text-sm text-stone-600">
        <input
          v-model="searchStore.partialText"
          type="checkbox"
          class="mt-0.5 accent-terracotta-600" />
        <span>
          {{ t('search.forms.text.partial') }}
          <span class="block text-xs text-stone-400">
            {{ t('search.forms.text.partialHint') }}
          </span>
        </span>
      </label>

      <SearchFormActions @reset="searchStore.resetSearchInput('text')" />
    </form>
  </section>
</template>
