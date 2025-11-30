<script setup>
import { ref, watch, nextTick } from 'vue'
import { Loader2 } from 'lucide-vue-next'

const props = defineProps({ 
  modelValue: String, 
  label: String, 
  marker: String,
  suggestions: { type: Array, default: () => [] }, 
  isLoading: Boolean 
})

const emit = defineEmits(['update:modelValue', 'select', 'search'])

const focused = ref(false)
const listRef = ref(null)
const idx = ref(-1)
const cursorPos = ref(0)

watch(() => props.suggestions, () => idx.value = -1)

const updateCursorAndSearch = (el) => {
  if (!el) return
  cursorPos.value = el.selectionStart
  const val = props.modelValue || ''
  const query = val.slice(0, cursorPos.value)
  emit('search', query)
}

const handleInput = (e) => {
  const val = e.target.value
  emit('update:modelValue', val)
  idx.value = -1
  updateCursorAndSearch(e.target)
}

const select = (item) => {
  emit('select', item)
  focused.value = false
}

const blur = () => {
  setTimeout(() => {
    if (focused.value && props.suggestions.length > 0) {
      select(props.suggestions[0])
    }
    focused.value = false
    idx.value = -1
  }, 200)
}

const searchByCursor = (e) => {
  setTimeout(() => updateCursorAndSearch(e.target), 0)
}

const onFocus = (e) => {
  focused.value = true
  searchByCursor(e)
}

const highlight = (text, fullValue) => {
  const limit = cursorPos.value || fullValue?.length || 0
  const q = fullValue?.slice(0, limit)
  return q ? text.replace(new RegExp(`(${q})`, 'gi'), '<span class="text-orange-400 font-bold">$1</span>') : text
}

const onKey = (e) => {
  if (['ArrowLeft', 'ArrowRight'].includes(e.key)) {
    searchByCursor(e)
    return
  }

  const len = props.suggestions.length
  if (!len) return
  
  if (['ArrowUp', 'ArrowDown'].includes(e.key)) {
    e.preventDefault()
    idx.value = (idx.value + (e.key === 'ArrowDown' ? 1 : -1) + len) % len
    nextTick(() => listRef.value?.children[idx.value]?.scrollIntoView({ block: 'nearest' }))
  } else if (e.key === 'Enter') {
    e.preventDefault()
    select(props.suggestions[Math.max(0, idx.value)])
  } else if (e.key === 'Escape') {
    focused.value = false
  }
}
</script>

<template>
  <!-- Добавлен flex и gap для позиционирования буквы слева -->
  <div class="relative group/input min-w-0 flex items-start gap-3">
    
    <!-- Буква-маркер (Видна только на мобильных sm:hidden) -->
    <div v-if="marker" 
         class="sm:hidden relative shrink-0 mt-3 -top-2 left-1 w-4 -mr-1 pr-5 pl-2.5 py-0.4 text-center text-orange-400 font-extrabold text-xl select-none">
      {{ marker }}
    </div>

    <div class="relative w-full">
      <input
        :value="modelValue" 
        @input="handleInput" 
        @focus="onFocus"
        @click="searchByCursor"
        @keyup="onKey"
        @blur="blur" 
        @keydown="onKey" 
        type="text" 
        placeholder=" "
        class="relative top-[3px] placeholder-shown:-top-0.5 h-6 placeholder-shown:h-8 peer bg-transparent w-full rounded-sm py-1.5 mt-1 px-3 text-white font-medium placeholder-transparent focus:outline-none focus:bg-white/5 transition-all duration-700 text-ellipsis overflow-hidden"
      />
      
      <!-- Label: Скрыт на мобильных (hidden), виден на десктопе (sm:block) -->
      <label class="hidden sm:block absolute left-3 -top-2 text-[10px] uppercase tracking-wider text-white/40 pointer-events-none transition-all peer-placeholder-shown:top-1.5 peer-placeholder-shown:text-base peer-placeholder-shown:normal-case peer-placeholder-shown:text-white/50 truncate max-w-[80%]">
        {{ label }}
      </label>

      <!-- Плейсхолдер для мобильных (Виден, когда label скрыт и input пуст) -->
      <span v-if="!modelValue" class="sm:hidden absolute left-3 top-1.5 text-base text-white/50 pointer-events-none transition-all truncate max-w-[90%]">
        {{ label }}
      </span>

      <Loader2 v-if="focused && isLoading" class="absolute right-2 top-3 animate-spin text-white/30" :size="16" />

      <!-- Выпадающий список (перенесен внутрь relative w-full, чтобы выравнивался по инпуту, а не по букве) -->
      <ul v-if="focused && (suggestions.length || (modelValue && !isLoading && suggestions.length))" ref="listRef"
          class="absolute z-50 top-[calc(100%+4px)] left-0 w-full max-h-60 overflow-y-auto rounded-lg shadow-2xl border border-white/10 bg-[#1a1e28] scrollbar-thin text-white">
        <li v-if="!suggestions.length" class="p-4 text-center text-white/40 text-sm">Ничего не найдено</li>
        <li v-for="(s, i) in suggestions" :key="s.code" @mousedown.prevent="select(s)"
            :class="['px-4 py-3 cursor-pointer text-sm border-b border-white/5 last:border-0 transition-colors', i === idx ? 'bg-white/10' : 'hover:bg-white/5']">
          <div v-html="highlight(s.station, modelValue)" class="font-medium"></div>
          <div class="text-xs text-white/30 mt-0.5">Код: {{ s.code }}</div>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.scrollbar-thin::-webkit-scrollbar { width: 6px; }
.scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
.scrollbar-thin::-webkit-scrollbar-thumb { background-color: rgba(255, 255, 255, 0.2); border-radius: 20px; }
</style>