/**
 * The shapes the morphology search is built out of.
 *
 * A MULTEXT-East tag is a string of single characters: the part of speech
 * first, then one character per property, and every property always sits in
 * the same place. The specification for Macedonian, which these types
 * describe, is at https://nl.ijs.si/ME/V6/msd/html/msd-mk.html
 */

/** One value a property can take, e.g. feminine, which is written 'f'. */
export interface MsdValue {
  code: string
  labelKey: string
}

/**
 * One property of a part of speech, at its fixed place in the tag.
 *
 * ``position`` counts the way the specification counts: the part of speech
 * itself is 0, so a noun's gender is 2. The numbers are not always
 * consecutive — an adjective's definiteness is 6, because position 5 holds
 * nothing in Macedonian.
 *
 * Example: {
 *   name: 'gender',
 *   position: 2,
 *   labelKey: 'search.msd.properties.gender',
 *   values: [{ code: 'm', labelKey: 'search.msd.values.gender.masculine' }],
 * }
 */
export interface MsdProperty {
  name: string
  position: number
  labelKey: string
  values: readonly MsdValue[]
}

/** One part of speech, with the properties it can carry. */
export interface MsdCategory {
  code: string
  labelKey: string
  properties: readonly MsdProperty[]
}

/**
 * What the form has chosen: for each property, the code chosen for it. A
 * property nobody chose is simply absent.
 *
 * Example: { gender: 'f', definiteness: 'y' }
 */
export type MsdSelection = Record<string, string>
