export function useApiUrl(path: string): string {
  const apiBase = useRuntimeConfig().public.apiBase.replace(/\/+$/, '')
  return `${apiBase}/${path.replace(/^\/+/, '')}`
}

export function useApiDocsUrl(): string {
  return useRuntimeConfig().public.apiBase.replace(/\/api\/v1\/?$/, '/docs')
}
