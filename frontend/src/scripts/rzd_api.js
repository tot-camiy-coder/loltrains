import { ref } from 'vue'
import axios from 'axios'

const cache = new Map()

export function useStationSearch() {
  const suggestions = ref([])
  
  let timer = null
  let controller = null
  let lastTerm = ''

  const search = (term) => {
    if (term === lastTerm) return
    lastTerm = term

    clearTimeout(timer)

    if (!term || term.length < 2) {
        suggestions.value = []
        return
    }

    if (cache.has(term)) {
        suggestions.value = cache.get(term)
        console.log(`Cache Response: ${term}`)
        return
    }

    if (controller) {
        controller.abort()
    }

    timer = setTimeout(async () => {
      try {
        controller = new AbortController()
        console.log(`API Response: ${term}`)
        
        const { data } = await axios.get(`/api/stations?part=${term}`, {
          signal: controller.signal
        })
        
        const stations = data.stations || []
        
        cache.set(term, stations)
        suggestions.value = stations

      } catch (e) {
        if (!axios.isCancel(e)) {
          suggestions.value = []
        }
      } finally {
        controller = null
      }
    }, 300)
  }

  const clearSuggestions = () => {
    suggestions.value = []
    lastTerm = ''
    if (controller) controller.abort()
  }

  return {
    suggestions,
    search,
    clearSuggestions
  }
}