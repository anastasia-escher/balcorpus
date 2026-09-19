import {ref} from 'vue'
import {defineStore} from 'pinia'

export const useLayoutStore = defineStore('layout', () => {
  const mobileNavigationOpen = ref(false)

  const toggleMobileNavigation = () => {
    mobileNavigationOpen.value = !mobileNavigationOpen.value
  }

  const closeMobileNavigation = () => {
    mobileNavigationOpen.value = false
  }

  return {
    mobileNavigationOpen,
    toggleMobileNavigation,
    closeMobileNavigation,
  }
})
