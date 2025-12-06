<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MapPinIcon, Zap, Star, Layers, ArrowLeft } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const trainParam = computed(() => String(route.query.train || '').trim())
const fromParam = computed(() => String(route.query.from || '').trim())
const toParam = computed(() => String(route.query.to || '').trim())

const loading = ref(false)
const error = ref(null)
const stops = ref([])
const trainNumber = ref('')
const trainInfo = ref(null)
const originName = ref('')
const destinationName = ref('')
const currentTime = ref(new Date())
let tick = null

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

// Функция скролла до текущей станции
const scrollToCurrentStop = async () => {
  await nextTick()
  setTimeout(() => {
    const el = document.querySelector(`[data-stop-index="${nextStopIndex.value}"]`)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, 100)
}

const goBack = () => {
  router.back()
}

const fetchStops = async () => {
  if (!trainParam.value || !fromParam.value || !toParam.value) {
    error.value = 'Нужно указать train, from и to'
    return
  }
  error.value = null
  loading.value = true
  try {
    const res = await fetch(`/api/station_list?train_num=${encodeURIComponent(trainParam.value)}&str_from=${encodeURIComponent(fromParam.value)}&str_to=${encodeURIComponent(toParam.value)}`)
    const data = await res.json()
    stops.value = Array.isArray(data?.stops) ? data.stops : []
    trainNumber.value = data?.train || trainParam.value
    originName.value = stops.value[0]?.name || ''
    destinationName.value = stops.value[stops.value.length - 1]?.name || ''

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
      trainInfo.value = (rdata?.trains || []).find(t => t.number === trainNumber.value) || null
    }
    
    scrollToCurrentStop()
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
  tick = setInterval(() => { currentTime.value = new Date() }, 10000)
})
onUnmounted(() => { if (tick) clearInterval(tick) })
watch(() => route.fullPath, fetchStops)

const isElektrichka = computed(() => {
  const type = (trainInfo.value?.type || '').toLowerCase()
  return !type || type.includes('пригородный')
})

const originStop = computed(() => stops.value.filter(s => s.is_target)[0] || null)
const destinationStop = computed(() => {
  const targets = stops.value.filter(s => s.is_target)
  return targets[targets.length - 1] || null
})

const routeDeparture = computed(() => parseDT(trainInfo.value?.ts_dep) || parseDT(originStop.value?.ts_dep) || parseDT(originStop.value?.ts_arr))
const routeArrival = computed(() => parseDT(trainInfo.value?.ts_arr) || parseDT(destinationStop.value?.ts_arr) || parseDT(destinationStop.value?.ts_dep))

const durationText = computed(() => {
  if (!routeDeparture.value || !routeArrival.value) return ''
  const diff = routeArrival.value - routeDeparture.value
  const h = Math.floor(diff / 3600000)
  const m = Math.floor((diff % 3600000) / 60000)
  if (h === 0) return `${m} мин`
  if (m === 0) return `${h} ч`
  return `${h} ч ${m} мин`
})

const progressPercent = computed(() => {
  if (!routeDeparture.value || !routeArrival.value) return 0
  const total = routeArrival.value - routeDeparture.value
  const curr = currentTime.value - routeDeparture.value
  return Math.max(0, Math.min(100, (curr / total) * 100))
})

const status = computed(() => {
  const now = currentTime.value
  const dep = routeDeparture.value
  const arr = routeArrival.value
  if (!dep || !arr) return { text: 'Статус неизвестен', color: 'text-zinc-300', bg: 'bg-zinc-700/50', dot: 'bg-zinc-500' }
  if (now > arr) return { text: 'Прибыл', color: 'text-zinc-400', bg: 'bg-zinc-800', dot: 'bg-zinc-500' }
  if (now > dep) {
    const min = Math.ceil((arr - now) / 60000)
    const h = Math.floor(min / 60), m = min % 60
    const t = h > 0 ? (m > 0 ? `${h}ч ${m}м` : `${h}ч`) : `${m}м`
    return { text: `В пути (${t})`, color: 'text-green-400', bg: 'bg-green-500/10', dot: 'animate-pulse bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' }
  }
  const minToDep = Math.ceil((dep - now) / 60000)
  if (minToDep <= 5) return { text: minToDep <= 1 ? 'Отправляется' : `Посадка • ${minToDep} мин`, color: 'text-red-400', bg: 'bg-red-500/10', dot: 'animate-pulse bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' }
  if (minToDep <= 25) return { text: `Через ${minToDep} мин`, color: 'text-amber-400', bg: 'bg-amber-500/10', dot: 'bg-amber-500' }
  return { text: 'По расписанию', color: 'text-zinc-300', bg: 'bg-zinc-700/50', dot: 'bg-zinc-500' }
})

const stopTime = (s) => parseDT(s?.ts_dep) || parseDT(s?.ts_arr) || null
const nextStopIndex = computed(() => {
  for (let i = 0; i < stops.value.length; i++) {
    const t = stopTime(stops.value[i])
    if (t && t >= currentTime.value) return i
  }
  return stops.value.length - 1
})
const currentStopIndex = computed(() => Math.max(0, nextStopIndex.value - 1))
const nextStop = computed(() => stops.value[nextStopIndex.value] || null)

