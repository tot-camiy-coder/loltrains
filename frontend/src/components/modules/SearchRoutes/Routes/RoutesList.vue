<script setup>
import { ref, watch, nextTick, computed, onMounted, onUnmounted } from 'vue'
import RouteCard from './RouteCard.vue'
import { ArrowUp, ArrowDown, Clock } from 'lucide-vue-next'

const props = defineProps({
  routes: Array,
  info: Object,
  isLoading: Boolean
})

const emit = defineEmits(['select'])

// Текущее время (обновляется каждые 20 сек)
const now = ref(new Date())
let timer = null

// Refs для карточек
const routeCards = ref([])

// Направление скролла (true = вниз, false = вверх)
const scrollDown = ref(true)

// Элемент уже видим (кнопка не нужна)
const isTargetVisible = ref(false)

// Индекс первого актуального рейса
const firstActiveIndex = computed(() => {
  if (!props.routes?.length) return -1
  const idx = props.routes.findIndex(t => new Date(t.ts_dep) >= now.value)
  return idx
})

// Целевой индекс для скролла
const targetIndex = computed(() => {
  if (!props.routes?.length) return -1
  return firstActiveIndex.value === -1 
    ? props.routes.length - 1 
    : firstActiveIndex.value
})

// Обновление направления скролла и видимости
const updateScrollState = () => {
  if (targetIndex.value === -1) {
    isTargetVisible.value = true
    return
  }
  
  const el = routeCards.value[targetIndex.value]?.$el || routeCards.value[targetIndex.value]
  if (!el) {
    isTargetVisible.value = false
    return
  }
  
  const rect = el.getBoundingClientRect()
  const viewportHeight = window.innerHeight
  
  // Проверяем, видим ли элемент (с отступами)
  const margin = 100
  const isVisible = rect.top >= margin && rect.bottom <= viewportHeight - margin
  
  isTargetVisible.value = isVisible
  scrollDown.value = rect.top > viewportHeight / 2
}

// Показывать ли кнопку скролла
const showScrollButton = computed(() => {
  return props.routes?.length > 0 && !props.isLoading && !isTargetVisible.value
})

// Скролл к первому актуальному рейсу
const scrollToActive = async () => {
  await nextTick()
  if (targetIndex.value === -1) return
  
  const el = routeCards.value[targetIndex.value]?.$el || routeCards.value[targetIndex.value]
  el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

// Авто-скролл после загрузки данных
watch(
  () => props.isLoading,
  (loading) => {
    if (!loading && props.routes?.length) {
      scrollToActive()
      nextTick(() => updateScrollState())
    }
  }
)

// Обновлять при изменении маршрутов
watch(
  () => props.routes,
  () => nextTick(() => updateScrollState()),
  { deep: true }
)

onMounted(() => {
  timer = setInterval(() => now.value = new Date(), 20000)
  window.addEventListener('scroll', updateScrollState, { passive: true })
  window.addEventListener('resize', updateScrollState, { passive: true })
  
  // Автоскролл при загрузке страницы (если данные уже есть)
  if (props.routes?.length && !props.isLoading) {
    // Небольшая задержка для рендера карточек
    setTimeout(() => {
      scrollToActive()
      updateScrollState()
    }, 100)
  }
})

onUnmounted(() => {
  clearInterval(timer)
  window.removeEventListener('scroll', updateScrollState)
  window.removeEventListener('resize', updateScrollState)
})
</script>

<template>
  <div class="max-w-4xl mx-auto pb-20">
    <!-- Заголовок -->
    <div v-if="info?.origin" class="mb-6">
      <h2 class="text-xl md:text-2xl font-bold text-white flex items-center gap-3">
        <span class="truncate">{{ info.origin }}</span>
        <svg class="w-5 h-5 text-white/40 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
        </svg>
        <span class="truncate">{{ info.destination }}</span>
      </h2>
      <p class="text-white/50 text-sm mt-1">
        {{ isLoading ? 'Загрузка...' : `Найдено ${routes?.length || 0} рейсов` }}
      </p>
    </div>

    <!-- Скелетон -->
    <div v-if="isLoading" class="space-y-4">
      <div v-for="i in 5" :key="i" class="h-28 bg-white/5 rounded-xl animate-pulse" />
    </div>

    <!-- Пусто -->
    <div v-else-if="!routes?.length" class="text-center py-16">
      <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center">
        <svg class="w-8 h-8 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-white/70">Рейсы не найдены</h3>
      <p class="text-white/40 text-sm mt-1">Попробуйте изменить параметры поиска</p>
    </div>

    <!-- Список -->
    <div v-else class="space-y-3">
      <template v-for="(train, index) in routes" :key="train.number + train.ts_dep">
        
        <!-- Разделитель перед актуальными -->
        <div v-if="index === firstActiveIndex && firstActiveIndex > 0" 
             class="flex items-center gap-3 py-3">
          <div class="flex-1 h-px bg-white/20" />
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
            <ArrowUp :size="14" class="text-white/40" />
            <span class="text-white/50 text-xs font-medium">Ушедшие</span>
          </div>
          <div class="flex-1 h-px bg-white/20" />
        </div>
        
        <RouteCard
          :ref="el => el && (routeCards[index] = el)"
          :train="train"
          @click="$emit('select', train)"
        />
      </template>

      <!-- Все ушли -->
      <div v-if="firstActiveIndex === -1" class="flex items-center gap-3 py-4 mt-2">
        <div class="flex-1 h-px bg-amber-500/20" />
        <div class="flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/20">
          <Clock :size="14" class="text-amber-400/70" />
          <span class="text-amber-400/80 text-xs font-medium">Все рейсы ушли</span>
        </div>
        <div class="flex-1 h-px bg-amber-500/20" />
      </div>
    </div>

    <!-- Кнопка скролла -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-4"
    >
      <button
        v-if="showScrollButton"
        @click="scrollToActive"
        class="fixed bottom-6 right-6 flex items-center gap-2 
               px-2 py-2 rounded-full bg-yellow-300 hover:bg-yellow-500 
               text-black text-sm font-medium shadow-lg shadow-yellow-500/25
               transition-all active:scale-95"
      >
        <Transition
          mode="out-in"
          enter-active-class="transition duration-150"
          enter-from-class="opacity-0 rotate-180 scale-75"
          enter-to-class="opacity-100 rotate-0 scale-100"
          leave-active-class="transition duration-100"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-75"
        >
          <ArrowDown v-if="scrollDown" :size="26" :stroke-width="2" key="down" />
          <ArrowUp v-else :size="26" :stroke-width="2" key="up" />
        </Transition>
      </button>
    </Transition>
  </div>
</template>