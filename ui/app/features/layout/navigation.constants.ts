export interface NavigationLink {
  path: string
  label: string
  icon: string
}

export const NAVIGATION_LINKS: readonly NavigationLink[] = [
  { path: '/', label: 'Home', icon: 'pi pi-home' },
]
