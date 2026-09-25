# PHP port of the backend (Plesk hosting, spec: `php/ЗАГРУЗКА.md`)

- [x] Stage 1 — spec: all 5 endpoints, limits, browser loader behind a secret + empty data folder
- [ ] Stage 2 — `private/sql/schema.sql` + `private/db.php` + `config.example.php`
  - collation `utf8mb4_unicode_ci`: equality then ignores case, so plain indexes serve the case-insensitive search (unlike Postgres, which is left without new indexes)
  - indexes on tokens: `lemma`, `source`, `diplomatic`, `pos_tag`, `ud_type`, unique `(sentence_id, ud_id)`
  - speakers keep `religion` and `show_metadata` (see the loader and Stage 4)
- [ ] Stage 3 — loader (`private/upload/`, `httpdocs/upload/index.php`)
- [ ] Stage 4 — `texts/` and `texts/coverage/`
  - authors: never `religion`; `show_metadata = 0` → only `speaker_id`, `full_name`, `gender`, `l1`–`l3`, the rest `null`
- [ ] Stage 5 — `tokens/search/`
  - tag search ignores case (as Django's `iregex`; MariaDB `REGEXP` does this with a `_ci` collation)
  - nearby word: a window given the wrong way round (`near_from > near_to`) is swapped, not empty
- [ ] Stage 6 — `sentences/context/`
  - a sentence is read from `source`, or from `diplomatic` when it has no source (as `displayed_sentence` in Django)
- [ ] Stage 7 — `tokens/search/xlsx/` and the rate limits
- [ ] Each stage: compare responses with Django on the same data
- [ ] After loading the real corpus: time the partial-word search (`LIKE '%…%'` cannot use an index). Only if it is slow, decide what to do then
