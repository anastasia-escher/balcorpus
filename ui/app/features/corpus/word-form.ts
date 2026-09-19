/**
 * The written form of a word, as the corpus recorded it.
 *
 * Every token carries two readings: ``source``, the form as it stands in the
 * original, and ``diplomatic``, a transcription of it. Most tokens have only
 * the first. The concordance and the text page show the same word, so the
 * rule for choosing between the two lives here rather than in either of them.
 */

/**
 * Anything the corpus recorded a written form for: a token of a text, or a
 * hit in a search.
 */
interface WrittenWord {
  source: string | null
  diplomatic: string | null
}

/**
 * The word as it is written, preferring the source reading.
 *
 * A word with neither reading gives an empty string: the corpus has rows that
 * carry only annotation, and they must not print the word "null".
 *
 * Example: wordForm({source: 'Антон', diplomatic: null}) -> 'Антон'
 */
export function wordForm(word: WrittenWord): string {
  return word.source || word.diplomatic || ''
}
