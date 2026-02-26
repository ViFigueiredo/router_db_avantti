export const useApi = () => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl

  const fetchApi = async (endpoint: string, options: any = {}) => {
    return await $fetch(`${apiUrl}${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
      }
    })
  }

  return {
    fetchApi
  }
}
