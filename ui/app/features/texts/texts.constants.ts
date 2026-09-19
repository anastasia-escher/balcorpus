/** How many texts one page of the list holds. */
export const TEXTS_PAGE_SIZE = 25

/**
 * How many sentences one page of a text holds.
 *
 * This is the most the corpus will hand out at once. A text of average length
 * runs to some fourteen thousand tokens, so it is read in chunks either way;
 * asking for the largest chunk allowed means the fewest clicks through it.
 */
export const TEXT_SENTENCES_PAGE_SIZE = 100
