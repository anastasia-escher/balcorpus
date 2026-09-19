<script setup lang="ts">
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import SearchFormIntro from '~/components/search/SearchFormIntro.vue'
import {computed} from 'vue'
import {UD_TAG_OPTIONS} from '~/features/search/search.constants'
import {useSearchStore} from '~/stores/search'
import {useI18n} from 'vue-i18n'

const searchStore = useSearchStore()
const {t} = useI18n()
const udTagOptions = computed(() =>
  UD_TAG_OPTIONS.map(option => ({
    label: t(option.labelKey),
    value: option.value,
  }))
)

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
      <USelect
        v-model="searchStore.parent"
        :items="udTagOptions"
        :placeholder="t('search.forms.ud.parentPlaceholder')"
        class="search-control w-full"
        size="xl" />
      <SearchFormActions @reset="searchStore.resetSearchInput('ud')" />
    </form>
  </section>
</template>
