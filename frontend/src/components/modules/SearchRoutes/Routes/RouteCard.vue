<script setup>
import { ChevronRight, MapPinIcon, Zap, Star, Layers, Train } from 'lucide-vue-next'
import { computed, ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  train: {
    type: Object,
    required: true
  }
})

// Маппинг классов поездов
const classLabels = {
  BrandedTrain: { label: 'Фирменный', icon: 'star', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  HighSpeedTrain: { label: 'Скоростной', icon: 'zap', color: 'text-sky-400', bg: 'bg-sky-500/10', border: 'border-sky-500/20' },
  LegacyBrandedTrain: { label: 'Фирменный', icon: 'star', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  LegacyHighSpeedTrain: { label: 'Скоростной', icon: 'zap', color: 'text-sky-400', bg: 'bg-sky-500/10', border: 'border-sky-500/20' },
  LegacyTwoStoreyTrain: { label: 'Двухэтажный', icon: 'layers', color: 'text-violet-400', bg: 'bg-violet-500/10', border: 'border-violet-500/20' }
}

// ===== ОПРЕДЕЛЕНИЕ ТИПА ТРАНСПОРТА =====
const isElektrichka = computed(() => {
  const type = (props.train.type || '').toLowerCase().trim()
  
  if (!type) return true
  if (type.includes('пригородный')) return true
  
  return false
})

// Лейбл типа транспорта
const transportLabel = computed(() => {
  return isElektrichka.value ? 'Электричка' : 'Поезд'
})

// Имя поезда (если есть)
const trainName = computed(() => {
  return (props.train.name || '').trim()
})

// Проверка на экспресс
const isExpress = computed(() => {
  return props.train.is_express === true
})

// Уникальные классы + экспресс бейдж
const trainClasses = computed(() => {
  const classes = []
  
  if (isExpress.value) {
    classes.push({ 
      label: 'Экспресс', 
      icon: 'zap', 
      color: 'text-emerald-400', 
      bg: 'bg-emerald-500/10', 
      border: 'border-emerald-500/20' 
    })
  }
  
  if (props.train.class && Array.isArray(props.train.class)) {
    const seen = new Set(classes.map(c => c.label))
    
    props.train.class.forEach(cls => {
      const item = classLabels[cls]
      if (item && !seen.has(item.label)) {
        seen.add(item.label)
        classes.push(item)
      }
    })
  }
  
  return classes
})

// Парсинг времени
const departure = computed(() => new Date(props.train.ts_dep))
const arrival = computed(() => new Date(props.train.ts_arr))

// Форматирование
const formatTime = (date) => {
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

const formatDate = (date) => {
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

// Длительность
const durationText = computed(() => {
  const diff = arrival.value - departure.value
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours === 0) return `${minutes} мин`
  if (minutes === 0) return `${hours} ч`
  return `${hours} ч ${minutes} мин`
})

// ✅ Реактивное текущее время
const currentTime = ref(new Date())

// Процент выполнения пути (реальный)
const progressPercent = computed(() => {
  const now = currentTime.value.getTime()
  const start = departure.value.getTime()
  const end = arrival.value.getTime()
  const total = end - start
  const current = now - start

  if (current <= 0) return 0
  if (current >= total) return 100
  return (current / total) * 100
})

// Для плавной анимации - начинаем с 0
const displayProgress = ref(0)
let updateInterval = null

onMounted(() => {
  // Двойной requestAnimationFrame для гарантированного срабатывания transition
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      displayProgress.value = progressPercent.value
    })
  })
  
  // ✅ Обновление каждую минуту (60000 мс)
  updateInterval = setInterval(() => {
    currentTime.value = new Date()
    displayProgress.value = progressPercent.value
  }, 20000) // 1 минута
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})

// ✅ Статус с отображением оставшегося времени
const status = computed(() => {
  const now = currentTime.value
  const dep = departure.value
  const arr = arrival.value
  
  // Ушёл
  if (now > arr) {
    return { 
      text: 'Прибыл', 
      color: 'text-zinc-400', 
      bg: 'bg-zinc-800', 
      dot: 'bg-zinc-500' 
    }
  }
  
  // В пути - показываем сколько осталось до прибытия
  if (now > dep) {
    const minToArr = Math.ceil((arr - now) / (1000 * 60))
    const hours = Math.floor(minToArr / 60)
    const mins = minToArr % 60
    
    let timeLeft = ''
    if (hours > 0 && mins > 0) {
      timeLeft = `${hours}ч ${mins}м`
    } else if (hours > 0) {
      timeLeft = `${hours}ч`
    } else {
      timeLeft = `${mins}м`
    }
    
    return { 
      text: `В пути (ещё ${timeLeft})`, 
      color: 'text-green-400', 
      bg: 'bg-green-500/10', 
      dot: 'animate-pulse bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' 
    }
  }
  
  const minToDep = Math.ceil((dep - now) / (1000 * 60))
  
  // Посадка (< 5 мин) - показываем минуты
  if (minToDep <= 5) {
    return { 
      text: minToDep <= 1 ? 'Отправляется' : `Посадка • ${minToDep} мин`, 
      color: 'text-red-400', 
      bg: 'bg-red-500/10', 
      dot: 'animate-pulse bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' 
    }
  }
  
  // Прибывает (5-25 мин) - показываем минуты
  if (minToDep <= 25) {
    return { 
      text: `Через ${minToDep} мин`, 
      color: 'text-amber-400', 
      bg: 'bg-amber-500/10', 
      dot: 'bg-amber-500' 
    }
  }
  
  // Больше 25 минут
  return { 
    text: 'По расписанию', 
    color: 'text-zinc-300', 
    bg: 'bg-zinc-700/50', 
    dot: 'bg-zinc-500' 
  }
})

