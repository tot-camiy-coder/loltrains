<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { MapPinIcon, ChevronRight, Zap, Star, Layers, Train as TrainIcon } from 'lucide-vue-next'

// Можно переиспользовать из @/scripts/rzd_api.js при желании
// import { findStation } from '@/scripts/rzd_api.js'

// Параметры из URL
const route = useRoute()
const trainParam = computed(() => String(route.query.train || '').trim())
const fromParam = computed(() => String(route.query.from || '').trim())
const toParam = computed(() => String(route.query.to || '').trim())

// Состояния
const loading = ref(false)
const error = ref(null)
const stops = ref([])
const trainNumber = ref('')
const trainInfo = ref(null) // из /routes (если удалось найти)
const originName = ref('')
const destinationName = ref('')

const currentTime = ref(new Date())
let tick = null

// Вспомогательные утилиты
const parseDT = (s) => {
  if (!s || s === 'Н/Д') return null
  const d = new Date(s)
  return isNaN(d.getTime()) ? null : d
}
const formatTime = (d) => d ? d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) : '—'
const formatDate = (d) => d ? d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }) : ''

const plural = (n, one, few, many) => {
  const abs = Math.abs(n) % 100
  const n1 = abs % 10
  if (abs > 10 && abs < 20) return many
  if (n1 > 1 && n1 < 5) return few
  if (n1 === 1) return one
  return many
}

// Загрузка данных
const fetchStops = async () => {
  if (!trainParam.value || !fromParam.value || !toParam.value) {
    error.value = 'Нужно указать train, from и to'
    return
  }
  error.value = null
  loading.value = true
  try {
    // Берем остановки напрямую (бэкенд сам резолвит имена и подбирает provider/service)
    const res = await fetch(
      `/api/station_list?train_num=${encodeURIComponent(trainParam.value)}&str_from=${encodeURIComponent(fromParam.value)}&str_to=${encodeURIComponent(toParam.value)}`
    )
    const data = await res.json()
    stops.value = Array.isArray(data?.stops) ? data.stops : []
    trainNumber.value = data?.train || trainParam.value

    // Назначим начало/конец по всему маршруту для заголовка
    if (stops.value.length) {
      originName.value = stops.value[0]?.name || ''
      destinationName.value = stops.value[stops.value.length - 1]?.name || ''
    } else {
      originName.value = ''
      destinationName.value = ''
    }

    // Параллельно — попробуем достать /routes, чтобы получить route, type, class и т.п.
    // Для этого нужно коды станций from/to. Бэкенд их найдёт, но тут нам придётся дернуть /stations.
    // Чтобы не усложнять — поищем коды через /stations и возьмём первый релевантный результат.
    const [fromRes, toRes] = await Promise.all([
      fetch(`/api/stations?part=${encodeURIComponent(fromParam.value)}`),
      fetch(`/api/stations?part=${encodeURIComponent(toParam.value)}`)
    ])
    const fromData = await fromRes.json()
    const toData = await toRes.json()
    const codeFrom = fromData?.stations?.[0]?.code
    const codeTo = toData?.stations?.[0]?.code

    if (codeFrom && codeTo) {
      const r = await fetch(`/api/routes?code_from=${codeFrom}&code_to=${codeTo}`)
      const rdata = await r.json()
      const found = (rdata?.trains || []).find(t => t.number === trainNumber.value)
      if (found) {
        trainInfo.value = found
      } else {
        trainInfo.value = null
      }
    }
  } catch (e) {
    console.error(e)
    error.value = 'Ошибка загрузки данных'
    stops.value = []
    trainInfo.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStops()
  tick = setInterval(() => {
    currentTime.value = new Date()
  }, 20000)
})
onUnmounted(() => {
  if (tick) clearInterval(tick)
})
watch(() => route.fullPath, fetchStops)

// Вычисления по маршруту
const isElektrichka = computed(() => {
  const type = (trainInfo.value?.type || '').toLowerCase().trim()
  if (!type) return true
  if (type.includes('пригородный')) return true
  return false
})

const originStop = computed(() => {
  const targets = stops.value.filter(s => s.is_target)
  if (!targets.length) return null
  return targets[0] // первая отмеченная станция в списке — отправление в нашем сегменте
})
const destinationStop = computed(() => {
  const targets = stops.value.filter(s => s.is_target)
  if (!targets.length) return null
  return targets[targets.length - 1] // последняя — прибытие в нашем сегменте
})

