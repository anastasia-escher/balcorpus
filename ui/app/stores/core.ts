
import {defineStore} from 'pinia'
import {ref} from 'vue'
import {useAPI} from '~/composables/useAPI'



export const useCoreStore = defineStore(
  'coreData',
  () => {
    const test = 'test'

    return {
      test
    }
  },
  {
    persist: true,
  }
)
