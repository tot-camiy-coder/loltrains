// @/scripts/rzd_api.js
import { ref } from 'vue'

const API_BASE = '/api'

// --- НОВАЯ ФУНКЦИЯ: Прямой поиск без реактивности (для резолвинга из URL) ---
export async function findStation(query) {
  if (!query || query.length < 2) return []
  try {
    const res = await fetch(`${API_BASE}/stations?part=${encodeURIComponent(query)}`)
    const data = await res.json()
    return data.stations || []
  } catch (e) {
    console.error('Station resolve error:', e)
    return []
  }
}

// Хук для поиска станций (для автокомплита в UI)
export function useStationSearch() {
  const suggestions = ref([])
  const isLoading = ref(false)
  let debounceTimer = null

  const search = async (query) => {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(async () => {
      isLoading.value = true
      const results = await findStation(query) // Используем общую функцию
      suggestions.value = results
      isLoading.value = false
    }, 1)
  }

  return { suggestions, search, isLoading }
}

// Хук для получения маршрутов (без изменений, но код нужен полный)
export function useRoutes() {
  const routes = ref([])
  const info = ref({})
  const isLoading = ref(false)
  const error = ref(null)

  const fetchRoutes = async (codeFrom, codeTo) => {
    if (!codeFrom || !codeTo) return

    isLoading.value = true
    error.value = null

    try {
      const res = await fetch(
        `${API_BASE}/routes?code_from=${codeFrom}&code_to=${codeTo}`
      )
      const data = await res.json()
      
      routes.value = data.trains || []
      info.value = data.info || {}
    } catch (e) {
      console.error('Routes fetch error:', e)
      error.value = e.message
      routes.value = []
    } finally {
      isLoading.value = false
    }
  }

  return { routes, info, fetchRoutes, isLoading, error }
}

// Хук для получения остановок поезда (без изменений)
export function useTrainStops() {
  const stops = ref([])
  const trainNumber = ref('')
  const isLoading = ref(false)

  const fetchStops = async (train, codeFrom, codeTo) => {
    if (!train || !codeFrom || !codeTo) return

    isLoading.value = true
    try {
      const res = await fetch(
        `${API_BASE}/station_list?train_num=${encodeURIComponent(train)}&code_from=${codeFrom}&code_to=${codeTo}`
      )
      const data = await res.json()
      
      stops.value = data.stops || []
      trainNumber.value = data.train || train
    } catch (e) {
      console.error('Stops fetch error:', e)
      stops.value = []
    } finally {
      isLoading.value = false
    }
  }

  return { stops, trainNumber, fetchStops, isLoading }
}