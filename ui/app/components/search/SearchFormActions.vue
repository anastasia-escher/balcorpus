<script setup lang="ts">
import Button from 'primevue/button'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const emit = defineEmits<{
  reset: []
}>()
</script>

<template>
  <div class="flex gap-4 mt-8">
    <Button
      type="submit"
      :label="t('search.actions.submit')"
      class="px-6"
      severity="info"
    />
    <Button
      type="button"
      :label="t('search.actions.reset')"
      class="px-6"
      severity="secondary"
      outlined
      @click="emit('reset')"
    />
  </div>
</template>
