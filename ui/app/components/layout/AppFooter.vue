<script setup lang="ts">
import {useI18n} from 'vue-i18n'

const {t} = useI18n()
</script>

<template>
  <footer class="border-t border-stone-200">
    <div class="mx-auto max-w-5xl px-6 py-8 text-xs leading-relaxed text-stone-500">
      <p class="font-serif text-sm text-stone-700">{{ t('site.name') }}</p>
      <p class="mt-2 max-w-2xl">{{ t('site.tagline') }}</p>
      <p class="mt-3 flex flex-wrap gap-x-5 gap-y-1">
        <a
          class="underline-offset-2 hover:text-terracotta-700 hover:underline"
          href="https://universaldependencies.org/"
          target="_blank"
          rel="noopener">
          {{ t('search.forms.ud.universalDependencies') }}
        </a>
        <a
          class="underline-offset-2 hover:text-terracotta-700 hover:underline"
          href="http://nl.ijs.si/ME/V3/msd/html/msd-mk.html"
          target="_blank"
          rel="noopener">
          {{ t('search.forms.tag.multtextEast') }}
        </a>
      </p>
    </div>
  </footer>
</template>
