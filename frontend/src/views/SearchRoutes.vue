<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStationSearch } from '@/scripts/rzd_api'
import { ArrowRightLeft, Ban, Search } from 'lucide-vue-next';

const router = useRouter()
const { suggestions, search } = useStationSearch()
const active = ref(null), list = ref([]), cache = new Map()
const form = ref([{ name: '', code: null, ph: 'Откуда' }, { name: '', code: null, ph: 'Куда' }])

watch(suggestions, (v) => {
  if (!v?.length) return
  v.forEach(s => cache.set(s.code, s))
  if (active.value !== null) list.value = v
})

const isDisabled = () => {
  return form.value.some(f => !f.code)
}
const onBlur = () => {
  form.value.forEach(f => {
    if (f.code || !f.name) return
    const m = [...cache.values()].find(s => s.station.toLowerCase().includes(f.name.toLowerCase()))
    if (m) Object.assign(f, { name: m.station, code: m.code })
  })
  list.value = null
}
const isHaveSomeOne = () => {
  return form.value.some(f => !f.name)
}

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
    <div class="w-full md:w-4/6 relative m-4 p-2 bg-[#18181B] rounded-xl border border-white/10">
      <div class="absolute inset-0 scale-x-105 scale-y-110 bg-linear-to-bl from-purple-500 via-pink-500 to-orange-400 blur-3xl -z-1 opacity-20"></div>
      <div class="relative z-1">
        <div class="flex gap-2">
          
          <template v-for="(f, i) in form" :key="i">
            <div class="autocomplete-wrapper relative align-middle justify-center items-center flex-1 transition-all duration-700">
              <div class="relative w-full">
                <input 
                  type="text" 
                  v-model="f.name" 
                  placeholder=" " 
                  @input="onInput(i)" 
                  @focus="focus(i)" 
                  @blur="onBlur()"
                  class="peer bg-transparent w-full rounded-sm focus:outline-none focus:ring focus:ring-white/10 transition-all duration-200 text-white 
                         pt-3 pb-1 px-2" 
                />
                <label 
                  class="absolute left-2 text-white/30 pointer-events-none transition-all duration-200
                         text-xs -top-1
                         peer-placeholder-shown:text-base peer-placeholder-shown:top-2
                         peer-focus:text-xs peer-focus:-top-2 peer-focus:text-white/70"
                >
                  {{ f.ph }}
                </label>
              </div>
              
              <ul v-if="active === i && list?.length" 
                  class="suggestions-list absolute z-10 w-full bg-[linear-gradient(139deg,rgba(26,30,40,1)_0%,rgba(26,30,40,1)_50%,rgba(27,18,30,1)_100%)] rounded-sm shadow-lg max-h-48 overflow-y-hidden text-white top-full mt-1">
                <li v-for="s in list" :key="s.code" @mousedown.prevent="select(s)"
                  class="p-2 cursor-pointer hover:bg-black/50">
                  {{ s.station }}
                </li>
              </ul>
            </div>

            <div v-if="i < form.length - 1" class="relative flex items-center justify-center px-1">
              <div class="w-px h-8 bg-white/10"></div>
            </div>
          </template>

          <button
            @click="!isDisabled() ? find() : ''"
            :class="[
              'group relative flex-1 max-w-[100px] max-h-10 border-2 font-bold py-2 px-4 rounded-lg transition duration-500 overflow-hidden',
              {
                'cursor-not-allowed opacity-70 bg-white/5 text-white/50 border-white/10 hover:border-red-500/50 hover:text-red-400': isDisabled(),
                'cursor-pointer bg-white text-black hover:bg-transparent hover:text-white border-white': !isDisabled()
              }
            ]"
          >
            <span v-if="isDisabled()" class="flex items-center justify-center w-full h-full relative">
              <span class="absolute transition-all duration-500 group-hover:opacity-0 group-hover:translate-y-4">
                Найти
              </span>
              <Ban :size="24" class="absolute transition-all duration-500 opacity-0 -rotate-90 scale-50 group-hover:opacity-100 group-hover:rotate-0 group-hover:scale-100 text-red-500"/>
            </span>
            <span v-else class="flex items-center justify-center w-full h-full relative translate-x-2 group-hover:translate-x-0 transition duration-700">
              Найти
              <Search :size="20" class="inline-block opacity-0 -rotate-90 -translate-x-8 group-hover:opacity-100 group-hover:translate-x-1 group-hover:rotate-12 transition duration-1000"/>
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>