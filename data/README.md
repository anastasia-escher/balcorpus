# Working with the corpus files

Where the files the linguists send go, what turns them into the corpus, and
what leaves for the server.

The project keeps three kinds of file apart on purpose: what arrives, what the
database holds, and what the PHP server is given. Nothing is edited in more
than one of them.

```
data/
  input/                    what goes into the database; its README describes every column
    metadata_speakers/        the speaker table, .xlsx -- the master copy, edited here
    metadata_texts/           the text table, .xlsx -- the master copy, edited here
    annotations/              one annotated text per file, .xlsx, as the linguists send it

  php_ready/                what the server loads -- generated, never edited
    speakers.csv
    texts.csv
    text_authors.csv
    sentences/<text_id>.csv
    tokens/<text_id>.csv
```

`data/` is mounted in the container as `/data`, which is why the commands
below are given paths starting with `/data`.

## When a new text arrives

The linguists send only the annotation file. Three steps:

1. Add a row for the text to `input/metadata_texts/texts.xlsx`, and a row for
   each new person to `input/metadata_speakers/speakers.xlsx`, following the
   rows around it. Import the tables that changed (commands 1 and 2 below).
2. Put the linguists' file, unchanged, into `input/annotations/` and import it
   (command 3). The text is found by the title in the file, the speakers by
   their names.
3. Copy the new files from `php_ready/` to the server.

## The order of work

A new file arrives and goes through one of these three commands. Each of them
checks the file and refuses it whole if anything is wrong: either everything is
imported or nothing is, and every problem found is listed at once, so a file
can be corrected in one go rather than one error per run.

**Each command ends by writing the files for the server itself**, so there is
no fourth step to remember. The two metadata commands rewrite the metadata
files; importing an annotation rewrites that text's two files.

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
docker compose exec api python manage.py upload_transcription /data/input/annotations/<file>.xlsx
```

The file may be in the linguists' own format. If two texts share the title
written in the file, the command stops, lists their `text_id`s, and the right
one is given with `--text <text_id>`.

Re-running this for a text that is already in the corpus replaces everything
stored for it, so a corrected file can simply be imported again.

### Then: to the server

Copy `data/php_ready/` to `private/data/` on the server and run the loader
there.

## Writing every file again

The imports keep `php_ready/` up to date on their own. One command writes the
whole corpus out again, for when that is not enough -- after restoring a
backup, or when the folder has been emptied:

```
docker compose exec api python manage.py export_php
```

It also takes a single text, leaving the metadata files alone:

```
docker compose exec api python manage.py export_php --text <text_id>
```

## Why that order

Each command needs what the one before it wrote:

- a text names its author by `speaker_id`, so the speaker has to exist before
  the text table is imported;
- an annotation names its text by `text_id` and its speakers by `speaker_id`,
  so both tables have to be imported before the annotation;
- the export reads the database, so it happens at the end of each command.

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
- **An annotation file is imported as it was delivered.** The checks exist
  so that a file does not have to be tidied up by hand first. A correction
  made here to a delivered file (as for `panov_pechalbari_1936.xlsx`) means
  the linguists' original of that text must not be imported again.
