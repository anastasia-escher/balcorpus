<script setup lang="ts">
import Button from 'primevue/button'

const emit = defineEmits<{
  reset: []
}>()
</script>

<template>
  <div class="flex gap-4 mt-8">
    <Button
      type="submit"
      label="SUBMIT"
      class="px-6"
      severity="info"
    />
    <Button
      type="button"
      label="RESET"
      class="px-6"
      severity="secondary"
      outlined
      @click="emit('reset')"
    />
  </div>
</template>
