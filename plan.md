# Context search (a word together with what stands near it)

Tracking note for the work in progress; delete when the feature is done.

- [x] **Step 1 — backend query** (done, tests green, checked on real data)
      `processing/context_search.py` (new), `processing/token_search.py`
      (shared criteria builder), `views.py` (wiring), `serializers.py`
      (`context_ud_id`, `context_source`), tests.
- [x] Step 2 — backend highlight spans: `processing/sentence_spans.py`,
      serializer fields (`match_span`, `context_span`), tests.
- [x] Step 3 — frontend data: `context-criteria.ts` and
      `morphology-selection.ts` (new), types, distance options, store wiring.
      Only checkable once step 4 puts it on screen.
- [ ] Step 4 — frontend UI: `SearchContextFilter.vue` (new), reusable
      morphology fields, wiring into the four forms, `en.json`.
- [ ] Step 5 — frontend rendering: `highlight.ts`, `SearchResults.vue`.

Decided with the owner:
- distance is a range `near_from`..`near_to`, clamped to +/-3;
- distance counts tokens as annotated, punctuation included;
- when several neighbours fit, the first one in corpus order is reported.
