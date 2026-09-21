import {describe, expect, it} from 'vitest'
import {splitSentenceIntoPieces} from './highlight'

describe('splitSentenceIntoPieces', () => {
  it('marks the matched word inside the sentence', () => {
    expect(splitSentenceIntoPieces('Да молим.', [3, 8], null)).toEqual([
      {text: 'Да ', mark: null},
      {text: 'молим', mark: 'match'},
      {text: '.', mark: null},
    ])
  })

  it('marks both words, in the order they are read', () => {
    // The nearby word stands first here, although it is passed second.
    expect(splitSentenceIntoPieces('што направи од нас', [15, 18], [4, 11])).toEqual([
      {text: 'што ', mark: null},
      {text: 'направи', mark: 'nearby'},
      {text: ' од ', mark: null},
      {text: 'нас', mark: 'match'},
    ])
  })

  it('tells two equal forms apart by their place', () => {
    expect(splitSentenceIntoPieces('и ние и', [6, 7], [0, 1])).toEqual([
      {text: 'и', mark: 'nearby'},
      {text: ' ние ', mark: null},
      {text: 'и', mark: 'match'},
    ])
  })

  it('leaves the sentence plain when there is nothing to mark', () => {
    expect(splitSentenceIntoPieces('Да молим.', null, null)).toEqual([{text: 'Да молим.', mark: null}])
  })

  it('ignores a span that does not fit the sentence', () => {
    expect(splitSentenceIntoPieces('Да', [0, 99], null)).toEqual([{text: 'Да', mark: null}])
  })
})