// Общее время по нашему сегменту — приоритет trainInfo, иначе из target-остановок
const routeDeparture = computed(() => {
  return parseDT(trainInfo.value?.ts_dep) || parseDT(originStop.value?.ts_dep) || parseDT(originStop.value?.ts_arr)
})
const routeArrival = computed(() => {
  return parseDT(trainInfo.value?.ts_arr) || parseDT(destinationStop.value?.ts_arr) || parseDT(destinationStop.value?.ts_dep)
})

const durationText = computed(() => {
  const dep = routeDeparture.value
  const arr = routeArrival.value
  if (!dep || !arr) return ''
  const diff = arr - dep
  const h = Math.floor(diff / 3600000)
  const m = Math.floor((diff % 3600000) / 60000)
  if (h === 0) return `${m} ${plural(m, 'мин', 'мин', 'мин')}`
  if (m === 0) return `${h} ${plural(h, 'ч', 'ч', 'ч')}`
  return `${h} ч ${m} мин`
})

const progressPercent = computed(() => {
  const dep = routeDeparture.value
  const arr = routeArrival.value
  if (!dep || !arr) return 0
  const total = arr - dep
  const curr = currentTime.value - dep
  if (curr <= 0) return 0
  if (curr >= total) return 100
  return (curr / total) * 100
})

// Статус поездки
const status = computed(() => {
  const now = currentTime.value
  const dep = routeDeparture.value
  const arr = routeArrival.value
  if (!dep || !arr) {
    return {
      text: 'Статус неизвестен',
      color: 'text-zinc-300',
      bg: 'bg-zinc-700/50',
      dot: 'bg-zinc-500'
    }
  }

  if (now > arr) {
    return {
      text: 'Ушёл',
      color: 'text-zinc-400',
      bg: 'bg-zinc-800',
      dot: 'bg-zinc-500'
    }
  }

  if (now > dep) {
    const minToArr = Math.ceil((arr - now) / 60000)
    const hours = Math.floor(minToArr / 60)
    const mins = minToArr % 60
    let timeLeft = ''
    if (hours > 0 && mins > 0) timeLeft = `${hours}ч ${mins}м`
    else if (hours > 0) timeLeft = `${hours}ч`
    else timeLeft = `${mins}м`
    return {
      text: `В пути (ещё ${timeLeft})`,
      color: 'text-green-400',
      bg: 'bg-green-500/10',
      dot: 'animate-pulse bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]'
    }
  }

  const minToDep = Math.ceil((dep - now) / 60000)
  if (minToDep <= 5) {
    return {
      text: minToDep <= 1 ? 'Отправляется' : `Посадка • ${minToDep} мин`,
      color: 'text-red-400',
      bg: 'bg-red-500/10',
      dot: 'animate-pulse bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]'
    }
  }
  if (minToDep <= 25) {
    return {
      text: `Через ${minToDep} мин`,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
      dot: 'bg-amber-500'
    }
  }
  return {
    text: 'По расписанию',
    color: 'text-zinc-300',
    bg: 'bg-zinc-700/50',
    dot: 'bg-zinc-500'
  }
})

// Вычисляем текущую/следующую остановку
const stopTime = (s) => parseDT(s?.ts_dep) || parseDT(s?.ts_arr) || null

const nextStopIndex = computed(() => {
  const now = currentTime.value
  for (let i = 0; i < stops.value.length; i++) {
    const t = stopTime(stops.value[i])
    if (t && t >= now) return i
  }
  return stops.value.length - 1
})
const currentStopIndex = computed(() => {
  const n = nextStopIndex.value
  return n <= 0 ? 0 : n - 1
})
const nextStop = computed(() => stops.value[nextStopIndex.value] || null)
const currentStop = computed(() => stops.value[currentStopIndex.value] || null)

// Автоскролл
const listRef = ref(null)
const scrollToActive = async () => {
  await nextTick()
  const idx = nextStopIndex.value || 0
  const el = document.querySelector(`[data-stop-index="${idx}"]`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}
watch([stops, nextStopIndex], () => {
  // Автоскролл при загрузке/смене актуальной станции
  scrollToActive()
})

// Таймлайн с точками остановок
const timelinePositions = computed(() => {
  const dep = routeDeparture.value
  const arr = routeArrival.value
  const total = dep && arr ? (arr - dep) : null

  const n = stops.value.length
  if (!n) return []

  return stops.value.map((s, i) => {
    const t = stopTime(s)
    let percent
    if (t && dep && total) {
      percent = Math.min(100, Math.max(0, ((t - dep) / total) * 100))
    } else {
      // Фоллбэк — равномерно
      percent = n === 1 ? 0 : (i / (n - 1)) * 100
    }
    const state = i < nextStopIndex.value ? 'past' : (i === nextStopIndex.value ? 'next' : 'future')
    return { i, name: s.name, is_target: !!s.is_target, percent, state }
  })
})
const displayProgress = ref(0)
watch(progressPercent, (v) => {
  // плавная анимация полосы
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      displayProgress.value = v
    })
  })
})
onMounted(() => {
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      displayProgress.value = progressPercent.value
    })
  })
})

