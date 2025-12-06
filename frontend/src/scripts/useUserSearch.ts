import { ref } from 'vue'

export interface UserMention {
  id: number
  username: string
  nickname: string
  photo: string
}

export function useUserSearch() {
  const results = ref<UserMention[]>([])
  const loading = ref(false)

  let debounceTimer: ReturnType<typeof setTimeout>

  const search = (query: string) => {
    clearTimeout(debounceTimer)

    if (!query || query.length < 1) {
      results.value = []
      return
    }

    debounceTimer = setTimeout(async () => {
      loading.value = true
      try {
        const url = new URL('/search', window.location.origin)
        url.searchParams.append('who', query)

        const response = await fetch(url.toString())
        if (!response.ok) throw new Error('Network error')
        const data: UserMention[] = await response.json()
        results.value = data
      } catch {
        results.value = []
      } finally {
        loading.value = false
      }
    }, 300)
  }

  const clear = () => {
    results.value = []
    clearTimeout(debounceTimer)
  }

  return { results, loading, search, clear }
}
