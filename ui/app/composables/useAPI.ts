import {useRuntimeConfig} from '#app'
import {useI18n} from 'vue-i18n'
import {serverMessage} from '~/features/api/server-message'

/**
 * Interface for API request options
 */
interface APIOptions {
  params?: Record<string, string>
  /**
   * Do not raise a toast when the corpus answers "not found".
   *
   * Set it where a missing thing is an ordinary answer the caller already
   * explains on the page — a text_id nobody has, a page number past the end
   * of a list. Everything else, a broken connection included, still raises
   * one, so this never hides a real failure.
   */
  quietNotFound?: boolean
}

/**
 * Response type returned by useAPI
 */
interface APIResponse<T> {
  data: {value: T | null}
  error: {value: Error | null}
}

/**
 * Simplified API composable for client-side rendering only.
 * Call it during component setup, then use its returned request function in
 * event handlers. This keeps Nuxt UI's useToast() in Vue's setup scope.
 * @returns A request function that shows a toast on errors.
 */
export const useAPI = () => {
  const config = useRuntimeConfig()
  const toast = useToast()
  const {t} = useI18n()

  return async <T = any>(endpoint: string, options: APIOptions = {}): Promise<APIResponse<T>> => {
    try {
      const response = await $fetch<T>(`${config.public.baseURL}/api/v1/${endpoint}`, {
        query: options.params,
      })

      return {
        data: {value: response},
        error: {value: null},
      }
    } catch (error: any) {
      const status = error.response?.status ?? error.status
      const notFound = status === 404

      if (!(notFound && options.quietNotFound)) {
        const statusCode = status ?? t('api.networkStatus')
        // What the corpus said about it, e.g. "q: Longer than 100 characters.",
        // is more use to the reader than the technical summary of the request.
        const message = serverMessage(error.data) || error.message || t('api.unknownError')
        toast.add({
          color: 'error',
          title: t('api.errorSummary', {statusCode}),
          description: message,
          duration: 5000,
        })
      }

      return {
        data: {value: null},
        error: {value: error},
      }
    }
  }
}
