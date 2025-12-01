<script setup>
import { ref, watch, nextTick, computed } from 'vue'
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

// Сбрасываем индекс при изменении входных данных
watch(() => props.suggestions, () => idx.value = -1)

// --- Вспомогательная функция для экранирования Regex ---
const escapeRegExp = (string) => {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

// --- Вычисляем текущий запрос (текст до курсора) ---
const currentQuery = computed(() => {
  const val = props.modelValue || ''
  // Если курсор в начале (0), считаем что запроса нет или берем весь текст, 
  // зависит от логики, но здесь сохраняем логику "до курсора"
  const limit = cursorPos.value || val.length
  return val.slice(0, limit)
})

// --- Сортировка списка ---
const sortedSuggestions = computed(() => {
  if (!props.suggestions.length) return []
  
  const query = currentQuery.value.toLowerCase().trim()
  if (!query) return props.suggestions

  // Создаем копию массива, чтобы не мутировать пропсы
  return [...props.suggestions].sort((a, b) => {
    const nameA = a.station.toLowerCase()
    const nameB = b.station.toLowerCase()
    
    const startsA = nameA.startsWith(query)
    const startsB = nameB.startsWith(query)

    // 1. Приоритет тем, что начинаются с запроса
    if (startsA && !startsB) return -1
    if (!startsA && startsB) return 1

    // 2. Если оба начинаются или оба содержат - сортируем по индексу вхождения
    // (чем ближе к началу, тем выше)
    const indexA = nameA.indexOf(query)
    const indexB = nameB.indexOf(query)
    
    if (indexA !== indexB) {
      return indexA - indexB
    }

    // 3. Алфавитный порядок как запасной вариант
    return nameA.localeCompare(nameB)
  })
})

const updateCursorAndSearch = (el) => {
  if (!el) return
  cursorPos.value = el.selectionStart
  emit('search', currentQuery.value)
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
  idx.value = -1
}

const blur = () => {
  setTimeout(() => {
    // При блюре выбираем первый элемент из ОТСОРТИРОВАННОГО списка, если он есть
    if (focused.value && sortedSuggestions.value.length > 0) {
      select(sortedSuggestions.value[0])
    }
    focused.value = false
    idx.value = -1
  }, 100)
}

const searchByCursor = (e) => {
  setTimeout(() => updateCursorAndSearch(e.target), 0)
}

const onFocus = (e) => {
  focused.value = true
  searchByCursor(e)
}

// --- Исправленная функция подсветки ---
const highlight = (text) => {
  const query = currentQuery.value
  if (!query) return text

  // Экранируем спецсимволы, чтобы ввод "(" не ломал регулярку
  const escapedQuery = escapeRegExp(query)
  
  // Создаем регулярку для поиска с сохранением регистра (i)
  const regex = new RegExp(`(${escapedQuery})`, 'gi')
  
  return text.replace(regex, '<span class="text-orange-400 font-bold">$1</span>')
}

const onKeyDown = (e) => {
  // Используем sortedSuggestions вместо props.suggestions
  const list = sortedSuggestions.value
  const len = list.length
  
  switch (e.key) {
    case 'ArrowDown':
      if (!focused.value || !len) return
      e.preventDefault()
      idx.value = idx.value < len - 1 ? idx.value + 1 : 0
      nextTick(() => {
        listRef.value?.children[idx.value]?.scrollIntoView({ block: 'nearest' })
      })
      break
      
    case 'ArrowUp':
      if (!focused.value || !len) return
      e.preventDefault()
      idx.value = idx.value <= 0 ? len - 1 : idx.value - 1
      nextTick(() => {
        listRef.value?.children[idx.value]?.scrollIntoView({ block: 'nearest' })
      })
      break
      
    case 'Enter':
      if (!focused.value || !len) return
      e.preventDefault()
      const selectedIdx = idx.value >= 0 ? idx.value : 0
      select(list[selectedIdx])
      break
      
    case 'Escape':
      e.preventDefault()
      focused.value = false
      idx.value = -1
      break
      
    case 'Tab':
      if (focused.value && len) {
        const selectedIdx = idx.value >= 0 ? idx.value : 0
        select(list[selectedIdx])
      }
      break
  }
}

const onKeyUp = (e) => {
  if (['ArrowLeft', 'ArrowRight'].includes(e.key)) {
    searchByCursor(e)
  }
}
</script>

<template>
  <div class="relative group/input min-w-0 flex items-start gap-3">
    
    <div v-if="marker" 
         class="sm:hidden relative shrink-0 mt-3 -top-2 left-0 w-4 -mr-1 pr-5 pl-2.5 py-0.4 text-center text-orange-400 font-extrabold text-xl select-none">
      {{ marker }}
    </div>

    <div class="relative w-full">
      <input
        :value="modelValue" 
        @input="handleInput" 
        @focus="onFocus"
        @click="searchByCursor"
        @keydown="onKeyDown"
        @keyup="onKeyUp"
        @blur="blur"
        type="text" 
        placeholder=" "
        autocomplete="off"
        class="relative sm:top-[3px] sm:placeholder-shown:-top-0.5 h-8 sm:h-6 sm:placeholder-shown:h-8 peer bg-transparent w-full 
        rounded-sm py-1.5 sm:mt-1 px-3 text-white font-medium placeholder-transparent focus:outline-none focus:bg-white/5 transition-all duration-700 text-ellipsis overflow-hidden"
      />
      
      <label class="hidden sm:block absolute left-3 -top-2 text-[10px] uppercase tracking-wider 
      text-white/40 pointer-events-none transition-all peer-placeholder-shown:top-1.5 peer-placeholder-shown:text-base 
      peer-placeholder-shown:normal-case peer-placeholder-shown:text-white/50 truncate max-w-[80%]">
        {{ label }}
      </label>

      <span v-if="!modelValue" class="sm:hidden absolute left-3 top-1.5 text-base text-white/50 pointer-events-none transition-all truncate max-w-[90%]">
        {{ label }}
      </span>

      <Loader2 v-if="focused && isLoading" class="absolute right-2 top-3 animate-spin text-white/30" :size="16" />

      <!-- Используем sortedSuggestions в цикле -->
      <ul v-if="focused && sortedSuggestions.length" ref="listRef"
          class="absolute z-50 top-[calc(100%+4px)] left-0 w-full max-h-60 overflow-y-auto rounded-lg shadow-2xl border border-white/10 bg-[#1a1e28] scrollbar-thin text-white">
        <li v-for="(s, i) in sortedSuggestions" :key="s.code" @mousedown.prevent="select(s)"
            :class="['px-4 py-3 cursor-pointer text-sm border-b border-white/5 last:border-0 transition-colors', i === idx ? 'bg-white/10 border-l-2 border-l-orange-400' : 'hover:bg-white/5 hover:border-l-2 hover:border-l-orange-500']">
          <!-- highlight теперь принимает только текст станции -->
          <div v-html="highlight(s.station)" class="font-medium"></div>
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