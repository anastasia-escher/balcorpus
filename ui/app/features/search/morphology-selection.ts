import {computed, ref} from 'vue'
import {findMsdCategory} from './msd.constants'
import {buildMsdPattern} from './msd.pattern'
import type {MsdSelection} from './msd.types'

/**
 * The state behind one morphology chooser: a part of speech, the values
 * chosen for its properties, and the tag pattern that follows from the two.
 *
 * This is a factory rather than a single shared object because a search holds
 * two choosers at once — one for the word being looked for, one for a word
 * standing near it — and they must not share their state.
 *
 * Example: selectCategory('V'); setValue('tense', 'a') gives pattern 'V???a*'
 */
export function createMorphologySelection() {
  const categoryCode = ref<string | null>(null)
  const selection = ref<MsdSelection>({})

  const category = computed(() => findMsdCategory(categoryCode.value))

  const pattern = computed(() =>
    category.value ? buildMsdPattern(category.value, selection.value) : ''
  )

  /** Choose a part of speech. Its properties start over. */
  const selectCategory = (code: string | null) => {
    categoryCode.value = code
    // A gender chosen for a noun says nothing about a verb, and the properties
    // are not even the same ones, so nothing is carried over.
    selection.value = {}
  }

  /** Choose the value of one property, or let it mean "any" again with null. */
  const setValue = (propertyName: string, code: string | null) => {
    const chosen = {...selection.value}

    if (code) {
      chosen[propertyName] = code
    } else {
      delete chosen[propertyName]
    }

    selection.value = chosen
  }

  const reset = () => {
    selectCategory(null)
  }

  return {categoryCode, selection, category, pattern, selectCategory, setValue, reset}
}
