/**
 * The people behind the corpus.
 *
 * Names and institutions are not translated, so they live here as data rather
 * than in the locale files; only the headings around them go through i18n.
 *
 * One entry looks like:
 * { name: "Anastasia Escher", affiliation: "ETH Zurich" }
 */

export interface Contributor {
  name: string
  affiliation: string
}

export const CONTRIBUTORS: readonly Contributor[] = [
  {name: 'Olivier Winistörfer', affiliation: 'University of Zurich, Department of Romance Studies'},
  {name: 'Anastasia Escher', affiliation: 'ETH Zurich'},
  {name: 'Maxim Makartsev', affiliation: 'University of Oldenburg'},
  {name: 'Elena Garkusha', affiliation: 'Moscow State University'},
]
