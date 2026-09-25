<script setup lang="ts">
/**
 * Choosing a part of speech and the values of its properties.
 *
 * The same fields describe two different words — the one being searched for,
 * and one standing near it — so they know nothing about the search itself:
 * they are given what is chosen and report back what the user chose.
 */
import FieldLabel from '~/components/search/FieldLabel.vue'
import {computed, useId} from 'vue'
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

// Each copy of these fields gets its own prefix, so that the chooser for
// the searched word and the one for the word beside it do not both call
// their gender dropdown the same thing.
const fieldPrefix = useId()
const categoryFieldId = `${fieldPrefix}-category`
const propertyFieldId = (property: MsdProperty) => `${fieldPrefix}-${property.name}`

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
      <label
        :for="categoryFieldId"
        class="mb-2 block text-xs tracking-[0.12em] text-stone-500 uppercase">
        {{ t('search.forms.tag.categoryLabel') }}
      </label>
      <USelect
        :id="categoryFieldId"
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
        <FieldLabel :field-id="propertyFieldId(property)">
          {{ t(property.labelKey) }}
        </FieldLabel>
        <USelect
          :id="propertyFieldId(property)"
          :model-value="chosenValue(property)"
          :items="valueOptions(property)"
          class="search-control w-full"
          size="lg"
          @update:model-value="chooseValue(property, $event)" />
      </div>
    </div>
  </div>
</template>
