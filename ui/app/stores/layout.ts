import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useLayoutStore = defineStore('layout', () => {
  const mobileNavigationOpen = ref(false)
  const darkModeEnabled = ref(false)

  function initializeTheme() {
    darkModeEnabled.value = document.documentElement.classList.contains('p-dark')
  }

  function toggleMobileNavigation() {
    mobileNavigationOpen.value = !mobileNavigationOpen.value
  }

  function closeMobileNavigation() {
    mobileNavigationOpen.value = false
  }

  function toggleTheme() {
    darkModeEnabled.value = !darkModeEnabled.value
    document.documentElement.classList.toggle('p-dark', darkModeEnabled.value)
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
