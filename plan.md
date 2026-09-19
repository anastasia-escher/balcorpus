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

Agreed afterwards, not part of the minimal version:
- 3. Speaker details in a modal, opened from the author in the table.
- 4. The text page itself: every word with its lemma and tags under it.

Decided: paging everywhere, no infinite scroll.

Noticed while building, not touched — waiting on a decision:
- The navigation bar carries a dark scrim meant to sit over the cover
  photograph on the home page. On a page without a photograph it reads as
  a grey smudge.
- `components/search/SearchPagination.vue` and the new
  `components/common/CorpusPagination.vue` are now the same pager twice,
  one reading the search store and one taking props.
- `/api/v1/sentences/` without `?text=` is paginated but unordered, which
  Django warns about. Pre-existing; `?text=` orders properly.

Worth knowing: only `panov_pechalbari_1936` carries annotation today; the
other 103 texts have metadata only.
