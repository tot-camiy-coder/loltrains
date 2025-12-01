<script setup>
import { ref, watch, nextTick, computed, onMounted, onUnmounted } from 'vue'
import RouteCard from './RouteCard.vue'
import { ArrowUp } from 'lucide-vue-next'

const props = defineProps({
  routes: Array,
  info: Object,
  isLoading: Boolean
})

const emit = defineEmits(['select'])

// Реактивное текущее время (обновляется каждые 20 сек)
const now = ref(new Date())
let updateInterval = null

// Refs для карточек маршрутов
const routeCards = ref([])

const setRouteRef = (el, index) => {
  if (el) {
    routeCards.value[index] = el
  }
}

// Индекс первого актуального рейса (который ещё не ушёл)
const firstActiveIndex = computed(() => {
  if (!props.routes?.length) return -1
  
  return props.routes.findIndex(train => {
    const depTime = new Date(train.ts_dep)
    return depTime >= now.value
  })
})

// Проверка: рейс уже ушёл?
const isDeparted = (train) => {
  return new Date(train.ts_dep) < now.value
}

// Скролл к первому актуальному рейсу
const scrollToFirstActive = async () => {
  await nextTick()
  
  if (!props.routes?.length) return
  
  let targetIndex = firstActiveIndex.value
  
  // Если все рейсы прошли - скроллим к последнему
  if (targetIndex === -1) {
    targetIndex = props.routes.length - 1
  }
  
  const targetRef = routeCards.value[targetIndex]
  if (targetRef) {
    const element = targetRef.$el || targetRef
    element?.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    })
  }
}

// Обновление времени каждые 20 секунд
onMounted(() => {
  updateInterval = setInterval(() => {
    now.value = new Date()
  }, 20000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})

// Следим за окончанием загрузки
watch(
  [() => props.routes, () => props.isLoading],
  ([routes, loading]) => {
    if (!loading && routes?.length) {
      scrollToFirstActive()
    }
  },
  { immediate: true }
)
</script>

<template>
  <div class="max-w-4xl mx-auto pb-8">
    <!-- Заголовок с информацией о маршруте -->
    <div v-if="info?.origin" class="mb-6">
      <h2 class="text-xl md:text-2xl font-bold text-white flex items-center gap-3">
        <span>{{ info.origin }}</span>
        <svg class="w-5 h-5 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
        </svg>
        <span>{{ info.destination }}</span>
      </h2>
      <p class="text-white/50 text-sm mt-1">
        {{ isLoading ? 'Загрузка...' : `Найдено ${routes?.length || 0} рейсов` }}
      </p>
    </div>

    <!-- Скелетон загрузки -->
    <div v-if="isLoading" class="space-y-4">
      <div 
        v-for="i in 5" 
        :key="i"
        class="h-28 bg-white/5 rounded-xl animate-pulse"
      />
    </div>

    <!-- Пустой результат -->
    <div 
      v-else-if="!routes?.length" 
      class="text-center py-16"
    >
      <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center">
        <svg class="w-8 h-8 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-white/70">Рейсы не найдены</h3>
      <p class="text-white/40 text-sm mt-1">Попробуйте изменить параметры поиска</p>
    </div>

    <!-- Список маршрутов -->
    <div v-else class="space-y-3">
      <template v-for="(train, index) in routes" :key="train.number + train.ts_dep">
        
        <!-- Разделитель "Ушедшие" ПЕРЕД первым актуальным рейсом -->
        <div 
          v-if="index === firstActiveIndex && firstActiveIndex > 0" 
          class="flex items-center gap-3 py-3 my-2"
        >
          <div class="flex-1 h-px bg-white/30"></div>
          <div class="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10">
            <ArrowUp :size="16" class="text-neutral-500"/>
            <span class="text-white/50 text-xs font-medium uppercase tracking-wider">Ушедшие</span>
          </div>
          <div class="flex-1 h-px bg-white/30"></div>
        </div>
        
        <!-- Карточка рейса -->
        <RouteCard
          :ref="el => setRouteRef(el, index)"
          :train="train"
          @click="$emit('select', train)"
        />
      </template>

      <!-- Если ВСЕ рейсы ушли - показываем разделитель в конце -->
      <div 
        v-if="firstActiveIndex === -1" 
        class="flex items-center gap-3 py-4 mt-4"
      >
        <div class="flex-1 h-px bg-linear-to-r from-transparent via-amber-500/30 to-transparent"></div>
        <div class="flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/20">
          <svg class="w-4 h-4 text-amber-400/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-amber-400/80 text-xs font-medium">Все рейсы на сегодня уже ушли</span>
        </div>
        <div class="flex-1 h-px bg-linear-to-r from-transparent via-amber-500/30 to-transparent"></div>
      </div>
    </div>
  </div>
</template>