# Safe Excel export and public API limits

- [x] Step 1 — export as .xlsx (`tokens/search/xlsx/`), text cells never run as formulas, lighter serializer
- [x] Step 2 — rate limits per IP (60/min API, 5/min export) and max 100 chars per search field
- [x] Step 3 — frontend: open the export link in a new tab, so a 429/400 does not replace the results
- [x] Step 4 — note for the PHP port: xlsx via ZipArchive, the limits above (in `php/ЗАГРУЗКА.md`)

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
- [ ] Stage 7 — `tokens/search/xlsx/` and the rate limits
- [ ] Each stage: compare responses with Django on the same data
- [ ] After loading the real corpus: time the partial-word search (`LIKE '%…%'` cannot use an index). Only if it is slow, decide what to do then

# Linguists' annotation files import as they are (replaces `tools/fix_data`)

- [x] Step 1 — importer reads `ud_valency`/`speaker`, finds text by title (or `--text`) and speaker by name, drops wordless rows; test on the real raw file
- [ ] Step 2 — delete `tools/fix_data` and the copies in `data/fixed_data/` (README + datapackage.json move to `data/input/`); update `data/README.md` and `php/ЗАГРУЗКА.md`
