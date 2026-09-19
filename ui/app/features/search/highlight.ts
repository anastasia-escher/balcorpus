/**
 * Splitting a sentence around the word form that was matched, so the result
 * list can show it the way a concordance does: the hit standing out inside
 * the sentence it came from.
 */

export interface SentenceParts {
  before: string
  match: string
  after: string
}

/** True for anything a language uses as a letter, Cyrillic included. */
function isLetter(character: string | undefined): boolean {
  return character !== undefined && /\p{L}/u.test(character)
}

/**
 * Find the word form inside the sentence and split the sentence there.
 *
 * Only a whole word counts, so looking for "со" in "Драма со музика" matches
 * the preposition and not the "со" inside another word. When the form cannot
 * be found the whole sentence comes back as `before`, and the caller simply
 * renders it unmarked.
 *
 * Example: splitSentenceAroundToken('Драма со музика', 'со')
 *          -> { before: 'Драма ', match: 'со', after: ' музика' }
 */
export function splitSentenceAroundToken(
  sentence: string | null | undefined,
  token: string | null | undefined
): SentenceParts {
  const text = sentence ?? ''
  if (!text || !token) {
    return {before: text, match: '', after: ''}
  }

  let searchFrom = 0
  while (searchFrom <= text.length) {
    const start = text.indexOf(token, searchFrom)
    if (start === -1) {
      break
    }

    const end = start + token.length
    const standsAlone = !isLetter(text[start - 1]) && !isLetter(text[end])
    if (standsAlone) {
      return {
        before: text.slice(0, start),
        match: text.slice(start, end),
        after: text.slice(end),
      }
    }

    searchFrom = start + 1
  }

  return {before: text, match: '', after: ''}
}