const listRef = ref(null)

watch(nextStopIndex, (newVal, oldVal) => {
  if (newVal !== oldVal && stops.value.length > 0) {
    scrollToCurrentStop()
  }
})

const timelinePositions = computed(() => {
  const dep = routeDeparture.value, arr = routeArrival.value
  const total = dep && arr ? (arr - dep) : null
  return stops.value.map((s, i) => {
    const t = stopTime(s)
    const percent = t && total ? Math.min(100, Math.max(0, ((t - dep) / total) * 100)) : (stops.value.length === 1 ? 0 : (i / (stops.value.length - 1)) * 100)
    const state = i < nextStopIndex.value ? 'past' : (i === nextStopIndex.value ? 'next' : 'future')
    return { i, name: s.name, is_target: !!s.is_target, percent, state }
  })
})

const displayProgress = ref(0)
watch(progressPercent, (v) => { requestAnimationFrame(() => requestAnimationFrame(() => { displayProgress.value = v })) })
onMounted(() => { requestAnimationFrame(() => requestAnimationFrame(() => { displayProgress.value = progressPercent.value })) })

const classLabels = {
  BrandedTrain: { label: 'Фирменный', icon: 'star', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  HighSpeedTrain: { label: 'Скоростной', icon: 'zap', color: 'text-sky-400', bg: 'bg-sky-500/10', border: 'border-sky-500/20' },
  LegacyTwoStoreyTrain: { label: 'Двухэтажный', icon: 'layers', color: 'text-violet-400', bg: 'bg-violet-500/10', border: 'border-violet-500/20' }
}
const trainClasses = computed(() => {
  const classes = []
  if (trainInfo.value?.is_express) classes.push({ label: 'Экспресс', icon: 'zap', color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' })
  const seen = new Set(classes.map(c => c.label))
  ;(trainInfo.value?.class || []).forEach(cls => {
    const it = classLabels[cls] || classLabels[cls.replace('Legacy', '')]
    if (it && !seen.has(it.label)) { seen.add(it.label); classes.push(it) }
  })
  return classes
})
</script>

<template>
  <header class="sticky top-0 px-3 sm:px-20 z-30 backdrop-blur-md w-full pt-3 sm:pt-4 pb-2 sm:pb-3">
    <div class="flex items-start justify-between mb-2 sm:mb-3">
      <div class="flex flex-col min-w-0 flex-1 mr-2 sm:mr-3">
        <span :class="isElektrichka ? 'text-white/40' : 'text-white/50'" class="text-[10px] sm:text-xs font-bold uppercase tracking-wider">
        <span class="text-2xl sm:text-3xl font-black text-white tracking-tight leading-none">{{ trainNumber || trainParam }}</span>
          {{ isElektrichka ? 'Электричка' : 'Поезд' }}
        </span>
        <div class="flex items-center gap-2 sm:gap-3 flex-wrap mt-1">
          <div v-if="trainClasses.length" class="flex items-center gap-1 sm:gap-1.5 flex-wrap">
            <span v-for="(cls, idx) in trainClasses" :key="idx" class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] sm:text-[10px] font-semibold uppercase tracking-wide border" :class="[cls.bg, cls.color, cls.border]">
              <Zap v-if="cls.icon === 'zap'" :size="10" :stroke-width="2.5" />
              <Star v-else-if="cls.icon === 'star'" :size="10" :stroke-width="2.5" />
              <Layers v-else-if="cls.icon === 'layers'" :size="10" :stroke-width="2.5" />
              {{ cls.label }}
            </span>
          </div>
        </div>
        <span v-if="trainInfo?.name?.trim()" class="mt-1 sm:mt-1.5 text-xs sm:text-sm font-medium text-amber-500 truncate">«{{ trainInfo.name.trim() }}»</span>
      </div>
      <div class="px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg text-[10px] sm:text-xs font-medium border border-transparent flex items-center gap-1.5 sm:gap-2 shrink-0" :class="[status.bg, status.color]">
        <span class="w-1.5 h-1.5 rounded-full" :class="status.dot"></span>
        <span class="hidden sm:inline">{{ status.text }}</span>
        <span class="sm:hidden">{{ status.text.split('(')[0].trim() }}</span>
      </div>
    </div>

    <div class="flex items-end justify-between gap-2 sm:gap-4">
      <div class="flex flex-col">
        <span class="text-lg sm:text-2xl font-bold text-white tabular-nums leading-none mb-0.5 sm:mb-1">{{ formatTime(routeDeparture) }}</span>
        <span class="text-[10px] sm:text-sm font-medium text-white/40">{{ formatDate(routeDeparture) }}</span>
      </div>
      <div class="flex-1 flex flex-col items-center pb-1 sm:pb-1.5 px-1 sm:px-2 min-w-16 sm:min-w-20">
        <div class="text-[10px] sm:text-xs font-medium text-white/30 mb-1.5 sm:mb-2">{{ durationText }}</div>
        <div class="w-full h-1 bg-white/10 rounded-full relative overflow-hidden">
          <div class="absolute left-0 top-0 h-full rounded-full bg-linear-to-r from-lime-300 to-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.5)] transition-all duration-1000 ease-out" :style="{ width: `${displayProgress}%` }"></div>
        </div>
        <div class="relative w-full h-4 sm:h-5 mt-1.5 sm:mt-2 hidden sm:block">
          <div v-for="p in timelinePositions" :key="p.i" class="absolute -translate-x-1/2 top-1/2 -translate-y-1/2" :style="{ left: `${p.percent}%` }">
            <div class="w-2.5 h-2.5 rounded-full border-2" :class="[p.state === 'past' ? 'bg-emerald-400 border-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.6)]' : '', p.state === 'next' ? 'bg-amber-400 border-amber-400 animate-pulse shadow-[0_0_6px_rgba(245,158,11,0.6)]' : '', p.state === 'future' ? 'bg-white/10 border-white/20' : '', p.is_target ? 'ring-2 ring-white/40' : '']" :title="p.name"></div>
          </div>
        </div>
      </div>
      <div class="flex flex-col items-end text-right">
        <span class="text-lg sm:text-2xl font-bold text-white tabular-nums leading-none mb-0.5 sm:mb-1">{{ formatTime(routeArrival) }}</span>
        <span class="text-[10px] sm:text-sm font-medium text-white/40">{{ formatDate(routeArrival) }}</span>
      </div>
    </div>

    <div class="mt-3 sm:mt-4 flex items-center gap-2 text-xs sm:text-sm text-white/60 truncate">
      <MapPinIcon :size="16" class="text-white/20 shrink-0"/>
      <span class="truncate">{{ trainInfo?.route || (originName && destinationName ? `${originName} — ${destinationName}` : 'Маршрут') }}</span>
    </div>
  </header>

  <div class="container mx-auto px-3 sm:px-64 bg-transparent">
    <section class="mt-2">
      <div v-if="loading" class="text-white/60 text-sm py-8 text-center">Загружаем остановки…</div>
      <div v-else-if="error" class="text-red-400 text-sm py-8">{{ error }}</div>

      <template v-else>
        <div v-if="nextStop" class="flex items-center gap-2 text-white/80 text-xs sm:text-sm mb-3 sm:mb-4">
          <span class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">Следующая</span>
          <span class="font-medium truncate">{{ nextStop.name }}</span>
          <span class="text-white/40">•</span>
          <span class="tabular-nums">{{ formatTime(parseDT(nextStop.ts_arr) || parseDT(nextStop.ts_dep)) }}</span>
        </div>

        <div ref="listRef" class="divide-y divide-white/5 rounded-xl border border-white/5 overflow-hidden">
          <div
            v-for="(s, i) in stops" :key="i" :data-stop-index="i"
            class="flex items-center justify-between px-2.5 sm:px-4 py-2.5 sm:py-3.5 transition-colors scroll-mt-28"
            :class="[i < nextStopIndex ? 'opacity-40' : '', s.is_target === 0 ? 'bg-indigo-400/10' : s.is_target === 1 ? 'bg-amber-400/8' : 'bg-[#242527]/90']"
          >
            <div class="min-w-0 pr-2 sm:pr-3 flex-1">
              <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                <span class="font-medium text-sm sm:text-base text-white truncate">{{ s.name }}</span>
                <span v-if="s.is_target === 0" class="text-[9px] sm:text-[12px] uppercase font-semibold px-1.5 sm:px-2 py-0.5 rounded border text-indigo-400 bg-indigo-500/10 border-indigo-500/20">were are you from?</span>
                <span v-if="s.is_target === 1" class="text-[9px] sm:text-[12px] uppercase font-semibold px-1.5 sm:px-2 py-0.5 rounded border text-amber-400 bg-amber-500/10 border-amber-500/20">пункт назначения</span>
                <span v-if="i === nextStopIndex" class="text-[9px] sm:text-[10px] uppercase font-semibold px-1 sm:px-1.5 py-0.5 rounded border text-amber-400 bg-amber-500/10 border-amber-500/20">следующая</span>
              </div>
              <div class="text-[10px] sm:text-xs text-white/40 mt-0.5 sm:mt-1 flex items-center gap-2 sm:gap-3">
                <span v-if="s.stop_min && s.stop_min !== 'Н/Д'">{{ s.stop_min }} мин</span>
                <span v-if="s.code && s.code !== 'Н/Д'" class="text-white/30 hidden sm:inline">код {{ s.code }}</span>
              </div>
            </div>
            <div class="flex items-center gap-3 sm:gap-6 shrink-0 text-right">
              <div>
                <div class="text-[9px] sm:text-[11px] text-white/40 uppercase">прибытие</div>
                <div class="text-xs sm:text-base text-white tabular-nums">{{ formatTime(parseDT(s.ts_arr)) }}</div>
              </div>
              <div>
                <div class="text-[9px] sm:text-[11px] text-white/40 uppercase">отправление</div>
                <div class="text-xs sm:text-base text-white tabular-nums">{{ formatTime(parseDT(s.ts_dep)) }}</div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </section>
  </div>
</template>