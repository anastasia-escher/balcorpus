import {computed, ref} from 'vue'
import {CONTEXT_PARAMETER_BY_KIND, DEFAULT_CONTEXT_DISTANCE, findContextDistance} from './search.constants'
import {createMorphologySelection} from './morphology-selection'
import type {SearchKind} from './search.types'

// The way of describing the nearby word the block starts out with. Morphology
// is what this block is mostly used for: "a verb in the aorist".
const DEFAULT_CONTEXT_KIND: SearchKind = 'tag'

/**
 * The second half of a search: a word that has to stand near the match.
 *
 * It is described the same four ways the searched word is — by word form, by
 * lemma, by morphology or by UD relation — and one of them at a time, chosen
 * by ``kind``. The distance is a window of at most three tokens to either
 * side; the corpus looks no further.
 *
 * Example: kind 'tag', a verb in the aorist, distance 'exactly2Before' asks
 * the corpus for near_pos=V???a*&near_from=-2&near_to=-2
 */
export function createContextCriteria() {
  // Whether the block is open in the form. Kept here rather than in the form
  // because all four search tabs show the same block and it should stay as
  // the user left it when they move between them.
  const isOpen = ref(false)
  const kind = ref<SearchKind>(DEFAULT_CONTEXT_KIND)
  const textQuery = ref('')
  const lemma = ref('')
  const udTag = ref<string | null>(null)
  const morphology = createMorphologySelection()
  const distanceCode = ref(DEFAULT_CONTEXT_DISTANCE)

  /** What the chosen way of describing the word amounts to, e.g. 'V???a*'. */
  const query = computed(() => {
    if (kind.value === 'text') {
      return textQuery.value.trim()
    }
    if (kind.value === 'lemma') {
      return lemma.value.trim()
    }
    if (kind.value === 'tag') {
      return morphology.pattern.value
    }
    return udTag.value ?? ''
  })

  /** True once the block says something the corpus can look for. */
  const isFilledIn = computed(() => Boolean(query.value))

  /**
   * The parameters this block adds to a search, or nothing at all when it has
   * not been filled in.
   *
   * Example: { near_pos: 'V???a*', near_from: '-2', near_to: '-2' }
   */
  const toParameters = (): Record<string, string> => {
    const distance = findContextDistance(distanceCode.value)

    if (!isFilledIn.value || !distance) {
      return {}
    }

    return {
      [CONTEXT_PARAMETER_BY_KIND[kind.value]]: query.value,
      near_from: String(distance.offsetFrom),
      near_to: String(distance.offsetTo),
    }
  }

  /** Put the block back the way it is first seen, leaving it open if it was. */
  const reset = () => {
    kind.value = DEFAULT_CONTEXT_KIND
    textQuery.value = ''
    lemma.value = ''
    udTag.value = null
    morphology.reset()
    distanceCode.value = DEFAULT_CONTEXT_DISTANCE
  }

  /**
   * Open the block, or close it and drop what it asked for.
   *
   * Closing has to empty it: a folded-away block is invisible, and a search
   * that silently kept asking about a word nobody can see would be a puzzle.
   */
  const toggle = () => {
    isOpen.value = !isOpen.value

    if (!isOpen.value) {
      reset()
    }
  }

  return {
    isOpen,
    toggle,
    kind,
    query,
    textQuery,
    lemma,
    udTag,
    morphology,
    distanceCode,
    isFilledIn,
    toParameters,
    reset,
  }
}
