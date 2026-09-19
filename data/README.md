# Working with the corpus files

Where the files the linguists send go, what turns them into the corpus, and
what leaves for the server.

The project keeps three kinds of file apart on purpose: what arrives, what the
database holds, and what the PHP server is given. Nothing is edited in more
than one of them.

```
data/
  input/                    what the linguists deliver, as delivered
    metadata_speakers/        the speaker table, .xlsx
    metadata_texts/           the text table, .xlsx
    annotations/              one annotated text per file, .xlsx

  php_ready/                what the server loads -- generated, never edited
    speakers.csv
    texts.csv
    text_authors.csv
    sentences/<text_id>.csv
    tokens/<text_id>.csv

  fixed_data/               the published data package, see its own README
  transcripts/              working copies of material being prepared
```

`data/` is mounted in the container as `/data`, which is why the commands
below are given paths starting with `/data`.

## The order of work

A new file arrives, and it goes through these four steps. The first three
check the file and refuse it whole if anything is wrong: either everything is
imported or nothing is, and every problem found is listed at once, so a file
can be corrected in one go rather than one error per run.

### 1. The speakers

```
docker compose exec api python manage.py import_speakers /data/input/metadata_speakers/<file>.xlsx
```

### 2. The texts

```
docker compose exec api python manage.py import_texts /data/input/metadata_texts/<file>.xlsx
```

### 3. The annotated text

```
docker compose exec api python manage.py upload_transcription /data/input/annotations/<text_id>.xlsx
```

Re-running this for a text that is already in the corpus replaces everything
stored for it, so a corrected file can simply be imported again.

### 4. The files for the server

```
docker compose exec api python manage.py export_php
```

Or, after re-importing a single annotation, only that text:

```
docker compose exec api python manage.py export_php --text <text_id>
```

Then copy `data/php_ready/` to `private/data/` on the server and run the
loader there.

## Why that order

Each step needs what the one before it wrote:

- a text names its author by `speaker_id`, so the speaker has to exist before
  the text table is imported;
- an annotation names its text by `text_id` and its speakers by `speaker_id`,
  so both tables have to be imported before the annotation;
- the export reads the database, so it comes last.

Out of order, the import stops and says which file to run first. It does not
write half of the data and leave the rest.

## What the exported files are

Plain CSV: UTF-8, comma separated, a header line naming the columns, quotation
marks around any cell containing a comma, a quotation mark or a line break.
**An empty cell means NULL.** No field of the corpus is one where an empty
string would mean something different from nothing.

No database key is ever written. Importing a text deletes its sentences and
tokens and creates them again, so their numeric `id` is different after every
import and would mean nothing on the server. The files name a text by its
`text_id`, a person by their `speaker_id`, a sentence by its number within the
text and a token by its number within the sentence -- the same identifiers the
linguists use.

The metadata is written whole, the annotation one file per text. That is what
makes adding a text to the server cheap: two small files to copy rather than
the whole corpus again.

## Two rules

- **Nothing in `php_ready/` is edited by hand.** It is generated, it is not in
  git, and the next export overwrites it. A correction belongs in the file
  under `input/`, which is then imported again.
- **Files under `input/` are kept as they were delivered.** They are the
  record of what was received; the checks exist so that a file does not have
  to be tidied up by hand before it can be imported.
