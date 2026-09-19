
---

# Morphology search — tracking note

Replacing the raw MULTEXT-East tag box with a chooser: a part of speech, then
a dropdown per property of that part of speech, in words rather than codes.
Remove this section when the work is done.

- [x] **1. Backend — an open tail on a tag pattern.** A closing `*` in `?pos=`
      means "and anything, or nothing, after this", because the annotation
      names as many positions as it knows: feminine pronouns sit in the corpus
      as 5-, 7- and 8-character tags. Without it the chooser would have to
      guess a length and would silently lose the rest.
      Wiring: `core/processing/token_search.py`, `core/tests/test_token_search.py`.
- [x] **2. Frontend — the specification as data.** The MSD-MK table (14
      categories, their ordered properties and values) plus one pure function
      that turns a selection into a pattern such as `N?fp?y*`. No UI yet.
      New: `features/search/msd.types.ts`, `features/search/msd.constants.ts`,
      `features/search/msd.pattern.ts`.
- [x] **3. Frontend — store and wiring.** The chosen category and values live
      in the search store and leave as the existing `pos` parameter.
      Wiring: `stores/search.ts`, `features/search/search.types.ts`,
      `features/search/search.constants.ts`.
- [x] **4. Frontend — the chooser itself.** A part-of-speech select, the
      property selects for whatever was chosen, and the built pattern shown
      underneath. The raw tag input goes away with it, along with `posQuery`.
      New: `components/search/forms/SearchMorphologyForm.vue`.
      Wiring: `pages/index.vue`, `i18n/locales/en.json`.

Decided: the pattern is built in the browser and the backend only learns `*`,
so the table of properties lives in one place, next to its human labels.
Decided: every value of the specification is offered, not only the ones the
corpus happens to carry today — one text of 104 is annotated so far.
Decided: the raw tag box is replaced, not kept as an "advanced" field.

Done, waiting on review — delete this section once it is reviewed.

Worth knowing afterwards:
- The old tag form's own explanation went with it, including the `N?sny`
  example, which was five characters long and therefore matched nothing: noun
  tags in the corpus have six. The link in the form now points at V6 of the
  specification, the one the table was written from, rather than V3.
- Typing a raw tag is no longer possible anywhere in the interface. The
  endpoint still accepts one, so `?pos=Ncfsny` by hand keeps working.
