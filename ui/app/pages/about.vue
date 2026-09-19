<script setup lang="ts">
import {CONTRIBUTORS} from '~/features/about/contributors'
import {useI18n} from 'vue-i18n'

const {t} = useI18n()
</script>

<template>
  <article class="mx-auto max-w-5xl px-6 pt-12 pb-24">
    <header>
      <h1 class="font-serif text-3xl text-stone-900">{{ t('about.title') }}</h1>
    </header>

    <section class="mt-10 max-w-2xl">
      <h2 class="font-serif text-xl text-stone-900">{{ t('about.corpus.heading') }}</h2>
      <p class="mt-4 text-sm leading-relaxed text-stone-600">
        {{ t('about.corpus.whatItIs') }}
      </p>
      <p class="mt-3 text-sm leading-relaxed text-stone-600">
        {{ t('about.corpus.annotation') }}
      </p>
    </section>

    <section class="mt-12 max-w-2xl">
      <h2 class="font-serif text-xl text-stone-900">{{ t('about.contributors.heading') }}</h2>
      <ul class="mt-4">
        <li v-for="contributor in CONTRIBUTORS" :key="contributor.name" class="mt-4 first:mt-0">
          <p class="text-sm text-stone-900">{{ contributor.name }}</p>
          <p class="mt-1 text-sm text-stone-600">{{ contributor.affiliation }}</p>
        </li>
      </ul>
    </section>
  </article>
</template>
