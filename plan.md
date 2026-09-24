# Safe Excel export and public API limits

- [x] Step 1 — export as .xlsx (`tokens/search/xlsx/`), text cells never run as formulas, lighter serializer
- [x] Step 2 — rate limits per IP (60/min API, 5/min export) and max 100 chars per search field
- [x] Step 3 — frontend: open the export link in a new tab, so a 429/400 does not replace the results
- [x] Step 4 — note for the PHP port: xlsx via ZipArchive, the limits above (in `php/ЗАГРУЗКА.md`)

# PHP port of the backend (Plesk hosting, spec: `php/ЗАГРУЗКА.md`)

- [x] Stage 1 — spec: all 5 endpoints, limits, browser loader behind a secret + empty data folder
- [ ] Stage 2 — `private/sql/schema.sql` + `private/db.php` + `config.example.php`
- [ ] Stage 3 — loader (`private/upload/`, `httpdocs/upload/index.php`)
- [ ] Stage 4 — `texts/` and `texts/coverage/`
- [ ] Stage 5 — `tokens/search/`
- [ ] Stage 6 — `sentences/context/`
- [ ] Stage 7 — `tokens/search/xlsx/` and the rate limits
- [ ] Each stage: compare responses with Django on the same data
