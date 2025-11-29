<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStationSearch } from '@/scripts/rzd_api'

const router = useRouter()
const { suggestions, search } = useStationSearch()
const active = ref(null), list = ref([]), cache = new Map()
const form = ref([{ name: '', code: null, ph: 'Откуда' }, { name: '', code: null, ph: 'Куда' }])

watch(suggestions, (v) => {
  if (!v?.length) return
  v.forEach(s => cache.set(s.code, s))
  if (active.value !== null) list.value = v
})

const onInput = (i) => {
  active.value = i
  form.value[i].code = null
  const v = form.value[i].name.toLowerCase()
  if (!v) return list.value = []

  const local = [...cache.values()]
    .filter(s => s.station.toLowerCase().includes(v))
    .sort((a, b) => b.station.toLowerCase().startsWith(v) - a.station.toLowerCase().startsWith(v))
  
  local.length ? (list.value = local) : search(v)
}

const select = (s) => {
  Object.assign(form.value[active.value], { name: s.station, code: s.code })
  active.value = null
}

const focus = (index) => {
  if (index == active.value) return
  active.value = index
  list.value = null
}

const find = () => {
  form.value.forEach(f => {
    if (f.code || !f.name) return
    const m = [...cache.values()].find(s => s.station.toLowerCase().includes(f.name.toLowerCase()))
    if (m) Object.assign(f, { name: m.station, code: m.code })
  })

  if (form.value.some(f => !f.code)) return console.warn('Ошибка: станции не распознаны')

  router.push({ path: '/routes', query: { from: form.value[0].code, to: form.value[1].code } })
  active.value = null
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="w-2/6 relative p-6 bg-[linear-gradient(139deg,rgba(36,40,50,1)_0%,rgba(36,40,50,1)_50%,rgba(37,28,40,1)_100%)] rounded-xl shadow-xl/30">
      <div class="absolute inset-0 scale-x-105 scale-y-110 bg-linear-to-bl from-purple-500 via-pink-500 to-orange-400 blur-xl -z-1 opacity-10"></div>
      <div class="relative z-1">
        <div class="flex space-x-4 mb-4">
          <div v-for="(f, i) in form" :key="i" class="autocomplete-wrapper relative flex-1">
            <input type="text" v-model="f.name" :placeholder="f.ph"
              @input="onInput(i)" @focus="focus(i)"
              class="bg-transparent p-2 w-full rounded-sm focus:outline-none focus:ring-2 focus:ring-white/40" />
            
            <ul v-if="active === i && list?.length" 
                class="suggestions-list absolute z-10 w-full bg-[linear-gradient(139deg,rgba(26,30,40,1)_0%,rgba(26,30,40,1)_50%,rgba(27,18,30,1)_100%)] rounded-sm mt-1 shadow-lg max-h-48 overflow-y-hidden">
              <li v-for="s in list" :key="s.code" @mousedown.prevent="select(s)"
                class="p-2 cursor-pointer hover:bg-black/50">
                {{ s.station }}
              </li>
            </ul>
          </div>
        </div>

        <button @click="find" class="w-full bg-white text-black hover:bg-white/5 hover:text-white border-white border-2 font-bold py-2 px-4 rounded-lg transition duration-900">
          Найти
        </button>
      </div>
    </div>
  </div>
</template>