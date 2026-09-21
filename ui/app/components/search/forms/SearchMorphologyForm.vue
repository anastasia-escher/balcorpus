<script setup lang="ts">
/**
 * Searching by morphology without knowing the tag language: a part of speech,
 * and then a dropdown for each property that part of speech can carry.
 */
import MorphologyFields from '~/components/search/MorphologyFields.vue'
import SearchContextFilter from '~/components/search/SearchContextFilter.vue'
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import SearchFormIntro from '~/components/search/SearchFormIntro.vue'
import {useSearchStore} from '~/stores/search'
import {useI18n} from 'vue-i18n'

const searchStore = useSearchStore()
const {t} = useI18n()

const submit = () => {
  searchStore.submitSearch('tag')
}
</script>

<template>
  <section>
    <SearchFormIntro :title="t('search.forms.tag.title')">
      <p>{{ t('search.forms.tag.summary') }}</p>
      <p>
        {{ t('search.forms.tag.descriptionOneBefore') }}
        <a
          class="text-terracotta-700 underline underline-offset-2 transition-colors hover:text-terracotta-800"
          href="https://nl.ijs.si/ME/V6/msd/html/msd-mk.html"
          target="_blank"
          rel="noopener">
          {{ t('search.forms.tag.multtextEast') }}
        </a>
        {{ t('search.forms.tag.descriptionOneAfter') }}
      </p>
      <p>{{ t('search.forms.tag.descriptionTwo') }}</p>
    </SearchFormIntro>

    <form class="space-y-6" @submit.prevent="submit">
      <MorphologyFields
        :category-code="searchStore.morphologyCategoryCode"
        :selection="searchStore.morphologySelection"
        @select-category="searchStore.selectMorphologyCategory"
        @set-value="searchStore.setMorphologyValue" />

      <p v-if="searchStore.morphologyCategoryCode" class="text-xs text-stone-400">
        {{ t('search.forms.tag.patternLabel') }}
        <code class="text-stone-600">{{ searchStore.morphologyPattern }}</code>
      </p>

      <SearchContextFilter />

      <SearchFormActions @reset="searchStore.resetSearchInput('tag')" />
    </form>
  </section>
</template>
