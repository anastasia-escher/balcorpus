/**
 * Latin letters that look exactly like a Macedonian Cyrillic letter.
 * A word typed as "тоj" (Cyrillic т and о, Latin j) looks right on screen but
 * matches nothing in the corpus; swapping the look-alikes makes it "тој".
 */
const LATIN_TO_CYRILLIC: Record<string, string> = {
  a: 'а', c: 'с', e: 'е', j: 'ј', k: 'к', o: 'о', p: 'р', s: 'ѕ', x: 'х', y: 'у',
  A: 'А', B: 'В', C: 'С', E: 'Е', H: 'Н', J: 'Ј', K: 'К', M: 'М', O: 'О', P: 'Р',
  S: 'Ѕ', T: 'Т', X: 'Х', Y: 'У',
  // Accented letters: a Latin è looks like ѐ. Nothing Latin looks like ѝ
  // (a Latin ì is an i, not an и), so it has no entry here.
  è: 'ѐ', È: 'Ѐ',
}

const CYRILLIC_LETTER = /\p{Script=Cyrillic}/u

/**
 * Swap Latin look-alikes for their Cyrillic letters, but only in a word that
 * already has Cyrillic in it. A word typed fully in Latin ("slovo") is left
 * alone: there is no telling it was meant to be Cyrillic, and swapping only
 * some of its letters would give nonsense like "ѕlоvо".
 *
 * Example: fixLatinLookalikes('тоj') === 'тој', fixLatinLookalikes('slovo') === 'slovo'
 * and fixLatinLookalikes('сè') === 'сѐ'
 */
export function fixLatinLookalikes(word: string): string {
  if (!CYRILLIC_LETTER.test(word)) {
    return word
  }

  // A grave accent can arrive as a separate mark after the letter (е + ̀).
  // The corpus stores ѐ and ѝ as one character each, so the two are joined.
  const joined = word.normalize('NFC')

  let fixed = ''
  for (const letter of joined) {
    fixed += LATIN_TO_CYRILLIC[letter] ?? letter
  }
  return fixed
}
