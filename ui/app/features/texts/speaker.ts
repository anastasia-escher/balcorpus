/**
 * Reading what the corpus records about a person.
 *
 * Most of a speaker's fields are empty for most people, so everything here is
 * about telling "nothing recorded" apart from a value, and about putting two
 * fields that belong together on one line.
 */

import type {SpeakerDetails} from './texts.types'

// The two fields every speaker has. Anything beyond them is what makes a
// person worth opening a window for.
const NAME_FIELDS = ['speaker_id', 'full_name']

/**
 * Whether the corpus knows anything about this person beyond their name.
 *
 * The table uses it to decide whether a name is worth making clickable: an
 * author with nothing recorded would open an empty window.
 */
export function hasSpeakerDetails(speaker: SpeakerDetails): boolean {
  return Object.entries(speaker).some(
    ([field, value]) => !NAME_FIELDS.includes(field) && value !== null && value !== ''
  )
}

/**
 * Where the person was born, with the kind of place in brackets.
 *
 * Example: birthplace({place_of_birth: 'Shtip', place_type: 'town'}) ->
 * 'Shtip (town)'
 */
export function birthplace(speaker: SpeakerDetails): string | null {
  if (!speaker.place_of_birth) {
    return null
  }

  if (!speaker.place_type) {
    return speaker.place_of_birth
  }

  return `${speaker.place_of_birth} (${speaker.place_type})`
}

/**
 * How far the person studied, together with whatever the editors wrote
 * beside it.
 *
 * Example: 'tertiary — studied in Belgrade'
 */
export function education(speaker: SpeakerDetails): string | null {
  const parts = [speaker.education_level, speaker.education_note].filter(Boolean)
  return parts.length ? parts.join(' — ') : null
}

/**
 * The person's languages, first to third, as the corpus records them.
 *
 * Example: languages({l1: 'mk', l2: 'sr', l3: null}) -> 'mk, sr'
 */
export function languages(speaker: SpeakerDetails): string | null {
  const spoken = [speaker.l1, speaker.l2, speaker.l3].filter(Boolean)
  return spoken.length ? spoken.join(', ') : null
}
