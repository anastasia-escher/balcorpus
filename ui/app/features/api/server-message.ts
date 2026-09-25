/**
 * The explanation the corpus sent along with an error, or null.
 *
 * The API answers a refused request in one of two shapes, and both are read:
 *   {detail: 'Provide text, a lemma, a PoS tag, or a UD tag.'} -> that text
 *   {q: 'Longer than 100 characters.'}                         -> 'q: Longer than 100 characters.'
 * A field's message may also come as a list, {q: ['…']}; its first entry is taken.
 *
 * Anything else — no answer at all when the network is down, or an HTML
 * error page — gives null, and the caller falls back to its own message.
 */
export const serverMessage = (data: unknown): string | null => {
  if (!data || typeof data !== 'object') {
    return null
  }

  const answer = data as Record<string, unknown>
  if (typeof answer.detail === 'string') {
    return answer.detail
  }

  for (const [field, message] of Object.entries(answer)) {
    const text = Array.isArray(message) ? message[0] : message
    if (typeof text === 'string') {
      return `${field}: ${text}`
    }
  }

  return null
}
