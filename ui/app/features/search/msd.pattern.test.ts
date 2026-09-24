import {describe, expect, it} from 'vitest'
import {buildMsdPattern} from './msd.pattern'
import {findMsdCategory} from './msd.constants'
import type {MsdSelection} from './msd.types'

/** What the form builds when this part of speech and these values are chosen. */
const pattern = (categoryCode: string, selection: MsdSelection) =>
  buildMsdPattern(findMsdCategory(categoryCode)!, selection)

describe('buildMsdPattern', () => {
  it('asks for a whole part of speech when nothing else is chosen', () => {
    expect(pattern('N', {})).toBe('N*')
  })

  it('leaves a wildcard where a property was not chosen', () => {
    expect(pattern('N', {gender: 'f', definiteness: 'y'})).toBe('N?f??y*')
  })

  it('stops at the last property that was chosen', () => {
    expect(pattern('V', {verbForm: 'm'})).toBe('V??m*')
  })

  it('counts the positions the specification leaves empty', () => {
    // A Macedonian adjective has nothing at the fifth position, so its
    // definiteness is the sixth character; a particle has nothing at the
    // first. Counting properties instead of positions would put both one
    // place too early, and the corpus would quietly answer with nothing.
    expect(pattern('A', {definiteness: 'n'})).toBe('A?????n*')
    expect(pattern('Q', {formation: 's'})).toBe('Q?s*')
  })
})
