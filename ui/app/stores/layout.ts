import {ref} from 'vue'
import {defineStore} from 'pinia'

export const useLayoutStore = defineStore('layout', () => {
  const mobileNavigationOpen = ref(false)
  const darkModeEnabled = ref(false)

  const initializeTheme = () => {
    darkModeEnabled.value = document.documentElement.classList.contains('dark')
  }

  const toggleMobileNavigation = () => {
    mobileNavigationOpen.value = !mobileNavigationOpen.value
  }

  const closeMobileNavigation = () => {
    mobileNavigationOpen.value = false
  }

  const toggleTheme = () => {
    darkModeEnabled.value = !darkModeEnabled.value
    document.documentElement.classList.toggle('dark', darkModeEnabled.value)
  }

  return {
    mobileNavigationOpen,
    darkModeEnabled,
    initializeTheme,
    toggleMobileNavigation,
    closeMobileNavigation,
    toggleTheme,
  }
})
