import {describe, expect, it} from 'vitest'
import {fixLatinLookalikes} from './cyrillic-lookalikes'

describe('fixLatinLookalikes', () => {
  it('swaps a Latin j in a Cyrillic word for the Cyrillic ј', () => {
    expect(fixLatinLookalikes('тоj')).toBe('тој')
  })

  it('swaps several look-alikes, capitals included', () => {
    // Latin T, o, a and e between the Cyrillic п, л and т.
    expect(fixLatinLookalikes('Toплaтe')).toBe('Топлате')
  })

  it('swaps a Latin è for the Cyrillic ѐ', () => {
    expect(fixLatinLookalikes('сè')).toBe('сѐ')
  })

  it('joins a separately typed grave accent into ѐ and ѝ', () => {
    expect(fixLatinLookalikes('се\u0300')).toBe('сѐ')
    expect(fixLatinLookalikes('и\u0300')).toBe('ѝ')
  })

  it('leaves a word typed fully in Latin alone', () => {
    expect(fixLatinLookalikes('slovo')).toBe('slovo')
  })

  it('leaves a correct Cyrillic word as it is', () => {
    expect(fixLatinLookalikes('тој')).toBe('тој')
  })
})
