"""The controlled vocabularies of the corpus, and their English wording.

The corpus interface is English and only the material itself stays Macedonian,
so every piece of metadata is translated here once. Each table is closed: a
value that is not listed is reported by the conversion rather than guessed at,
which is how a wrong translation gets noticed instead of shipped.

`MISSING` is what the source files write as "NA". It becomes an empty cell,
because "not recorded" is the absence of a value, not a value of its own.
"""

MISSING = {'NA', 'N/A', 'n/a', ''}

# What kind of material the text is.
DATA_GENRE = {
    'Литература': 'literature',
    'Говор': 'speech',
}

# The literary genre. A text may belong to more than one, and then the source
# separates them with a comma.
TEXT_GENRE = {
    'Драма': 'drama',
    'Проза': 'prose',
    'Поезија': 'poetry',
    'Критика': 'criticism',
    'Дијалог': 'dialogue',
}

# Whether the text is in the standard language or in a dialect. The source
# writes the details in free text, which is kept separately in variety_note.
TEXT_VARIETY = {
    'Стандарден': 'standard',
    'Дијалектен': 'dialectal',
}

SEX = {
    'М': 'male',
    'M': 'male',
    'Ж': 'female',
    'F': 'female',
}

RELIGION = {
    'Православен': 'Orthodox',
    'Муслиман': 'Muslim',
}

# The dialect area a speaker comes from. Areas inside Macedonia are given as
# compass directions, speakers from elsewhere by their country.
DIALECT_REGION = {
    'Југозапад': 'southwest',
    'Југоисток': 'southeast',
    'Југ': 'south',
    'Север': 'north',
    'Исток': 'east',
    'Запад': 'west',
    'Северозапад': 'northwest',
    'Североисток': 'northeast',
    'Центар': 'central',
    'Централно подрачје': 'central',
    'Егејска Македонија': 'Aegean Macedonia',
    'Турција': 'Turkey',
    'Косово': 'Kosovo',
    'Србија': 'Serbia',
    'Албанија': 'Albania',
    'Молдавија': 'Moldova',
    'Романија': 'Romania',
    'Грција': 'Greece',
    'Босна и Херцеговина': 'Bosnia and Herzegovina',
    'Хрватска': 'Croatia',
    # Parts of a country, which the source writes after a comma.
    'североисток': 'northeast',
    'централноисточен дел': 'central-east',
    'централна Босна': 'central Bosnia',
    'јужниот дел': 'south',
}

# How far the speaker went in school. The wording in brackets is not part of
# the level and is kept in education_note.
EDUCATION_LEVEL = {
    'Факултет': 'tertiary',
    'Високо': 'tertiary',
    'Учителска академија': 'tertiary',
    'Средно': 'secondary',
}

# The detail the source puts in brackets after the level.
EDUCATION_NOTE = {
    'гимназија': 'gymnasium',
    'стручно-техничко училиште': 'technical secondary school',
    'вечерни училишта': 'evening school',
    'Виша педагошка школа': 'higher pedagogical school',
    'факултет – незавршен': 'university not completed',
    'Охридска гимназија': 'Ohrid gymnasium',
    'учителска школа во Скопје': 'teacher training school in Skopje',
}

# Languages, as ISO 639-1 codes. A slot may hold several codes, separated by
# a semicolon, when the source records more than one.
LANGUAGE = {
    'MK': 'mk', 'BG': 'bg', 'SR': 'sr', 'HR': 'hr', 'BS': 'bs', 'SQ': 'sq',
    'RU': 'ru', 'EN': 'en', 'FR': 'fr', 'DE': 'de', 'RO': 'ro', 'CS': 'cs',
    'SL': 'sl', 'PL': 'pl',
}

# Remarks the source hides inside an "NA (...)" cell. They say nothing about
# the field they sit in, so they move to the speaker's notes.
NOTE_PHRASES = {
    'амб': 'ambassador to',
    'но: амб': 'ambassador to',
    'веројатно муслиман': 'probably Muslim',
}

# Country and place names that turn up inside those remarks.
PLACES_IN_NOTES = {
    'Либан': 'Lebanon',
    'Етиопија': 'Ethiopia',
    'Полска': 'Poland',
    'Боливија': 'Bolivia',
    'Перу': 'Peru',
    'Бразил': 'Brazil',
    'Сенегал': 'Senegal',
    'Унгарија': 'Hungary',
}
