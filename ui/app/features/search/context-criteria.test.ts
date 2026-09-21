import {describe, expect, it} from 'vitest'
import {createContextCriteria} from './context-criteria'

describe('createContextCriteria', () => {
  it('adds nothing to a search while the block is empty', () => {
    const context = createContextCriteria()

    expect(context.toParameters()).toEqual({})
  })

  it('asks for a lemma at the chosen distance', () => {
    const context = createContextCriteria()
    context.kind.value = 'lemma'
    context.lemma.value = 'дојде'
    context.distanceCode.value = 'exactly2Before'

    expect(context.toParameters()).toEqual({near_lemma: 'дојде', near_from: '-2', near_to: '-2'})
  })

  it('asks for the tag pattern built from the chosen morphology', () => {
    const context = createContextCriteria()
    context.morphology.selectCategory('V')
    context.morphology.setValue('tense', 'a')

    expect(context.toParameters()).toEqual({near_pos: 'V???a*', near_from: '-3', near_to: '3'})
  })

  it('sends only the way of describing the word that is chosen now', () => {
    const context = createContextCriteria()
    context.kind.value = 'lemma'
    context.lemma.value = 'дојде'
    context.kind.value = 'text'
    context.textQuery.value = 'дојдовме'

    expect(context.toParameters()).toEqual({near_q: 'дојдовме', near_from: '-3', near_to: '3'})
  })

  it('forgets what it asked for when it is folded away', () => {
    const context = createContextCriteria()
    context.toggle()
    context.kind.value = 'lemma'
    context.lemma.value = 'дојде'

    context.toggle()

    expect(context.isOpen.value).toBe(false)
    expect(context.kind.value).toBe('tag')
    expect(context.toParameters()).toEqual({})
  })
})
