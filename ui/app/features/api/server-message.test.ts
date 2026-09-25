import {describe, expect, it} from 'vitest'
import {serverMessage} from './server-message'

// The answers below are the ones the corpus API really gives.
describe('serverMessage', () => {
  it('reads the explanation of a refused search', () => {
    const answer = {detail: 'Provide text, a lemma, a PoS tag, or a UD tag.'}

    expect(serverMessage(answer)).toBe('Provide text, a lemma, a PoS tag, or a UD tag.')
  })

  it('names the field a message is about', () => {
    expect(serverMessage({q: 'Longer than 100 characters.'})).toBe('q: Longer than 100 characters.')
    expect(serverMessage({q: ['Longer than 100 characters.']})).toBe('q: Longer than 100 characters.')
  })

  it('gives nothing when the corpus sent no explanation', () => {
    expect(serverMessage(undefined)).toBeNull()
    expect(serverMessage('<html>Bad Gateway</html>')).toBeNull()
    expect(serverMessage({})).toBeNull()
  })
})