const isDifferentDay = computed(() => {
  return departure.value.toDateString() !== arrival.value.toDateString()
})
</script>

<template>
  <article
    class="group relative w-full bg-[#18181B] hover:bg-[#202024] 
           rounded-2xl border border-white/5 hover:border-white/10 
           p-5 cursor-pointer transition-all duration-300 
           shadow-lg shadow-black/20 active:scale-[0.99]"
  >
    <!-- Верхняя часть: Тип, Номер, Имя и Статус -->
    <div class="flex items-start justify-between mb-6">
      <!-- ЛЕВАЯ ЧАСТЬ -->
      <div class="flex flex-col min-w-0 flex-1 mr-3">
        <!-- Тип транспорта (Поезд / Электричка) -->
        <div class="flex items-center gap-1.5 mb-0.5">
          <span 
          :class="isElektrichka ? 'text-white/40' : 'text-white/50'"  
          class="text-xs font-bold uppercase tracking-wider">
            {{ transportLabel }}
          </span>
        </div>
        
        <!-- Номер и бейджи -->
        <div class="flex items-center gap-3 flex-wrap">
          <span class="text-3xl font-black text-white tracking-tight leading-none">
            {{ train.number }}
          </span>
          
          <!-- Бейджи классов поезда -->
          <div v-if="trainClasses.length" class="flex items-center gap-1.5 flex-wrap">
            <span 
              v-for="(cls, idx) in trainClasses" 
              :key="idx"
              class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wide border"
              :class="[cls.bg, cls.color, cls.border]"
            >
              <Zap v-if="cls.icon === 'zap'" :size="10" :stroke-width="2.5" />
              <Star v-else-if="cls.icon === 'star'" :size="10" :stroke-width="2.5" />
              <Layers v-else-if="cls.icon === 'layers'" :size="10" :stroke-width="2.5" />
              {{ cls.label }}
            </span>
          </div>
        </div>

        <!-- Имя поезда (если есть) -->
        <span 
          v-if="trainName" 
          class="mt-1.5 text-sm font-medium text-amber-500 truncate"
          :title="trainName"
        >
          «{{ trainName }}»
        </span>
      </div>

      <!-- Статус бейдж -->
      <div 
        class="px-3 py-1.5 rounded-lg text-xs font-medium border border-transparent transition-colors flex items-center gap-2 shrink-0"
        :class="[status.bg, status.color]"
      >
        <span class="-ml-1 w-1.5 h-1.5 rounded-full" :class="status.dot"></span>
        {{ status.text }}
      </div>
    </div>

    <!-- Средняя часть: Временная шкала -->
    <div class="flex items-end justify-between gap-4 relative z-10">
      <div class="flex flex-col">
        <span class="text-2xl font-bold text-white tabular-nums leading-none mb-1">
          {{ formatTime(departure) }}
        </span>
        <span class="text-sm font-medium text-white/40">
          {{ formatDate(departure) }}
        </span>
      </div>

      <div class="flex-1 flex flex-col items-center pb-1.5 px-2 min-w-20">
        <div class="text-xs font-medium text-white/30 mb-2">
          {{ durationText }}
        </div>
        
        <!-- ✅ Прогресс-бар с плавной анимацией -->
        <div class="w-full h-1 bg-white/10 rounded-full relative overflow-hidden">
          <div 
            class="absolute left-0 top-0 h-full rounded-full bg-linear-to-r from-lime-300 to-emerald-400 
                   shadow-[0_0_8px_rgba(16,185,129,0.5)] transition-all duration-1000 ease-out"
            :style="{ width: `${displayProgress}%` }"
          ></div>
        </div>

        <div class="w-full flex justify-between -mt-1.5 px-px">
          <div class="relative w-2 h-2 right-0.5 rounded-full bg-[#27272a] border-2"
          :class="displayProgress > 0 
              ? 'border-lime-300 shadow-[0_0_6px_rgb(187,244,81,0.5)]'
              : 'border-white/20'"></div>
          <div 
            class="relative w-2 h-2 left-0.5 rounded-full bg-[#27272a] border-2 transition-colors duration-500"
            :class="displayProgress >= 100 
              ? 'border-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.5)]'
              : 'border-white/20'"
          ></div>
        </div>
      </div>

      <div class="flex flex-col items-end text-right">
        <span class="text-2xl font-bold text-white tabular-nums leading-none mb-1">
          {{ formatTime(arrival) }}
        </span>
        <span class="text-sm font-medium text-white/40">
          {{ formatDate(arrival) }}
          <span v-if="isDifferentDay" class="text-amber-500 ml-0.5 font-bold text-xs sup">+1</span>
        </span>
      </div>
    </div>

    <!-- Нижняя часть: Маршрут -->
    <div class="mt-6 pt-4 border-t border-white/5 flex items-center justify-between">
      <div class="flex items-center gap-2 text-sm text-white/60 truncate pr-4">
        <MapPinIcon :size="18" :stroke-width="2" class="text-white/20 shrink-0"/>
        <span class="truncate group-hover:text-white/80 transition-colors">{{ train.route }}</span>
      </div>

      <div class="w-8 h-8 rounded-full flex items-center justify-center bg-white/0
        group-hover:text-white transition-all text-white/10 duration-500 shrink-0 -mr-2">
        <ChevronRight />
      </div>
    </div>
  </article>
</template>