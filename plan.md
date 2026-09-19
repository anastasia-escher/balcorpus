# Texts pages — tracking note

Minimal version: the list of texts, plus the backend an annotated text page
will need. Remove this file when the work is done.

- [x] **1. Backend — a text's sentences.** `?text=<text_id>` on
      `/api/v1/sentences/`, paginated, in the order the text is written.
      New: `core/processing/text_sentences.py`, `core/tests/test_sentence_endpoint.py`.
      Wiring: `core/views.py`.
- [x] **2. Frontend — the list of texts.** An airy table of the metadata.
      New: `features/texts/texts.types.ts`, `composables/useTextList.ts`,
      `components/texts/TextsTable.vue`, `pages/texts/index.vue`.
      Wiring: `features/layout/navigation.constants.ts`, `i18n/locales/en.json`.

- [x] **3. Speaker details in a window**, opened from the author's name.
      New: `features/texts/speaker.ts`, `components/texts/SpeakerDetailsModal.vue`.
      Wiring: `components/texts/TextsTable.vue`, `i18n/locales/en.json`.
- [x] **4. The text page:** every word with its lemma and tags under it.
      New: `features/texts/sentences.ts`, `composables/useTextDetails.ts`,
      `composables/useTextSentences.ts`, `components/texts/AnnotatedSentence.vue`,
      `components/texts/TextMetadataHeader.vue`, `pages/texts/[textId].vue`.
- [x] **5. Finding a text**, by title, author or text_id, on the server.
      New: `core/processing/text_search.py`, `core/tests/test_text_search.py`,
      `components/texts/TextsSearchField.vue`.
      Wiring: `core/views.py`, `pages/texts/index.vue`, `i18n/locales/en.json`.

Done along the way:
- [x] **One pager, one set of paging helpers.** `SearchPagination.vue` is
      gone; both the search and the catalogue use
      `components/common/CorpusPagination.vue`. The pure helpers moved out
      of `features/search/` into `features/pagination/`, and each feature
      now declares its own page size instead of inheriting the search's.
- [x] **One paging composable.** `composables/usePaginatedList.ts` holds
      the fetch-a-page dance; `useTextList` and `useTextSentences` are
      eight-line wrappers over it.
- [x] **Links are blue**, via a `--color-link` token, because the
      terracotta accent marks emphasis everywhere and did not read as
      "this takes you somewhere".
- [x] **The pointer cursor**, in one place: `assets/css/cursors.css`.
      Tailwind's preflight gives a button the arrow cursor and the Nuxt UI
      controls inherit it, so tabs, selects, checkboxes, Submit/Reset, the
      search pager and "Show context" all showed an arrow. Audited every
      clickable element on every screen: none left without a hand.
- [x] **The navigation bar** no longer wears its dark scrim on a page
      without a cover photograph. A page asks for the bar it wants through
      `definePageMeta({navigationVariant})`.
      New: `features/layout/navigation.variants.ts`.
      Wiring: `AppNavigation.vue`, `layouts/default.vue`, both pages.

Decided: paging everywhere, no infinite scroll.

Noticed while building, not touched — waiting on a decision:
- `/api/v1/sentences/` without `?text=` is paginated but unordered, which
  Django warns about. Pre-existing; `?text=` orders properly.

Worth knowing: only `panov_pechalbari_1936` carries annotation today; the
other 103 texts have metadata only.
