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
const activeIndex = ref(-1)

// Сброс индекса при изменении списка
watch(() => props.suggestions, () => activeIndex.value = -1)

// Текущий запрос
const query = computed(() => (props.modelValue || '').toLowerCase().trim())

// Сортировка: сначала те, что начинаются с запроса
const sortedList = computed(() => {
  if (!props.suggestions.length || !query.value) return props.suggestions
  
  return [...props.suggestions].sort((a, b) => {
    const nameA = a.station.toLowerCase()
    const nameB = b.station.toLowerCase()
    const startsA = nameA.startsWith(query.value)
    const startsB = nameB.startsWith(query.value)
    
    if (startsA !== startsB) return startsA ? -1 : 1
    return nameA.indexOf(query.value) - nameB.indexOf(query.value)
  })
})

// Показывать дропдаун?
const showDropdown = computed(() => focused.value && sortedList.value.length > 0)

// Подсветка совпадений
const highlight = (text) => {
  if (!query.value) return text
  const escaped = query.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${escaped})`, 'gi'), '<mark>$1</mark>')
}

// Выбор элемента
const select = (item) => {
  emit('select', item)
  focused.value = false
  activeIndex.value = -1
}

// Скролл к активному элементу
const scrollToActive = () => {
  nextTick(() => {
    listRef.value?.children[activeIndex.value]?.scrollIntoView({ block: 'nearest' })
  })
}

// Обработчики
const onInput = (e) => {
  emit('update:modelValue', e.target.value)
  emit('search', e.target.value)
  activeIndex.value = -1
}

const onFocus = () => {
  focused.value = true
  emit('search', props.modelValue || '')
}

const onBlur = () => {
  setTimeout(() => {
    if (focused.value && sortedList.value.length) {
      select(sortedList.value[Math.max(0, activeIndex.value)])
    }
    focused.value = false
  }, 150)
}

const onKeydown = (e) => {
  const len = sortedList.value.length
  if (!showDropdown.value) return

  const actions = {
    ArrowDown: () => {
      e.preventDefault()
      activeIndex.value = (activeIndex.value + 1) % len
      scrollToActive()
    },
    ArrowUp: () => {
      e.preventDefault()
      activeIndex.value = (activeIndex.value - 1 + len) % len
      scrollToActive()
    },
    Enter: () => {
      e.preventDefault()
      select(sortedList.value[Math.max(0, activeIndex.value)])
    },
    Escape: () => {
      focused.value = false
      activeIndex.value = -1
    },
    Tab: () => {
      select(sortedList.value[Math.max(0, activeIndex.value)])
    }
  }

  actions[e.key]?.()
}
</script>

<template>
  <div class="autocomplete">
    <!-- Маркер (мобильный) -->
    <span v-if="marker" class="marker">{{ marker }}</span>

    <div class="input-wrapper">
      <input
        :value="modelValue"
        @input="onInput"
        @focus="onFocus"
        @blur="onBlur"
        @keydown="onKeydown"
        type="text"
        :placeholder="label"
        autocomplete="off"
      />
      
      <label>{{ label }}</label>

      <Loader2 v-if="focused && isLoading" class="loader" :size="16" />

      <!-- Выпадающий список -->
      <Transition name="dropdown">
        <ul v-if="showDropdown" ref="listRef" class="dropdown">
          <li
            v-for="(item, i) in sortedList"
            :key="item.code"
            :class="{ active: i === activeIndex }"
            @mousedown.prevent="select(item)"
          >
            <span v-html="highlight(item.station)" class="station"></span>
            <span class="code">{{ item.code }}</span>
          </li>
        </ul>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.autocomplete {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  min-width: 0;
}

.marker {
  margin-top: 0.75rem;
  color: #fb923c;
  font-weight: 800;
  font-size: 1.25rem;
  user-select: none;
}

@media (min-width: 640px) {
  .marker { display: none; }
}

.input-wrapper {
  position: relative;
  width: 100%;
}

input {
  position: relative;
  width: 100%;
  height: 2.15rem;
  padding: 0.375rem 0.75rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  color: white;
  font-weight: 500;
  outline: none;
  transition: background 0.3s;
}

input:focus {
  background: rgba(255, 255, 255, 0.05);
}

input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

@media (min-width: 640px) {
  input::placeholder { color: transparent; }
  
  label {
    position: absolute;
    left: 0.75rem;
    top: 0.35rem;
    color: rgba(255, 255, 255, 0.5);
    font-size: 1rem;
    pointer-events: none;
    transition: all 0.2s;
  }

  input:focus + label,
  input:not(:placeholder-shown) + label {
    top: -0.4rem;
    font-size: 0.625rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: rgba(255, 255, 255, 0.4);
  }
}

@media (max-width: 639px) {
  label { display: none; }
}

.loader {
  position: absolute;
  right: 0.5rem;
  top: 0.5rem;
  color: rgba(255, 255, 255, 0.3);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.dropdown {
  position: absolute;
  z-index: 50;
  top: calc(100% + 4px);
  left: 0;
  width: 100%;
  max-height: 15rem;
  overflow-y: auto;
  background: #1a1e28;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  list-style: none;
  margin: 0;
  padding: 0;
}

.dropdown li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.15s;
}

.dropdown li:last-child {
  border-bottom: none;
}

.dropdown li:hover,
.dropdown li.active {
  background: rgba(255, 255, 255, 0.08);
  border-left: 2px solid #fb923c;
}

.station {
  font-weight: 500;
  color: white;
}

.station :deep(mark) {
  background: none;
  color: #fb923c;
  font-weight: 700;
}

.code {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.3);
}

/* Scrollbar */
.dropdown::-webkit-scrollbar { width: 6px; }
.dropdown::-webkit-scrollbar-track { background: transparent; }
.dropdown::-webkit-scrollbar-thumb { 
  background: rgba(255, 255, 255, 0.2); 
  border-radius: 20px; 
}

/* Анимация */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>