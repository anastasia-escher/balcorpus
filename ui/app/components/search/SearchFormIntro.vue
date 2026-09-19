<script setup lang="ts">
/**
 * The explanatory heading above each search form: a title and, in the slot,
 * however many paragraphs that kind of search needs to explain itself.
 */
defineProps<{title: string}>()
</script>

<template>
  <div class="mb-6">
    <h2 class="font-serif text-xl text-stone-900">{{ title }}</h2>
    <div class="mt-2 space-y-1.5 text-sm leading-relaxed text-stone-600">
      <slot />
    </div>
  </div>
</template>
