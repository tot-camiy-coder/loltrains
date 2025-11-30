<script setup>
import { computed } from 'vue'

const props = defineProps({
  train: {
    type: Object,
    required: true
  }
})

// Парсинг времени
const departure = computed(() => new Date(props.train.ts_dep))
const arrival = computed(() => new Date(props.train.ts_arr))

// Форматирование времени
const formatTime = (date) => {
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

const formatDate = (date) => {
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

// Длительность поездки
const duration = computed(() => {
  const diff = arrival.value - departure.value
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  return `${hours}ч ${minutes}м`
})

// Статус поезда
const status = computed(() => {
  const now = new Date()
  const dep = departure.value
  const arr = arrival.value
  
  if (now > arr) return { text: 'Прибыл', color: 'text-gray-400', bg: 'bg-gray-500/20' }
  if (now > dep) return { text: 'В пути', color: 'text-blue-400', bg: 'bg-blue-500/20' }
  
  const minToDep = (dep - now) / (1000 * 60)
  if (minToDep <= 5) return { text: 'Посадка', color: 'text-green-400', bg: 'bg-green-500/20' }
  if (minToDep <= 25) return { text: 'Прибывает', color: 'text-yellow-400', bg: 'bg-yellow-500/20' }
  
  return { text: 'По расписанию', color: 'text-white/60', bg: 'bg-white/10' }
})

// Разные даты отправления и прибытия
const isDifferentDay = computed(() => {
  return departure.value.toDateString() !== arrival.value.toDateString()
})
</script>

<template>
  <article
    class="group relative p-4 bg-[#18181B] rounded-xl border border-white/10 
           hover:border-white/20 hover:bg-[#1f1f23] cursor-pointer
           transition-all duration-200 active:scale-[0.99]"
  >
    <!-- Express badge -->
    <div 
      v-if="train.is_express"
      class="absolute -top-2 -right-2 px-2 py-0.5 text-xs font-bold 
             bg-linear-to-r from-amber-500 to-orange-500 rounded-full text-white shadow-lg"
    >
      EXPRESS
    </div>

    <div class="flex items-center gap-4">
      <!-- Номер поезда -->
      <div class="shrink-0 w-16 text-center">
        <div class="text-lg font-bold text-white">{{ train.number }}</div>
        <div 
          :class="['text-xs px-2 py-0.5 rounded-full mt-1', status.bg, status.color]"
        >
          {{ status.text }}
        </div>
      </div>

      <!-- Временная шкала -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center justify-between gap-4">
          <!-- Отправление -->
          <div class="text-left">
            <div class="text-xl font-bold text-white">{{ formatTime(departure) }}</div>
            <div class="text-xs text-white/50">{{ formatDate(departure) }}</div>
          </div>

          <!-- Линия с длительностью -->
          <div class="flex-1 flex items-center gap-2 px-2">
            <div class="h-px flex-1 bg-linear-to-r from-white/30 to-transparent" />
            <div class="text-xs text-white/40 whitespace-nowrap px-2 py-1 bg-white/5 rounded-full">
              {{ duration }}
            </div>
            <div class="h-px flex-1 bg-linear-to-l from-white/30 to-transparent" />
          </div>

          <!-- Прибытие -->
          <div class="text-right">
            <div class="text-xl font-bold text-white">{{ formatTime(arrival) }}</div>
            <div class="text-xs text-white/50">
              {{ formatDate(arrival) }}
              <span v-if="isDifferentDay" class="text-amber-400">(+1)</span>
            </div>
          </div>
        </div>

        <!-- Маршрут -->
        <div class="mt-2 text-sm text-white/50 truncate">
          {{ train.route }}
        </div>
      </div>

      <!-- Стрелка -->
      <div class="shrink-0 text-white/30 group-hover:text-white/60 transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  </article>
</template>