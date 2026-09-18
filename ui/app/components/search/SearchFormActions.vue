<script setup lang="ts">
import {useI18n} from 'vue-i18n'

const {t} = useI18n()
const emit = defineEmits<{
  reset: []
}>()
</script>

<template>
  <div class="flex gap-4 mt-8">
    <UButton type="submit" :label="t('search.actions.submit')" class="px-6" color="primary" />
    <UButton
      type="button"
      :label="t('search.actions.reset')"
      class="px-6"
      color="neutral"
      variant="outline"
      @click="emit('reset')" />
  </div>
</template>
