/**
 * Cutting a sentence into the pieces the result list draws: the words that
 * were matched, and the plain text around them.
 *
 * The corpus says where each matched word stands, because only it can know:
 * it assembled the sentence out of its tokens. Looking the word up in the
 * finished string here would be guesswork — the same form may stand in the
 * sentence twice, and a search with a nearby word marks two places at once.
 */

import type {SentenceSpan} from './search.types'

/** What a piece of the sentence is: one of the matches, or plain text. */
export type SentenceMark = 'match' | 'nearby' | null

export interface SentencePiece {
  text: string
  mark: SentenceMark
}

/**
 * Split the sentence at the given places, in the order they are read.
 *
 * Example: splitSentenceIntoPieces('и ние и', [2, 5], [0, 1]) ->
 *          [{text: 'и', mark: 'nearby'}, {text: ' ', mark: null},
 *           {text: 'ние', mark: 'match'}, {text: ' и', mark: null}]
 *
 * A span that is null is simply not marked.
 */
export function splitSentenceIntoPieces(
  sentence: string,
  matchSpan: SentenceSpan | null,
  nearbySpan: SentenceSpan | null
): SentencePiece[] {
  const marked: {span: SentenceSpan; mark: SentenceMark}[] = []

  if (matchSpan) {
    marked.push({span: matchSpan, mark: 'match'})
  }
  if (nearbySpan) {
    marked.push({span: nearbySpan, mark: 'nearby'})
  }

  marked.sort((one, other) => one.span[0] - other.span[0])

  const pieces: SentencePiece[] = []
  let readUpTo = 0

  for (const {span, mark} of marked) {
    const [start, end] = span

    if (start > readUpTo) {
      pieces.push({text: sentence.slice(readUpTo, start), mark: null})
    }

    pieces.push({text: sentence.slice(start, end), mark})
    readUpTo = end
  }

  if (readUpTo < sentence.length) {
    pieces.push({text: sentence.slice(readUpTo), mark: null})
  }

  return pieces
}
