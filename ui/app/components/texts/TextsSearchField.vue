<script setup lang="ts">
import {ref} from 'vue'
import {useI18n} from 'vue-i18n'

/**
 * Finding a text in the catalogue by its title or by who wrote it.
 *
 * The corpus does the searching, so this only collects what was typed and
 * says when to go and ask. It reports the query rather than acting on it.
 */
const props = defineProps<{
  // What was searched for already, so a link to a search arrives with its
  // own words still in the box.
  initialQuery: string
}>()

const emit = defineEmits<{search: [query: string]}>()

const {t} = useI18n()

const query = ref(props.initialQuery)

const search = () => emit('search', query.value.trim())

const clear = () => {
  query.value = ''
  emit('search', '')
}
</script>

<template>
  <form class="flex flex-wrap items-center gap-3" @submit.prevent="search">
    <UInput
      v-model="query"
      class="search-control w-full sm:w-80"
      :placeholder="t('texts.search.placeholder')"
      :aria-label="t('texts.search.label')" />

    <UButton type="submit" :label="t('texts.search.submit')" color="primary" size="md" />

    <button
      v-if="query"
      type="button"
      class="text-sm text-stone-500 transition-colors hover:text-stone-900"
      @click="clear">
      {{ t('texts.search.clear') }}
    </button>
  </form>
</template>
