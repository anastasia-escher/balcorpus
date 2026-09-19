/**
 * Reading a run of sentences as a text rather than as separate rows.
 *
 * A play records who is speaking on every line, but printing the name above
 * every line turns the page into a list. The name belongs where the speaker
 * changes, the way a printed play sets it.
 */

import type {TextSentence} from './texts.types'

/**
 * Whether this sentence begins a new speaker's turn, and so should carry the
 * name above it.
 *
 * The first sentence of a page always carries it: the reader has no line
 * above to carry it over from.
 *
 * Example: for three sentences spoken by A, A, B -> true, false, true
 */
export function startsNewTurn(sentences: TextSentence[], position: number): boolean {
  const sentence = sentences[position]
  if (!sentence?.speaker) {
    return false
  }

  if (position === 0) {
    return true
  }

  return sentences[position - 1]?.speaker?.speaker_id !== sentence.speaker.speaker_id
}
