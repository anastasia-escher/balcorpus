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
        ref="field"
        v-model="searchStore.textQuery"
        class="search-control w-full"
        size="xl"
        :placeholder="t('search.forms.text.placeholder')" />
      <MacedonianKeyboard v-model="searchStore.textQuery" :input="field?.inputRef" />
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

      <SearchContextFilter />

      <SearchFormActions @reset="searchStore.resetSearchInput('text')" />
    </form>
  </section>
</template>
