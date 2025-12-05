<script setup>
import { watch, computed, ref, onMounted, onUnmounted, nextTick } from 'vue'
import StationsSelect from '../Main/StationsSelect.vue'
import SearchForm from '../Main/SearchForm.vue'
import { ArrowRight, ArrowRightLeft } from 'lucide-vue-next'
import SearchButton from '../Main/SearchButton.vue'

const props = defineProps({
  form: Array,
  activeInputIndex: Number,
  currentItems: Array,
  isLoading: Boolean,
  isSearchValid: Boolean,
  isCompact: Boolean
})

const emit = defineEmits(['update:form', 'search', 'select', 'swap', 'find'])

// Скролл для стики-хедера
const isScrolled = ref(false)
const handleScroll = () => isScrolled.value = window.scrollY > 80

onMounted(() => window.addEventListener('scroll', handleScroll))
onUnmounted(() => window.removeEventListener('scroll', handleScroll))

// ✅ Исправленный автопоиск
const lastSearchKey = ref('')

// Используем computed для более надёжного отслеживания
const searchKey = computed(() => {
  const fromCode = props.form[0]?.code || ''
  const toCode = props.form[1]?.code || ''
  return `${fromCode}-${toCode}`
})

// Флаг для предотвращения двойного срабатывания
const isAutoSearching = ref(false)

watch(searchKey, async (newKey, oldKey) => {
  // Пропускаем если ключ не изменился или уже ищем
  if (newKey === oldKey || isAutoSearching.value) return
  
  const fromCode = props.form[0]?.code
  const toCode = props.form[1]?.code
  
  // Проверяем все условия
  if (props.isCompact && fromCode && toCode && newKey !== lastSearchKey.value) {
    isAutoSearching.value = true
    lastSearchKey.value = newKey
    
    // Ждём следующий тик для корректной работы на мобильных
    await nextTick()
    
    // Небольшая задержка для закрытия клавиатуры на мобильных
    setTimeout(() => {
      emit('find')
      isAutoSearching.value = false
    }, 100)
  }
}, { flush: 'post' }) // ✅ flush: 'post' важен для мобильных

// Хелперы
const updateField = (i, name) => {
  const newForm = [...props.form]
  newForm[i] = { ...newForm[i], name }
  emit('update:form', newForm)
}

const getSuggestions = (i) => props.activeInputIndex === i ? props.currentItems : []
const getLoading = (i) => props.activeInputIndex === i && props.isLoading

const handleFind = () => {
  if (props.isSearchValid) {
    emit('find')
  }
}

const fields = [
  { index: 0, label: 'A', btnClass: 'bg-linear-to-br from-pink-400 to-orange-300 text-black text-2xl font-extrabold' },
  { index: 1, label: 'B', btnClass: 'bg-gray-600 text-white text-2xl font-extrabold' }
]
</script>

<template>
  <!-- Мобильный стики-хедер -->
  <div 
    class="fixed top-0 w-screen inset-x-0 z-60 bg-[#19191900] backdrop-blur-xl border-b border-white/10 px-4 py-2 transition-transform duration-300 md:hidden"
    :class="isScrolled ? 'translate-y-0' : '-translate-y-full'"
  >
    <div class="flex items-center gap-3">
      <template v-for="(field, idx) in fields" :key="field.label">
        <div class="flex-1 flex items-center bg-[#18181B] rounded-lg border border-white/10 h-8">
          <button @click="$emit('swap')" :class="['w-8 h-8 rounded-l-lg font-bold flex items-center justify-center', field.btnClass]">
            {{ field.label }}
          </button>
          <div class="flex-1 px-2">
            <StationsSelect
              :modelValue="form[field.index].name"
              @update:modelValue="updateField(field.index, $event)"
              :suggestions="getSuggestions(field.index)"
              :isLoading="getLoading(field.index)"
              compact
              class="text-sm"
              @search="q => $emit('search', q, field.index)"
              @select="s => $emit('select', s, field.index)"
            />
          </div>
        </div>
        <ArrowRight v-if="idx === 0" class="text-white/60 shrink-0" :size="16" />
      </template>
    </div>
  </div>

  <!-- Основной хедер -->
  <header 
    class="relative z-50 transition-all duration-300 w-full"
    :class="isCompact 
      ? 'md:sticky top-0 py-2 bg-[#FFFF0000] backdrop-blur-xl border-b border-white/10' 
      : 'py-6 md:py-8'"
  >
    <div class="max-w-4xl mx-auto px-2">

      <!-- Desktop -->
      <SearchForm
        class="hidden md:block"
        v-bind="props"
        :showTitle="!isCompact"
        :showGlow="!isCompact"
        @update:form="$emit('update:form', $event)"
        @search="(q, i) => $emit('search', q, i)"
        @select="(s, i) => $emit('select', s, i)"
        @swap="$emit('swap')"
        @find="$emit('find')"
      />

      <!-- Mobile -->
      <div class="md:hidden relative bg-[#18181B] rounded-xl border border-white/10 shadow-xl p-3">
        <!-- Свечение -->
        <div v-if="!isCompact" class="absolute inset-0 -z-10 scale-105 blur-3xl opacity-20 bg-linear-to-r from-purple-500 via-pink-500 to-orange-400 rounded-2xl" />

        <div class="flex flex-col gap-3">
          <template v-for="(field, idx) in fields" :key="field.label">
            <!-- Стрелка между полями -->
            <div v-if="idx === 1" class="flex justify-start -my-3">
              <button @click="$emit('swap')" class="relative left-1.5 p-0 rounded-lg">
                <ArrowRightLeft :size="20" class="text-white/80 rotate-90" />
              </button>
            </div>

            <!-- Поле -->
            <div class="flex items-center gap-1">
              <button
                @click="$emit('swap')"
                :class="['w-8 h-8 rounded-lg font-bold flex items-center justify-center shrink-0 transition-transform hover:scale-110 active:scale-95', field.btnClass]"
              >
                {{ field.label }}
              </button>
              <div class="flex-1 border-b-2 border-white/20">
                <StationsSelect
                  :modelValue="form[field.index].name"
                  @update:modelValue="updateField(field.index, $event)"
                  :code="form[field.index].code"
                  :label="form[field.index].label"
                  :suggestions="getSuggestions(field.index)"
                  :isLoading="getLoading(field.index)"
                  :compact="isCompact"
                  @search="q => $emit('search', q, field.index)"
                  @select="s => $emit('select', s, field.index)"
                />
              </div>
            </div>
          </template>
          
          <SearchButton v-if="!isCompact"
            :disabled="!isSearchValid" 
            @click="handleFind" 
          />
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
@media (max-width: 768px) {
  :deep(.stations-select-container label) { display: none }
  :deep(.stations-select-container input) {
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    font-size: 14px !important;
  }
}
</style>