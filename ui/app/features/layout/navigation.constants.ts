export interface NavigationLink {
  path: string
  labelKey: string
  icon: string
}

export const NAVIGATION_LINKS: readonly NavigationLink[] = [
  {path: '/', labelKey: 'navigation.home', icon: 'i-lucide-house'},
]
