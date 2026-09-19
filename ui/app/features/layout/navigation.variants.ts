/**
 * How the navigation bar is painted, which is a different question from what
 * is in it, and so is kept apart from the list of links.
 *
 * 'over-photo' is for a page that opens with a cover photograph: the bar
 * floats on top of it in light ink, under a dark scrim. 'plain' is the bar on
 * its own, in the normal flow of the page.
 */

export type NavigationVariant = 'over-photo' | 'plain'

/** A page that asks for nothing gets the plain bar. */
export const DEFAULT_NAVIGATION_VARIANT: NavigationVariant = 'plain'

// So that a page can write definePageMeta({navigationVariant: 'over-photo'})
// and have it checked rather than taken on trust.
declare module 'vue-router' {
  interface RouteMeta {
    navigationVariant?: NavigationVariant
  }
}
