/**
 * Reading a text's metadata the way a page needs to print it.
 *
 * The corpus stores what it was given, which means empty cells and, in a few
 * columns, several values crammed into one string. Turning that into
 * something readable is a job of its own, kept out of the components.
 *
 * Nothing recorded comes back as null rather than as a dash, so that a caller
 * can tell an empty field from a filled one. Whether a dash is printed, or the
 * field left out altogether, is the page's decision.
 */

/** What is printed where the metadata simply has no value. */
export const MISSING_VALUE = '—'

/**
 * A column that may hold several values separated by a semicolon, spaced out
 * so it reads as a list: "drama;prose", "standard;dialectal".
 *
 * Example: readableList('drama;prose') -> 'drama, prose'
 * Example: readableList(null) -> null
 */
export function readableList(value: string | null): string | null {
  if (!value) {
    return null
  }

  const parts = value
    .split(';')
    .map(part => part.trim())
    .filter(Boolean)

  return parts.length ? parts.join(', ') : null
}
