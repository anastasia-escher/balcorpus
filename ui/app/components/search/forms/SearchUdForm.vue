<script setup lang="ts">
import SearchFormActions from '~/components/search/SearchFormActions.vue'
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
    <div class="mb-8 text-gray-900">
      <p class="font-bold text-lg mb-2">
        {{ t('search.forms.ud.title') }}
        <span class="font-normal text-base text-gray-700">— {{ t('search.forms.ud.summary') }}</span>
      </p>
      <p class="mb-2">
        {{ t('search.forms.ud.descriptionOneBefore') }}
        <a
          class="text-blue-700 underline"
          href="https://universaldependencies.org/"
          target="_blank"
          rel="noopener">
          {{ t('search.forms.ud.universalDependencies') }}
        </a>
        {{ t('search.forms.ud.descriptionOneAfter') }}
      </p>
      <p class="mb-2">
        {{ t('search.forms.ud.descriptionTwo') }}
      </p>
      <p class="mb-2">
        {{ t('search.forms.ud.descriptionThree') }}
      </p>
    </div>
    <form class="space-y-8" @submit.prevent="submit">
      <USelect
        v-model="searchStore.udTag"
        :items="udTagOptions"
        :placeholder="t('search.forms.ud.placeholder')"
        class="w-full"
        size="xl" />
      <USelect
        v-model="searchStore.parent"
        :items="udTagOptions"
        :placeholder="t('search.forms.ud.parentPlaceholder')"
        class="w-full"
        size="xl" />
      <SearchFormActions @reset="searchStore.resetSearchInput('ud')" />
    </form>
  </section>
</template>
