import {useToast} from 'primevue/usetoast'
import {useRuntimeConfig} from '#app'
import {useI18n} from 'vue-i18n'

/**
 * HTTP method types accepted by fetch APIs
 */
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS'

/**
 * Interface for API request options
 */
interface APIOptions {
  method?: HttpMethod
  headers?: Record<string, string>
  body?: any
  params?: Record<string, string>
}

/**
 * Response type returned by useAPI
 */
interface APIResponse<T> {
  data: {value: T | null}
  error: {value: Error | null}
}

/**
 * Gets CSRF token from cookies
 * @returns string | null The CSRF token or null if not found
 */
const getCsrfToken = (): string | null => {
  const cookies = document.cookie.split(';')
  const csrfCookie = cookies.find(cookie => cookie.trim().startsWith('csrftoken='))

  if (!csrfCookie) {
    return null
  }

  const separatorIndex = csrfCookie.indexOf('=')
  return separatorIndex === -1 ? null : csrfCookie.slice(separatorIndex + 1)
}

/**
 * Simplified API composable for client-side rendering only.
 * Call it during component setup, then use its returned request function in
 * event handlers. This keeps PrimeVue's Toast injection in Vue's setup scope.
 * @returns A request function that shows a PrimeVue toast on errors.
 */
export const useAPI = () => {
  const config = useRuntimeConfig()
  const toast = useToast()
  const {t} = useI18n()

  return async <T = any>(
    endpoint: string,
    options: APIOptions = {}
  ): Promise<APIResponse<T>> => {
    const {method = 'GET'} = options

    // Prepare headers with CSRF token for unsafe methods
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    }

    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
      const token = getCsrfToken()
      if (token) {
        headers['X-CSRFToken'] = token
      }
    }

    // Build URL with query parameters if needed
    let url = `${config.public.baseURL}/api/v1/${endpoint}`
    if (options.params) {
      const queryParams = new URLSearchParams()
      Object.entries(options.params).forEach(([key, value]) => {
        queryParams.append(key, value)
      })
      url += `?${queryParams.toString()}`
    }

    try {
      const response = await $fetch<T>(url, {
        method,
        headers,
        body: options.body,
        credentials: 'include',
      })

      return {
        data: {value: response},
        error: {value: null},
      }
    } catch (error: any) {
      const statusCode = error.response?.status ?? t('api.networkStatus')
      const message = error.message || t('api.unknownError')
      toast.add({
        severity: 'error',
        summary: t('api.errorSummary', {statusCode}),
        detail: message,
        life: 5000,
      })

      return {
        data: {value: null},
        error: {value: error},
      }
    }
  }
}
