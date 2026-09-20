/**
 * The shapes the corpus answers with when it is asked about its texts.
 *
 * These mirror the API's own field names rather than renaming them, so that
 * a field can be followed from the table on screen back to the serializer
 * that produced it.
 */

/**
 * A person the corpus knows something about: the author of a text, or the
 * speaker of a recorded passage. Most fields are empty for most people.
 *
 * Example:
 *   {
 *     speaker_id: 'aco_shopov', full_name: 'Ацо Шопов', birth_name: null,
 *     gender: 'male', birthyear: 1923, place_of_birth: 'Shtip',
 *     place_type: 'town', municipality: null, dialect_region: 'east',
 *     education_level: 'tertiary', education_note: null, religion: 'Orthodox',
 *     l1: 'mk', l2: 'sr', l3: null, notes: 'ambassador to Senegal',
 *   }
 */
export interface SpeakerDetails {
  speaker_id: string
  full_name: string
  birth_name: string | null
  gender: string | null
  birthyear: number | null
  place_of_birth: string | null
  place_type: string | null
  municipality: string | null
  dialect_region: string | null
  education_level: string | null
  education_note: string | null
  religion: string | null
  l1: string | null
  l2: string | null
  l3: string | null
  notes: string | null
}

/**
 * One text of the corpus with its metadata. The sentences are not part of
 * this: they are read separately, a page at a time.
 *
 * Example:
 *   {
 *     text_id: 'abadzhiev_pustina_1961', text_name: 'Пустина',
 *     data_genre: 'literature', text_genre: 'prose', variety: 'standard',
 *     variety_note: null, text_date: '1961', year_note: null, source: null,
 *     short_description: null, authors: [ …one SpeakerDetails… ],
 *   }
 */
export interface TextMetadata {
  text_id: string
  text_name: string
  data_genre: string | null
  text_genre: string | null
  variety: string | null
  variety_note: string | null
  text_date: string | null
  year_note: string | null
  source: string | null
  short_description: string | null
  authors: SpeakerDetails[]
}
