<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStationSearch, useRoutes, findStation } from '@/scripts/rzd_api'
import SearchHeader from '@/components/modules/SearchRoutes/Routes/SearchHeader.vue'
import RoutesList from '@/components/modules/SearchRoutes/Routes/RoutesList.vue'

// ============ Константы ============
const FROM_INDEX = 0
const TO_INDEX = 1

// ============ Роутер ============
const router = useRouter()
const route = useRoute()

// ============ API Composables ============
const { 
  suggestions, 
  search: searchStations, 
  isLoading: isStationsLoading // Это загрузка только для автокомплита (выпадающего списка)
} = useStationSearch()

const { 
  routes, 
  info, 
  fetchRoutes, 
  isLoading: isRoutesLoading 
} = useRoutes()

// ============ Состояние ============
const form = ref([
  { name: '', code: null, label: 'Откуда' },
  { name: '', code: null, label: 'Куда' }
])

const activeInputIndex = ref(null)
const autocompleteItems = ref([])

// Новая переменная для отслеживания загрузки данных из URL
const isResolvingUrl = ref(false)

// ============ Computed ============
const hasSearched = computed(() => 
  Boolean(route.query.from && route.query.to)
)

const isFormValid = computed(() => 
  form.value.every(field => field.code !== null)
)

// ИЗМЕНЕНИЕ: Убрали isStationsLoading из общей загрузки страницы.
// Теперь страница блокируется только при поиске маршрутов или разборе URL.
const isLoading = computed(() => 
  isRoutesLoading.value || isResolvingUrl.value
)

// ============ Резолвинг станции ============
const resolveStationCode = async (name) => {
  try {
    const stations = await findStation(name)
    
    if (stations.length > 0) {
      return stations[0].code
    }
  } catch (error) {
    console.error(`Ошибка поиска станции "${name}":`, error)
  }

  return null
}

// ============ Обработка URL ============
const syncFormWithURL = async (query) => {
  const { from, to } = query
  if (!from || !to) return

  // Заполняем имена
  form.value[FROM_INDEX].name = from
  form.value[TO_INDEX].name = to

  isResolvingUrl.value = true

  try {
    const [codeFrom, codeTo] = await Promise.all([
      resolveStationCode(from),
      resolveStationCode(to)
    ])

    form.value[FROM_INDEX].code = codeFrom
    form.value[TO_INDEX].code = codeTo

    // Загружаем маршруты
    if (codeFrom && codeTo) {
      await fetchRoutes(codeFrom, codeTo)
    }
  } catch (error) {
    console.error('Ошибка синхронизации с URL:', error)
  } finally {
    // ИЗМЕНЕНИЕ: Сбрасываем свою переменную
    isResolvingUrl.value = false
  }
}

// ============ Watchers ============
watch(() => route.query, syncFormWithURL, { immediate: true })

watch(suggestions, (newSuggestions) => {
  if (!newSuggestions?.length) return

  // Обновляем автокомплит
  if (activeInputIndex.value !== null) {
    autocompleteItems.value = newSuggestions
  }
})

// ============ Обработчики событий ============
function handleSearch(query, index) {
  activeInputIndex.value = index
  form.value[index].code = null

  const trimmedQuery = query.trim()
  
  if (!trimmedQuery) {
    autocompleteItems.value = []
    return
  }

  autocompleteItems.value = []
  searchStations(trimmedQuery.toLowerCase())
}

function handleSelect(station, index) {
  // Обновляем форму
  form.value[index].name = station.station
  form.value[index].code = station.code

  // Сбрасываем автокомплит
  autocompleteItems.value = []
  activeInputIndex.value = null
}

function handleSwap() {
  const fromData = { ...form.value[FROM_INDEX] }
  const toData = { ...form.value[TO_INDEX] }

  form.value[FROM_INDEX] = { ...toData, label: 'Откуда' }
  form.value[TO_INDEX] = { ...fromData, label: 'Куда' }

  // Автопоиск после swap
  if (hasSearched.value && isFormValid.value) {
    performSearch()
  }
}

function performSearch() {
  if (!isFormValid.value) return

  router.push({
    query: {
      from: form.value[FROM_INDEX].name,
      to: form.value[TO_INDEX].name
    }
  })
}

function handleRouteSelect(train) {
  router.push({
    path: '/route',
    query: {
      train: train.number,
      from: route.query.from,
      to: route.query.to
    }
  })
}
</script>

<template>
  <div class="min-h-screen flex flex-col pb-60 md:pb-20">
    <!-- До поиска: всё по центру -->
    <div
      v-if="!hasSearched"
      class="flex-1 flex flex-col items-center justify-center px-4"
    >
      <!-- Заголовок -->
      <div class="text-center mb-6 md:mb-8">
        <h1 class="text-2xl md:text-4xl font-bold text-white tracking-tight">
          Куда отправимся сегодня?
        </h1>
        <p class="mt-2 text-sm md:text-base text-white/60">
          Найдите лучшие маршруты, расписание и актуальные рейсы
        </p>
      </div>

      <!-- Шапка с поиском (центрированная) -->
      <div class="w-full max-w-4xl">
        <SearchHeader
          v-model:form="form"
          :active-input-index="activeInputIndex"
          :current-items="autocompleteItems"
          :is-loading="isStationsLoading"
          :is-search-valid="isFormValid"
          :is-compact="false"
          @search="handleSearch"
          @select="handleSelect"
          @swap="handleSwap"
          @find="performSearch"
        />
      </div>
    </div>

    <!-- После поиска: обычный layout -->
    <template v-else>
      <!-- Компактный поиск сверху -->
      <div class="px-4">
        <SearchHeader
          v-model:form="form"
          :active-input-index="activeInputIndex"
          :current-items="autocompleteItems"
          :is-loading="isStationsLoading"
          :is-search-valid="isFormValid"
          :is-compact="true"
          @search="handleSearch"
          @select="handleSelect"
          @swap="handleSwap"
          @find="performSearch"
        />
      </div>

      <!-- Основной контент -->
      <main class="flex-1 pt-4 px-4">
        <!-- Загрузка -->
        <div
          v-if="isLoading"
          class="flex justify-center items-center pt-10"
        >
          <span class="text-gray-600">Загрузка...</span>
        </div>

        <!-- Результаты -->
        <RoutesList
          v-else
          :routes="routes"
          :info="info"
          :is-loading="isRoutesLoading"
          @select="handleRouteSelect"
        />
      </main>
    </template>
  </div>
</template>