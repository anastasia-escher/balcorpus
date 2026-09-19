<script setup lang="ts">
/**
 * Searching by morphology without knowing the tag language: a part of speech,
 * and then a dropdown for each property that part of speech can carry.
 */
import SearchFormActions from '~/components/search/SearchFormActions.vue'
import SearchFormIntro from '~/components/search/SearchFormIntro.vue'
import {computed} from 'vue'
import {MSD_CATEGORIES} from '~/features/search/msd.constants'
import {useSearchStore} from '~/stores/search'
import {useI18n} from 'vue-i18n'
import type {MsdProperty} from '~/features/search/msd.types'

// A dropdown cannot hold an empty value, so "any" is a value of its own here,
// which the store reads as "this property was not chosen".
const ANY_VALUE = 'any'

const searchStore = useSearchStore()
const {t} = useI18n()

const categoryOptions = computed(() =>
  MSD_CATEGORIES.map(category => ({
    label: t(category.labelKey),
    value: category.code,
  }))
)

const properties = computed(() => searchStore.morphologyCategory?.properties ?? [])

/** The choices of one property, with "any" in front of them. */
const valueOptions = (property: MsdProperty) => [
  {label: t('search.forms.tag.anyValue'), value: ANY_VALUE},
  ...property.values.map(value => ({label: t(value.labelKey), value: value.code})),
]

const chosenValue = (property: MsdProperty) =>
  searchStore.morphologySelection[property.name] ?? ANY_VALUE

const chooseValue = (property: MsdProperty, chosen: string) => {
  searchStore.setMorphologyValue(property.name, chosen === ANY_VALUE ? null : chosen)
}

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
      <div>
        <label class="mb-2 block text-xs tracking-[0.12em] text-stone-500 uppercase">
          {{ t('search.forms.tag.categoryLabel') }}
        </label>
        <USelect
          :model-value="searchStore.morphologyCategoryCode ?? undefined"
          :items="categoryOptions"
          :placeholder="t('search.forms.tag.categoryPlaceholder')"
          class="search-control w-full"
          size="xl"
          @update:model-value="searchStore.selectMorphologyCategory($event)" />
      </div>

      <!-- The properties of the chosen part of speech, and nothing else: a
           noun has no tense and a verb has no definiteness. -->
      <div v-if="properties.length" class="grid gap-4 sm:grid-cols-2">
        <div v-for="property in properties" :key="property.name">
          <label class="mb-1.5 block text-xs tracking-[0.12em] text-stone-500 uppercase">
            {{ t(property.labelKey) }}
          </label>
          <USelect
            :model-value="chosenValue(property)"
            :items="valueOptions(property)"
            class="search-control w-full"
            size="lg"
            @update:model-value="chooseValue(property, $event)" />
        </div>
      </div>

      <p v-if="searchStore.morphologyCategoryCode" class="text-xs text-stone-400">
        {{ t('search.forms.tag.patternLabel') }}
        <code class="text-stone-600">{{ searchStore.morphologyPattern }}</code>
      </p>

      <SearchFormActions @reset="searchStore.resetSearchInput('tag')" />
    </form>
  </section>
</template>
