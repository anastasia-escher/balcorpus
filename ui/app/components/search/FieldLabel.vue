<script setup lang="ts">
/**
 * The small caption above a field of the search forms.
 *
 * ``fieldId`` is the id of the field it names, so that clicking the caption
 * puts the cursor in that field.
 */
defineProps<{fieldId: string}>()
</script>

<template>
  <label :for="fieldId" class="mb-1.5 block text-xs tracking-[0.12em] text-stone-500 uppercase">
    <slot />
  </label>
</template>
