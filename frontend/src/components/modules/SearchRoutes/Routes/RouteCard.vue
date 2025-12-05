<script setup>
import { ChevronRight, MapPinIcon, Zap, Star, Layers } from 'lucide-vue-next'
import { computed, ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({ train: { type: Object, required: true } })

const icons = { zap: Zap, star: Star, layers: Layers }

const classConfig = {
  BrandedTrain: { label: 'Фирменный', icon: 'star', theme: 'amber' },
  HighSpeedTrain: { label: 'Скоростной', icon: 'zap', theme: 'sky' },
  LegacyBrandedTrain: { label: 'Фирменный', icon: 'star', theme: 'amber' },
  LegacyHighSpeedTrain: { label: 'Скоростной', icon: 'zap', theme: 'sky' },
  LegacyTwoStoreyTrain: { label: 'Двухэтажный', icon: 'layers', theme: 'violet' }
}

const themeClasses = (t) => `text-${t}-400 bg-${t}-500/10 border-${t}-500/20`

const isElektrichka = computed(() => !props.train.type || props.train.type.toLowerCase().includes('пригородный'))
const trainName = computed(() => props.train.name?.trim())

const trainClasses = computed(() => {
  const classes = []
  const seen = new Set()
  
  if (props.train.is_express) {
    classes.push({ label: 'Экспресс', icon: 'zap', theme: 'red' })
    seen.add('Экспресс')
  }
  
  props.train.class?.forEach(cls => {
    const c = classConfig[cls]
    if (c && !seen.has(c.label)) {
      seen.add(c.label)
      classes.push(c)
    }
  })
  
  return classes
})

const dep = computed(() => new Date(props.train.ts_dep))
const arr = computed(() => new Date(props.train.ts_arr))
const now = ref(new Date())

const fmt = (d, opts) => d.toLocaleString('ru-RU', opts)
const fmtTime = d => fmt(d, { hour: '2-digit', minute: '2-digit' })
const fmtDate = d => fmt(d, { day: 'numeric', month: 'short' })

const duration = computed(() => {
  const m = Math.floor((arr.value - dep.value) / 60000)
  const h = Math.floor(m / 60), mins = m % 60
  return h ? (mins ? `${h} ч ${mins} мин` : `${h} ч`) : `${m} мин`
})

const progress = computed(() => {
  const [n, s, e] = [now.value, dep.value, arr.value].map(d => d.getTime())
  return Math.max(0, Math.min(100, (n - s) / (e - s) * 100))
})

const displayProgress = ref(0)
let interval

onMounted(() => {
  requestAnimationFrame(() => requestAnimationFrame(() => displayProgress.value = progress.value))
  interval = setInterval(() => { now.value = new Date(); displayProgress.value = progress.value }, 20000)
})

onUnmounted(() => clearInterval(interval))

const minTo = (target) => Math.ceil((target - now.value) / 60000)

const bgColor = computed(() => {
  const [n, d, a] = [now.value, dep.value, arr.value]
  if (n > a) return ['bg-zinc-400/5', 'hover:bg-zinc-500/10', 'opacity-80']
  if (n > d) return ['bg-emerald-400/10', 'hover:bg-emerald-500/20']
  const m = minTo(d)
  if (m <= 5) return ['bg-red-400/9', 'hover:bg-red-500/15']
  if (m <= 25) return ['bg-amber-400/12', 'hover:bg-amber-500/20']
  return ['bg-[#242527]', 'hover:bg-[#313235]']
})

const status = computed(() => {
  const [n, d, a] = [now.value, dep.value, arr.value]
  
  if (n > a) return { text: 'Ушёл', color: 'text-zinc-400', bg: 'bg-zinc-800', dot: 'bg-zinc-500' }
  
  if (n > d) {
    const m = minTo(a), h = Math.floor(m / 60), mins = m % 60
    const t = h && mins ? `${h}ч ${mins}м` : h ? `${h}ч` : `${mins}м`
    return { text: `В пути • ${t}`, color: 'text-green-400', bg: 'bg-green-500/10', dot: 'animate-pulse bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' }
  }
  
  const m = minTo(d)
  if (m <= 1) return { text: 'Отправляется', color: 'text-red-400', bg: 'bg-red-500/10', dot: 'animate-pulse bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' }
  if (m <= 5) return { text: `Посадка • ${m} мин`, color: 'text-red-400', bg: 'bg-red-500/10', dot: 'animate-pulse bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' }
  if (m <= 25) return { text: `Через ${m} мин`, color: 'text-amber-400', bg: 'bg-amber-500/10', dot: 'bg-amber-500' }
  
  return { text: 'По расписанию', color: 'text-zinc-300', bg: 'bg-zinc-700/50', dot: 'bg-zinc-500' }
})

const isDiffDay = computed(() => dep.value.toDateString() !== arr.value.toDateString())
</script>

<template>
  <article
    :class="bgColor"
    class="group relative w-full rounded-xl 
           p-4 cursor-pointer transition-all duration-300 shadow-lg shadow-black/20 active:scale-[0.99]"
  >
    <!-- Header -->
    <div class="flex items-start justify-between gap-3 mb-4">
      <div class="flex flex-col min-w-0 flex-1">
        <div class="flex items-baseline gap-2.5 flex-wrap">
          <span class="text-[10px] font-bold uppercase tracking-wider text-white/40 relative -top-2">
            {{ isElektrichka ? 'Электричка' : 'Поезд' }}
          </span>
          <span class="text-2xl font-black text-white tracking-tight leading-none">{{ train.number }}</span>
          
          <template v-for="(c, i) in trainClasses" :key="i">
            <span :class="themeClasses(c.theme)" class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wide border">
              <component :is="icons[c.icon]" :size="9" :stroke-width="2.5" />
              {{ c.label }}
            </span>
          </template>
        </div>
        
        <span v-if="trainName" class="mt-1 text-sm font-medium text-amber-500 truncate" :title="trainName">
          «{{ trainName }}»
        </span>
      </div>

      <div :class="[status.bg, status.color]" class="px-2.5 py-1 rounded-md text-[11px] font-medium flex items-center gap-1.5 shrink-0">
        <span :class="status.dot" class="w-1.5 h-1.5 rounded-full" />
        <span class="hidden xs:inline">{{ status.text }}</span>
        <span class="xs:hidden">{{ status.text }}</span>
      </div>
    </div>

    <!-- Timeline -->
    <div class="flex items-center gap-3">
      <div class="flex flex-col sm:flex-row sm:items-baseline sm:gap-2">
        <span class="text-xl font-bold text-white tabular-nums">{{ fmtTime(dep) }}</span>
        <span class="text-[11px] sm:text-xs text-white/40">{{ fmtDate(dep) }}</span>
      </div>

      <div class="flex-1 flex flex-col items-center min-w-12">
        <span class="text-[10px] font-medium text-white/30 mb-1.5">{{ duration }}</span>
        <div class="w-full h-0.5 bg-white/10 rounded-full relative overflow-hidden">
          <div class="absolute left-0 top-0 h-full rounded-full bg-linear-to-r from-lime-300 to-emerald-400 
                      shadow-[0_0_6px_rgba(16,185,129,0.4)] transition-all duration-1000 ease-out"
               :style="{ width: `${displayProgress}%` }" />
        </div>
        <div class="w-full flex justify-between -mt-1 px-px">
          <div class="w-1.5 h-1.5 rounded-full bg-zinc-900 border-[1.5px] transition-colors"
               :class="displayProgress > 0 ? 'border-lime-300 shadow-[0_0_4px_rgb(187,244,81,0.4)]' : 'border-white/20'" />
          <div class="w-1.5 h-1.5 rounded-full bg-zinc-900 border-[1.5px] transition-colors duration-500"
               :class="displayProgress >= 100 ? 'border-emerald-500 shadow-[0_0_4px_rgba(16,185,129,0.4)]' : 'border-white/20'" />
        </div>
      </div>

      <div class="flex flex-col items-end sm:flex-row sm:items-baseline sm:gap-2">
        <span class="text-xl font-bold text-white tabular-nums">{{ fmtTime(arr) }}</span>
        <span class="text-[11px] sm:text-xs text-white/40">
          {{ fmtDate(arr) }}<span v-if="isDiffDay" class="text-amber-500 font-bold"> +1</span>
        </span>
      </div>
    </div>

    <!-- Footer -->
    <div class="mt-3 pt-3 border-t border-white/5 flex items-center justify-between">
      <div class="flex items-center gap-2 text-sm text-white/50 truncate pr-3 min-w-0">
        <MapPinIcon :size="14" :stroke-width="2" class="text-white/25 shrink-0" />
        <span class="truncate group-hover:text-white/70 transition-colors">{{ train.route }}</span>
      </div>
      <ChevronRight :size="18" class="text-white/10 group-hover:text-white/40 group-hover:translate-x-0.5 transition-all duration-300 shrink-0" />
    </div>
  </article>
</template>