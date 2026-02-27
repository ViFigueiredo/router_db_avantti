export const useApi = () => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl

  const fetchApi = async <T = unknown>(endpoint: string, options: Record<string, unknown> = {}): Promise<T> => {
    return await $fetch<T>(`${apiUrl}${endpoint}`, {
      ...options,
      headers: {
        ...(options.headers as Record<string, string>),
      }
    })
  }

  return {
    fetchApi
  }
}
