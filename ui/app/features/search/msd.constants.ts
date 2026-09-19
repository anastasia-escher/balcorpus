import type {MsdCategory, MsdProperty, MsdValue} from './msd.types'

/**
 * The MULTEXT-East morphosyntactic description of Macedonian, written out so
 * the search form can offer it in words instead of codes.
 *
 * Every part of speech and every code below comes from the specification at
 * https://nl.ijs.si/ME/V6/msd/html/msd-mk.html — including the gaps: an
 * adjective has nothing at position 5 and a particle nothing at position 1,
 * which is why the positions are written down rather than counted.
 *
 * Every value of the specification is offered, even one the corpus does not
 * carry yet, because only part of the corpus has been annotated so far.
 */

/**
 * The values of one group of choices.
 *
 * The key is the character the tag uses, the value is the last part of the
 * translation key: values('gender', {m: 'masculine'}) gives the code 'm' the
 * label key 'search.msd.values.gender.masculine'.
 */
const values = (group: string, labelNames: Record<string, string>): readonly MsdValue[] =>
  Object.entries(labelNames).map(([code, labelName]) => ({
    code,
    labelKey: `search.msd.values.${group}.${labelName}`,
  }))

/** One property of a part of speech; its label key follows from its name. */
const property = (
  name: string,
  position: number,
  propertyValues: readonly MsdValue[]
): MsdProperty => ({
  name,
  position,
  labelKey: `search.msd.properties.${name}`,
  values: propertyValues,
})

// Groups of values that more than one part of speech uses. A group is shared
// only when the choices really are the same: a noun's cases are not a
// pronoun's cases, so those two stay apart.
const GENDERS = values('gender', {m: 'masculine', f: 'feminine', n: 'neuter'})
const NUMBERS = values('number', {s: 'singular', p: 'plural'})
const DEGREES = values('degree', {p: 'positive', c: 'comparative', s: 'superlative'})
const PERSONS = values('person', {'1': 'first', '2': 'second', '3': 'third'})
const FORMATIONS = values('formation', {s: 'simple', c: 'compound'})
const YES_OR_NO = values('yesNo', {n: 'no', y: 'yes'})
const DEFINITENESS = values('definiteness', {
  n: 'indefinite',
  y: 'definite',
  p: 'definiteNear',
  d: 'definiteFar',
})

// A noun can also stand in the count form, the one a numeral asks for.
const NOUN_NUMBERS = values('number', {s: 'singular', p: 'plural', t: 'count'})

export const MSD_CATEGORIES: readonly MsdCategory[] = [
  {
    code: 'N',
    labelKey: 'search.msd.categories.noun',
    properties: [
      property('type', 1, values('nounType', {c: 'common', p: 'proper'})),
      property('gender', 2, GENDERS),
      property('number', 3, NOUN_NUMBERS),
      property('case', 4, values('nounCase', {n: 'nominative', v: 'vocative', o: 'oblique'})),
      property('definiteness', 5, DEFINITENESS),
    ],
  },
  {
    code: 'V',
    labelKey: 'search.msd.categories.verb',
    properties: [
      property('type', 1, values('verbType', {m: 'main', a: 'auxiliary', o: 'modal'})),
      property('aspect', 2, values('aspect', {p: 'progressive', e: 'perfective', b: 'biaspectual'})),
      property('verbForm', 3, values('verbForm', {i: 'indicative', m: 'imperative'})),
      property('tense', 4, values('tense', {p: 'present', i: 'imperfect', a: 'aorist', c: 'compound'})),
      property('person', 5, PERSONS),
      property('number', 6, NUMBERS),
      property('gender', 7, GENDERS),
      property('negative', 8, YES_OR_NO),
    ],
  },
  {
    code: 'A',
    labelKey: 'search.msd.categories.adjective',
    properties: [
      property(
        'type',
        1,
        values('adjectiveType', {
          f: 'qualificative',
          g: 'general',
          s: 'possessive',
          o: 'ordinal',
          p: 'participle',
        })
      ),
      property('degree', 2, DEGREES),
      property('gender', 3, GENDERS),
      property('number', 4, NUMBERS),
      // Position 5 holds nothing for a Macedonian adjective.
      property('definiteness', 6, DEFINITENESS),
    ],
  },
  {
    code: 'P',
    labelKey: 'search.msd.categories.pronoun',
    properties: [
      property(
        'type',
        1,
        values('pronounType', {
          p: 'personal',
          d: 'demonstrative',
          i: 'indefinite',
          q: 'interrogative',
          r: 'relative',
          x: 'reflexive',
          z: 'negative',
          g: 'general',
        })
      ),
      property('person', 2, PERSONS),
      property('gender', 3, GENDERS),
      property('number', 4, NUMBERS),
      property('case', 5, values('pronounCase', {n: 'nominative', d: 'dative', a: 'accusative'})),
      property('clitic', 6, YES_OR_NO),
      property('definiteness', 7, DEFINITENESS),
    ],
  },
  {
    code: 'R',
    labelKey: 'search.msd.categories.adverb',
    properties: [
      property(
        'type',
        1,
        values('adverbType', {g: 'general', a: 'adjectival', v: 'verbal', d: 'modal'})
      ),
      property('degree', 2, DEGREES),
    ],
  },
  {
    code: 'M',
    labelKey: 'search.msd.categories.numeral',
    properties: [
      property('form', 1, values('numeralForm', {d: 'digit', r: 'roman', l: 'letter'})),
      property('type', 2, values('numeralType', {c: 'cardinal', p: 'pronominal', s: 'special'})),
      property('gender', 3, GENDERS),
      property('definiteness', 4, DEFINITENESS),
    ],
  },
  {
    code: 'S',
    labelKey: 'search.msd.categories.adposition',
    properties: [
      property('type', 1, values('adpositionType', {p: 'preposition'})),
      property('formation', 2, FORMATIONS),
    ],
  },
  {
    code: 'C',
    labelKey: 'search.msd.categories.conjunction',
    properties: [
      property('type', 1, values('conjunctionType', {c: 'coordinating', s: 'subordinating'})),
      property('formation', 2, FORMATIONS),
    ],
  },
  {
    code: 'Q',
    labelKey: 'search.msd.categories.particle',
    properties: [
      // Position 1 holds nothing for a Macedonian particle.
      property('formation', 2, FORMATIONS),
    ],
  },
  {
    code: 'I',
    labelKey: 'search.msd.categories.interjection',
    properties: [],
  },
  {
    code: 'Y',
    labelKey: 'search.msd.categories.abbreviation',
    properties: [],
  },
  {
    code: 'X',
    labelKey: 'search.msd.categories.residual',
    properties: [
      property(
        'type',
        1,
        values('residualType', {
          f: 'foreign',
          t: 'typo',
          w: 'web',
          e: 'emo',
          h: 'hashtag',
          a: 'at',
          p: 'program',
        })
      ),
    ],
  },
  {
    code: 'Z',
    labelKey: 'search.msd.categories.punctuation',
    properties: [],
  },
]

/** The part of speech written with this letter, or undefined if there is none. */
export const findMsdCategory = (code: string | null): MsdCategory | undefined =>
  MSD_CATEGORIES.find(category => category.code === code)
