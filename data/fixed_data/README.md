# Macedonian Corpus — metadata and annotated texts

Metadata and morphologically and syntactically annotated texts of the Macedonian Corpus. The metadata are in English; the material itself, and the names of people and titles, stay in Macedonian.

These files are produced from the spreadsheets the editors maintain, by
`python -m tools.fix_data.run` in the repository root. Edit the
spreadsheets and run it again rather than editing these files by hand.

## How the files fit together

```
speakers.xlsx          one row per person        speaker_id
        ▲                                              ▲
        │ author_id                                    │ speaker_id
texts.xlsx              one row per document      text_id
        ▲                                              ▲
        │ text_id                                      │
annotations/<text_id>.xlsx    one row per token
```

Every identifier is lowercase ASCII with underscores, so it survives
spreadsheets, exports and URLs unchanged.

## Conventions

- **The format is Excel (`.xlsx`)**, one table per workbook, the column
  names in row 1 and the data from row 2. Excel carries its own encoding,
  so nothing has to be set when opening a file and no accented or
  Cyrillic letter can turn into `Ð¿Ð°Ð½Ð¾Ð²`. A comma inside a cell is
  just a comma, because there is no delimiter to escape.
- **Numbers are stored as numbers** — years, sentence and token numbers,
  the head position — and everything else as text.
- **An empty cell means the value was not recorded.** The sources wrote
  `NA` for this, which is a value and not an absence, so it is gone.
- **A cell that holds several values** separates them with a semicolon,
  as in `drama;prose` or `sr;hr`.
- **Languages** are ISO 639-1 codes: `mk`, `bg`, `sr`, `hr`, `bs`, `sq`, `ru`, `en`, `fr`, `de`, `ro`, `cs`, `sl`, `pl`.
- **Macedonian is romanised** by the standard transliteration with the
  diacritics spelled out: `ж` → `zh`, `ч` → `ch`, `џ` → `dzh`, `ѓ` → `gj`,
  `ќ` → `kj`, `љ` → `lj`, `њ` → `nj`, `ѕ` → `dz`.

## speakers.xlsx

One row per person whose language the corpus records.

| column | type | meaning |
|---|---|---|
| `speaker_id` | string | Identifier used by texts.xlsx and by the annotation files. Example: `anton_panov`. |
| `name` | string | The name the person is known by, in Macedonian Cyrillic. For a writer this may be a pen name. |
| `birth_name` | string | The name on their papers, filled in only when it differs from name. |
| `sex` | string | Recorded sex of the speaker. One of: `male`, `female`. |
| `birth_year` | year | Year of birth. |
| `place_of_birth` | string | Settlement of birth, romanised. A second name the settlement goes by is kept in brackets. |
| `place_type` | string | Whether that settlement is a village or a town. One of: `village`, `town`. |
| `municipality` | string | Municipality the settlement belongs to, romanised, when the source named one. |
| `dialect_region` | string | Dialect area the speaker comes from. Areas inside Macedonia are compass directions; speakers from elsewhere are given by country, with a part of it in brackets. One of: `southwest`, `southeast`, `south`, `north`, `east`, `west`, `northwest`, `northeast`, `central`, `Aegean Macedonia`, `Turkey`, `Kosovo`, `Serbia`, `Albania`, `Moldova`, `Romania`, `Greece`, `Bosnia and Herzegovina`, `Croatia`, `central-east`, `central Bosnia`. |
| `education_level` | string | How far the speaker went in school. One of: `tertiary`, `secondary`. |
| `education_note` | string | What kind of school, when the source said so. |
| `religion` | string | Recorded religion. One of: `Orthodox`, `Muslim`. |
| `l1` | string | First language, as ISO 639-1 codes. Example: `mk`. |
| `l2` | string | Second language. Several codes are separated by a semicolon. Example: `sr;hr`. |
| `l3` | string | Third language, written like l2. |
| `notes` | string | Remarks the source hid inside cells that were meant to hold a value, such as postings as an ambassador. |
| `source_row` | integer | Row number in the spreadsheet this came from, for checking against the editors’ own copy. |

## texts.xlsx

One row per document of the corpus.

| column | type | meaning |
|---|---|---|
| `text_id` | string | Identifier used by the annotation files: author surname, short title, year. Example: `panov_pechalbari_1936`. |
| `title` | string | Title of the text, in Macedonian Cyrillic. |
| `author_id` | string | The author, as a speaker_id. |
| `data_genre` | string | What kind of material this is. One of: `literature`, `speech`. |
| `text_genre` | string | Literary genre. Several genres are separated by a semicolon. One of: `drama`, `prose`, `poetry`, `criticism`, `dialogue`. Example: `drama;prose`. |
| `variety` | string | Whether the text is in the standard language or a dialect. One of: `standard`, `dialectal`. |
| `variety_note` | string | What the source wrote beside the variety, romanised: which dialect, or why both are named. |
| `year` | year | Year of publication. The first one, if several. |
| `year_note` | string | Further years the source gave, for a text published more than once. |
| `source_url` | string | Where the text can be read online. |
| `source_file` | string | Name of the file the editors delivered, kept as the record of where this row came from. |
| `source_row` | integer | Row number in the spreadsheet this came from. |

## annotations/*.xlsx

One file per text, one row per token, in the order of the text. Morphology follows MULTEXT-East, syntax follows Universal Dependencies.

| column | type | meaning |
|---|---|---|
| `text_id` | string | The text this token belongs to. |
| `sent_id` | integer | Number of the sentence within the text. |
| `ud_id` | integer | Position of the token within the sentence. |
| `source` | string | The word form as it stands in the text. |
| `diplomatic` | string | The word form in diplomatic transcription, where the corpus has one. |
| `lemma` | string | Dictionary form of the word. |
| `ud_pos` | string | Universal part-of-speech tag. Example: `NOUN`. |
| `pos_tag` | string | MULTEXT-East morphosyntactic description. Example: `Ncmsnn`. |
| `pos_ext` | string | Universal Dependencies features. Example: `Case=Nom|Gender=Masc|Number=Sing`. |
| `head` | integer | The ud_id of this token’s syntactic head in the same sentence. 0 means the token is the root. The source called this column ud_valency, which it never was. |
| `ud_type` | string | Universal Dependencies relation to the head, subtypes included. Example: `nsubj:pass`. |
| `speaker_id` | string | Who produced this stretch of language. |
| `time` | string | Timecode in the recording; only spoken material has one. |

## Known gaps

The conversion prints everything it cannot translate or match. What it
reported last time is recorded here:

- Three authors write a text but are missing from the speaker
  spreadsheet: Миле Неделковски, Катица Ќулафкова and Славе Ѓ. Димовски.
  They appear in `speakers.xlsx` with their name only, and their `notes`
  say so.
- The first row of the annotation file held a byte order mark and no
  word, so it is not a token and was dropped.
