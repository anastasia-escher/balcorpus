# Safe Excel export and public API limits

- [x] Step 1 — export as .xlsx (`tokens/search/xlsx/`), text cells never run as formulas, lighter serializer
- [x] Step 2 — rate limits per IP (60/min API, 5/min export) and max 100 chars per search field
- [x] Step 3 — frontend: open the export link in a new tab, so a 429/400 does not replace the results
- [ ] Step 4 — note for the PHP port: xlsx via ZipArchive, the limits above
