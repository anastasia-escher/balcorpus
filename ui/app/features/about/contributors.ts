/**
 * The people behind the corpus.
 *
 * Names and institutions are not translated, so they live here as data rather
 * than in the locale files; only the headings around them go through i18n.
 *
 * One entry looks like:
 * { name: "Anastasia Escher", affiliation: "ETH Zurich, NEXUS Personalized Health" }
 */

export interface Contributor {
  name: string
  affiliation: string
}

export const CONTRIBUTORS: readonly Contributor[] = [
  {name: 'Anastasia Escher', affiliation: 'ETH Zurich, NEXUS Personalized Health'},
]