// Классы поездов (для бейджей)
const classLabels = {
  BrandedTrain: { label: 'Фирменный', icon: 'star', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  HighSpeedTrain: { label: 'Скоростной', icon: 'zap', color: 'text-sky-400', bg: 'bg-sky-500/10', border: 'border-sky-500/20' },
  LegacyBrandedTrain: { label: 'Фирменный', icon: 'star', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  LegacyHighSpeedTrain: { label: 'Скоростной', icon: 'zap', color: 'text-sky-400', bg: 'bg-sky-500/10', border: 'border-sky-500/20' },
  LegacyTwoStoreyTrain: { label: 'Двухэтажный', icon: 'layers', color: 'text-violet-400', bg: 'bg-violet-500/10', border: 'border-violet-500/20' }
}
const isExpress = computed(() => trainInfo.value?.is_express === true)
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
  const arr = trainInfo.value?.class
  if (arr && Array.isArray(arr)) {
    const seen = new Set(classes.map(c => c.label))
    arr.forEach(cls => {
      const it = classLabels[cls]
      if (it && !seen.has(it.label)) {
        seen.add(it.label)
        classes.push(it)
      }
    })
  }
  return classes
})
</script>

<template>
    
<!-- Хедер: закреплённый статус + таймлайн -->
<header class="sticky top-0 px-2 sm:px-20 z-30 backdrop-blur-md w-full pt-4 pb-3">
      <div class="flex items-start justify-between mb-3">
        <!-- Левая часть -->
        <div class="flex flex-col min-w-0 flex-1 mr-3">
          <div class="flex items-center gap-1.5">
            <span :class="isElektrichka ? 'text-white/40' : 'text-white/50'" class="text-xs font-bold uppercase tracking-wider">
              {{ isElektrichka ? 'Электричка' : 'Поезд' }}
            </span>
          </div>

          <div class="flex items-center gap-3 flex-wrap mt-1">
            <span class="text-3xl font-black text-white tracking-tight leading-none">
              {{ trainNumber || trainParam }}
            </span>

            <!-- Бейджи классов -->
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
          <span v-if="(trainInfo?.name || '').trim()" class="mt-1.5 text-sm font-medium text-amber-500 truncate">
            «{{ (trainInfo?.name || '').trim() }}»
          </span>
        </div>

        <!-- Статус -->
        <div
          class="px-3 py-1.5 rounded-lg text-xs font-medium border border-transparent transition-colors flex items-center gap-2 shrink-0"
          :class="[status.bg, status.color]"
        >
          <span class="-ml-1 w-1.5 h-1.5 rounded-full" :class="status.dot"></span>
          {{ status.text }}
        </div>
      </div>

      <!-- Тайминги -->
      <div class="flex items-end justify-between gap-4">
        <div class="flex flex-col">
          <span class="text-2xl font-bold text-white tabular-nums leading-none mb-1">
            {{ formatTime(routeDeparture) }}
          </span>
          <span class="text-sm font-medium text-white/40">
            {{ formatDate(routeDeparture) }}
          </span>
        </div>

        <div class="flex-1 flex flex-col items-center pb-1.5 px-2 min-w-20">
          <div class="text-xs font-medium text-white/30 mb-2">
            {{ durationText }}
          </div>

          <!-- Прогресс-бар -->
          <div class="w-full h-1 bg-white/10 rounded-full relative overflow-hidden">
            <div
              class="absolute left-0 top-0 h-full rounded-full bg-linear-to-r from-lime-300 to-emerald-400
                     shadow-[0_0_8px_rgba(16,185,129,0.5)] transition-all duration-1000 ease-out"
              :style="{ width: `${displayProgress}%` }"
            ></div>
          </div>

          <!-- Точки остановок поверх прогресса -->
          <div class="relative w-full h-5 mt-2">
            <template v-for="p in timelinePositions" :key="p.i">
              <div
                class="absolute -translate-x-1/2 top-1/2 -translate-y-1/2"
                :style="{ left: `${p.percent}%` }"
              >
                <div
                  class="w-2.5 h-2.5 rounded-full border-2"
                  :class="[
                    p.state === 'past' ? 'bg-emerald-400 border-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.6)]' : '',
                    p.state === 'next' ? 'bg-amber-400 border-amber-400 animate-pulse shadow-[0_0_6px_rgba(245,158,11,0.6)]' : '',
                    p.state === 'future' ? 'bg-white/10 border-white/20' : '',
                    p.is_target ? 'ring-2 ring-white/40' : ''
                  ]"
                  :title="p.name"
                ></div>
              </div>
            </template>
          </div>
        </div>

        <div class="flex flex-col items-end text-right">
          <span class="text-2xl font-bold text-white tabular-nums leading-none mb-1">
            {{ formatTime(routeArrival) }}
          </span>
          <span class="text-sm font-medium text-white/40">
            {{ formatDate(routeArrival) }}
          </span>
        </div>
      </div>

      <!-- Маршрут сверху -->
      <div class="mt-4 flex items-center justify-between">
        <div class="flex items-center gap-2 text-sm text-white/60 truncate pr-4">
          <MapPinIcon :size="18" :stroke-width="2" class="text-white/20 shrink-0"/>
          <span class="truncate">
            {{ trainInfo?.route || (originName && destinationName ? `${originName} - ${destinationName}` : 'Маршрут') }}
          </span>
        </div>
      </div>
    </header>

  <!-- Прозрачный контейнер -->
  <div class="container mx-auto sm:px-64 bg-transparent ">
    <!-- Содержание -->
    <section class="mt-2">
      <!-- Скелетоны/ошибки -->
      <div v-if="loading" class="text-white/60 text-sm py-8">
        Загружаем остановки…
      </div>
      <div v-else-if="error" class="text-red-400 text-sm py-8">
        {{ error }}
      </div>

      <!-- Следующая остановка -->
      <div v-else class="mb-4">
        <div v-if="nextStop" class="flex items-center gap-2 text-white/80 text-sm">
          <span class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
            Следующая
          </span>
          <span class="font-medium truncate">{{ nextStop.name }}</span>
          <span class="text-white/40">•</span>
          <span class="tabular-nums">{{ formatTime(parseDT(nextStop.ts_arr) || parseDT(nextStop.ts_dep)) }}</span>
        </div>
      </div>

      <!-- Компактный список станций -->
      <div ref="listRef" class="divide-y divide-white/5 rounded-xl border border-white/5 overflow-hidden">
        <div
          v-for="(s, i) in stops"
          :key="i"
          :data-stop-index="i"
          class="flex items-center justify-between px-3 sm:px-4 py-3 sm:py-3.5 bg-[#18181B]/60 hover:bg-[#202024]/60 transition-colors scroll-mt-28"
          :class="[
            i < nextStopIndex ? 'opacity-70' : 'opacity-100',
          ]"
        >
          <!-- Левая часть: Название + бейджи -->
          <div class="min-w-0 pr-3">
            <div class="flex items-center gap-2">
              <span class="font-medium text-white truncate">{{ s.name }}</span>
              <span v-if="s.is_target" class="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded border text-emerald-400 bg-emerald-500/10 border-emerald-500/20">
                Наш сегмент
              </span>
              <span v-if="i === currentStopIndex" class="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded border text-sky-400 bg-sky-500/10 border-sky-500/20">
                Текущая
              </span>
              <span v-else-if="i === nextStopIndex" class="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded border text-amber-400 bg-amber-500/10 border-amber-500/20">
                Следующая
              </span>
            </div>
            <div class="text-xs text-white/40 mt-1 flex items-center gap-3">
              <span v-if="s.stop_min && s.stop_min !== 'Н/Д'">Стоянка {{ s.stop_min }} {{ plural(+s.stop_min || 0, 'мин', 'мин', 'мин') }}</span>
              <span v-if="s.code && s.code !== 'Н/Д'" class="text-white/30">код {{ s.code }}</span>
            </div>
          </div>

          <!-- Правая часть: Времена прибытия/отправления -->
          <div class="flex items-center gap-6 shrink-0">
            <div class="text-right">
              <div class="text-[11px] text-white/40 uppercase">Приб.</div>
              <div class="text-white tabular-nums">{{ formatTime(parseDT(s.ts_arr)) }}</div>
            </div>
            <div class="text-right">
              <div class="text-[11px] text-white/40 uppercase">Отпр.</div>
              <div class="text-white tabular-nums">{{ formatTime(parseDT(s.ts_dep)) }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>