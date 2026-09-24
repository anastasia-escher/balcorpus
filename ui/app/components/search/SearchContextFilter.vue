<script setup lang="ts">
/**
 * Asking for a second word that has to stand near the match: "a first person
 * plural pronoun with a past tense verb two words in front of it".
 *
 * The block is the same on every search tab, and describes its word the same
 * four ways the tab above it does. It starts folded away, because most
 * searches are about one word only.
 */
import MorphologyFields from '~/components/search/MorphologyFields.vue'
import {computed, useId} from 'vue'
import {CONTEXT_DISTANCES, UD_TAG_OPTIONS} from '~/features/search/search.constants'
import {SEARCH_KINDS} from '~/features/search/search.types'
import {useSearchStore} from '~/stores/search'
import {useI18n} from 'vue-i18n'

const searchStore = useSearchStore()
const {t} = useI18n()

// A prefix of this block's own, so that every label names the field
// under it and the names stay apart from any other form on the page.
const fieldPrefix = useId()
const fieldId = (name: string) => `${fieldPrefix}-${name}`

// The block's own state lives in the store, because all four search tabs
// show this same block and it must survive moving between them.
const context = searchStore.context

const distanceOptions = computed(() =>
  CONTEXT_DISTANCES.map(distance => ({
    label: t(distance.labelKey),
    value: distance.value,
  }))
)

/** The four ways of describing a word, the same ones the tabs offer. */
const kindOptions = computed(() =>
  SEARCH_KINDS.map(kind => ({
    label: t(`search.nearbyWord.kinds.${kind}`),
    value: kind,
  }))
)

const udTagOptions = computed(() =>
  UD_TAG_OPTIONS.map(option => ({
    label: t(option.labelKey),
    value: option.value,
  }))
)
</script>

<template>
  <div class="border-t border-stone-200 pt-5">
    <button
      type="button"
      class="text-sm text-stone-500 underline-offset-4 transition-colors hover:text-terracotta-700 hover:underline"
      :aria-expanded="context.isOpen"
      @click="context.toggle()">
      {{ context.isOpen ? t('search.nearbyWord.hide') : t('search.nearbyWord.add') }}
    </button>

    <fieldset v-if="context.isOpen" class="mt-5 space-y-5 border-l-2 border-stone-200 pl-5">
      <legend class="font-serif text-base text-stone-900">
        {{ t('search.nearbyWord.title') }}
      </legend>
      <p class="text-sm text-stone-600">{{ t('search.nearbyWord.summary') }}</p>

      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label
            :for="fieldId('distance')"
            class="mb-1.5 block text-xs tracking-[0.12em] text-stone-500 uppercase">
            {{ t('search.nearbyWord.distanceLabel') }}
          </label>
          <USelect
            :id="fieldId('distance')"
            v-model="context.distanceCode"
            :items="distanceOptions"
            class="search-control w-full"
            size="lg" />
        </div>

        <div>
          <label
            :for="fieldId('kind')"
            class="mb-1.5 block text-xs tracking-[0.12em] text-stone-500 uppercase">
            {{ t('search.nearbyWord.kindLabel') }}
          </label>
          <USelect
            :id="fieldId('kind')"
            v-model="context.kind"
            :items="kindOptions"
            class="search-control w-full"
            size="lg" />
        </div>
      </div>

      <!-- One field per way of describing the word; only the chosen one shows. -->
      <div v-if="context.kind === 'text'">
        <label
          :for="fieldId('text')"
          class="mb-1.5 block text-xs tracking-[0.12em] text-stone-500 uppercase">
          {{ t('search.nearbyWord.kinds.text') }}
        </label>
        <UInput
          :id="fieldId('text')"
          v-model="context.textQuery"
          class="search-control w-full"
          size="lg"
          :placeholder="t('search.nearbyWord.textPlaceholder')" />
      </div>

      <div v-else-if="context.kind === 'lemma'">
        <label
          :for="fieldId('lemma')"
          class="mb-1.5 block text-xs tracking-[0.12em] text-stone-500 uppercase">
          {{ t('search.nearbyWord.kinds.lemma') }}
        </label>
        <UInput
          :id="fieldId('lemma')"
          v-model="context.lemma"
          class="search-control w-full"
          size="lg"
          :placeholder="t('search.nearbyWord.lemmaPlaceholder')" />
      </div>

      <MorphologyFields
        v-else-if="context.kind === 'tag'"
        :category-code="context.morphology.categoryCode"
        :selection="context.morphology.selection"
        @select-category="context.morphology.selectCategory"
        @set-value="context.morphology.setValue" />

      <div v-else-if="context.kind === 'ud'">
        <label
          :for="fieldId('ud')"
          class="mb-1.5 block text-xs tracking-[0.12em] text-stone-500 uppercase">
          {{ t('search.nearbyWord.kinds.ud') }}
        </label>
        <USelect
          :id="fieldId('ud')"
          v-model="context.udTag"
          :items="udTagOptions"
          :placeholder="t('search.nearbyWord.udPlaceholder')"
          class="search-control w-full"
          size="lg" />
      </div>

      <p v-if="context.isFilledIn" class="text-xs text-stone-400">
        {{ t('search.nearbyWord.askingFor') }}
        <code class="text-stone-600">{{ context.query }}</code>
      </p>
    </fieldset>
  </div>
</template>
