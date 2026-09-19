<script setup lang="ts">
import {useI18n} from 'vue-i18n'

const {t} = useI18n()
const emit = defineEmits<{
  reset: []
}>()
</script>

<template>
  <div class="flex items-center gap-5">
    <UButton type="submit" :label="t('search.actions.submit')" color="primary" size="md" class="px-6" />
    <button
      type="button"
      class="text-sm text-stone-500 underline-offset-4 transition-colors hover:text-stone-800 hover:underline"
      @click="emit('reset')">
      {{ t('search.actions.reset') }}
    </button>
  </div>
</template>
