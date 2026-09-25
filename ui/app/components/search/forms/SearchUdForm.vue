<script setup lang="ts">
import SearchContextFilter from '~/components/search/SearchContextFilter.vue'
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import SearchFormIntro from '~/components/search/SearchFormIntro.vue'
import {useUdTagOptions} from '~/composables/useUdTagOptions'
import {useSearchStore} from '~/stores/search'
import {useI18n} from 'vue-i18n'

const searchStore = useSearchStore()
const {t} = useI18n()
const udTagOptions = useUdTagOptions()

const submit = () => {
  searchStore.submitSearch('ud')
}
</script>

<template>
  <section>
    <SearchFormIntro :title="t('search.forms.ud.title')">
      <p>{{ t('search.forms.ud.summary') }}</p>
      <p>
        {{ t('search.forms.ud.descriptionOneBefore') }}
        <a
          class="text-terracotta-700 underline underline-offset-2 transition-colors hover:text-terracotta-800"
          href="https://universaldependencies.org/"
          target="_blank"
          rel="noopener">
          {{ t('search.forms.ud.universalDependencies') }}
        </a>
        {{ t('search.forms.ud.descriptionOneAfter') }}
      </p>
      <p>{{ t('search.forms.ud.descriptionTwo') }}</p>
      <p>{{ t('search.forms.ud.descriptionThree') }}</p>
    </SearchFormIntro>
    <form class="space-y-6" @submit.prevent="submit">
      <USelect
        v-model="searchStore.udTag"
        :items="udTagOptions"
        :placeholder="t('search.forms.ud.placeholder')"
        class="search-control w-full"
        size="xl" />
      <div>
        <USelect
          v-model="searchStore.parent"
          :items="udTagOptions"
          :placeholder="t('search.forms.ud.parentPlaceholder')"
          class="search-control w-full"
          size="xl" />
        <!-- The parent is optional, and a select cannot be emptied by itself. -->
        <button
          v-if="searchStore.parent"
          type="button"
          class="mt-1.5 text-xs text-stone-500 underline underline-offset-2 transition-colors hover:text-stone-900"
          @click="searchStore.parent = undefined">
          {{ t('search.forms.ud.clearParent') }}
        </button>
      </div>
      <SearchContextFilter />

      <SearchFormActions @reset="searchStore.resetSearchInput('ud')" />
    </form>
  </section>
</template>
