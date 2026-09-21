<script setup lang="ts">
/**
 * Choosing a part of speech and the values of its properties.
 *
 * The same fields describe two different words — the one being searched for,
 * and one standing near it — so they know nothing about the search itself:
 * they are given what is chosen and report back what the user chose.
 */
import {computed} from 'vue'
import {MSD_CATEGORIES, findMsdCategory} from '~/features/search/msd.constants'
import {useI18n} from 'vue-i18n'
import type {MsdProperty, MsdSelection} from '~/features/search/msd.types'

// A dropdown cannot hold an empty value, so "any" is a value of its own here,
// which is reported back as "this property was not chosen".
const ANY_VALUE = 'any'

const props = defineProps<{
  categoryCode: string | null
  selection: MsdSelection
}>()

const emit = defineEmits<{
  selectCategory: [code: string | null]
  setValue: [propertyName: string, code: string | null]
}>()

const {t} = useI18n()

const categoryOptions = computed(() =>
  MSD_CATEGORIES.map(category => ({
    label: t(category.labelKey),
    value: category.code,
  }))
)

const properties = computed(() => findMsdCategory(props.categoryCode)?.properties ?? [])

/** The choices of one property, with "any" in front of them. */
const valueOptions = (property: MsdProperty) => [
  {label: t('search.forms.tag.anyValue'), value: ANY_VALUE},
  ...property.values.map(value => ({label: t(value.labelKey), value: value.code})),
]

const chosenValue = (property: MsdProperty) => props.selection[property.name] ?? ANY_VALUE

const chooseValue = (property: MsdProperty, chosen: string) => {
  emit('setValue', property.name, chosen === ANY_VALUE ? null : chosen)
}
</script>

<template>
  <div class="space-y-4">
    <div>
      <label class="mb-2 block text-xs tracking-[0.12em] text-stone-500 uppercase">
        {{ t('search.forms.tag.categoryLabel') }}
      </label>
      <USelect
        :model-value="categoryCode ?? undefined"
        :items="categoryOptions"
        :placeholder="t('search.forms.tag.categoryPlaceholder')"
        class="search-control w-full"
        size="xl"
        @update:model-value="emit('selectCategory', $event)" />
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
  </div>
</template>
