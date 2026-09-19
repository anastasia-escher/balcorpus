import type {MsdCategory, MsdSelection} from './msd.types'

/** Stands for one character the search does not care about. */
const ANY_CHARACTER = '?'

/** Stands for the rest of the tag, however long it is — or for nothing. */
const REST_OF_TAG = '*'

/**
 * Turn a chosen part of speech and its chosen properties into the tag query
 * the corpus understands.
 *
 * The pattern is written position by position: a property that was chosen
 * contributes its own character, one that was not becomes '?'. Everything
 * after the last chosen property becomes '*', because the annotation stops
 * writing positions once it has nothing more to say — feminine pronouns sit
 * in the corpus as tags of five, seven and eight characters.
 *
 * Example: for the noun category and { gender: 'f', definiteness: 'y' } the
 * pattern is 'N?f??y*', and a part of speech chosen on its own gives 'N*'.
 */
export const buildMsdPattern = (category: MsdCategory, selection: MsdSelection): string => {
  const chosenPositions = category.properties
    .filter(property => selection[property.name])
    .map(property => property.position)

  if (chosenPositions.length === 0) {
    return category.code + REST_OF_TAG
  }

  const lastChosenPosition = Math.max(...chosenPositions)
  let pattern = category.code

  for (let position = 1; position <= lastChosenPosition; position += 1) {
    // A position the specification leaves empty for this part of speech has no
    // property, and is therefore left to the wildcard as well.
    const property = category.properties.find(candidate => candidate.position === position)
    const chosenCode = property ? selection[property.name] : undefined
    pattern += chosenCode || ANY_CHARACTER
  }

  return pattern + REST_OF_TAG
}
