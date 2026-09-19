<script setup lang="ts">
import AnnotatedSentence from '~/components/texts/AnnotatedSentence.vue'
import CorpusPagination from '~/components/common/CorpusPagination.vue'
import TextMetadataHeader from '~/components/texts/TextMetadataHeader.vue'
import {TEXT_SENTENCES_PAGE_SIZE} from '~/features/texts/texts.constants'
import {computed, onMounted} from 'vue'
import {pageRange} from '~/features/pagination/pagination'
import {startsNewTurn} from '~/features/texts/sentences'
import {useRoute} from 'vue-router'
import {useTextDetails} from '~/composables/useTextDetails'
import {useTextSentences} from '~/composables/useTextSentences'
import {useI18n} from 'vue-i18n'

const route = useRoute()
const details = useTextDetails()
const sentences = useTextSentences()
const {t} = useI18n()

const textId = String(route.params.textId)

/** Which sentences of the whole text this page is showing. */
const shownRange = computed(() => ({
  ...pageRange(sentences.page.value, sentences.itemCount.value, TEXT_SENTENCES_PAGE_SIZE),
  total: sentences.itemCount.value,
}))

onMounted(() => {
  details.loadText(textId)
  sentences.openText(textId)
})
</script>

<template>
  <article class="mx-auto max-w-4xl px-6 pt-12 pb-24">
    <NuxtLink to="/texts" class="text-xs text-link transition-colors hover:text-link-hover">
      {{ t('text.backToList') }}
    </NuxtLink>

    <!-- A text the corpus does not have says so and stops here. Going on to
         read its sentences would tell the reader it exists but is unannotated,
         which is a different thing entirely. -->
    <p
      v-if="details.missing.value"
      class="mt-12 border-l-2 border-terracotta-500 bg-terracotta-50 px-4 py-3 text-sm text-terracotta-900">
      {{ t('text.notFound') }}
    </p>

    <template v-else>
      <div class="mt-4">
        <TextMetadataHeader v-if="details.text.value" :text="details.text.value" />
        <p v-else-if="details.loading.value" class="text-sm text-stone-500">
          {{ t('text.loading') }}
        </p>
      </div>

      <p v-if="sentences.loading.value" class="mt-12 text-sm text-stone-500">
        {{ t('text.loading') }}
      </p>

      <p
        v-else-if="sentences.failed.value"
        class="mt-12 border-l-2 border-terracotta-500 bg-terracotta-50 px-4 py-3 text-sm text-terracotta-900">
        {{ t('text.failed') }}
      </p>

      <!-- Only one text of the corpus has been annotated so far; the rest
           carry metadata and nothing to read yet. -->
      <p v-else-if="!sentences.items.value.length" class="mt-12 text-sm text-stone-600">
        {{ t('text.notAnnotated') }}
      </p>

      <section v-else class="mt-8">
        <div class="space-y-6">
          <AnnotatedSentence
            v-for="(sentence, position) in sentences.items.value"
            :key="sentence.id"
            :sentence="sentence"
            :show-speaker="startsNewTurn(sentences.items.value, position)" />
        </div>

        <p v-if="sentences.pageCount.value > 1" class="mt-8 text-xs text-stone-500">
          {{ t('text.showingRange', shownRange) }}
        </p>

        <CorpusPagination
          :page="sentences.page.value"
          :page-count="sentences.pageCount.value"
          @select="sentences.goToPage" />
      </section>
    </template>
  </article>
</template>
