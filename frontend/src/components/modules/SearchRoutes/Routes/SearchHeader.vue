<script setup>
import { watch, computed, ref } from 'vue'
import StationsSelect from '../Main/StationsSelect.vue'
import SearchButton from '../Main/SearchButton.vue'
import { ArrowRightLeft } from 'lucide-vue-next'

const props = defineProps({
  form: Array,
  activeInputIndex: Number,
  currentItems: Array,
  isLoading: Boolean,
  isSearchValid: Boolean,
  isCompact: Boolean
})

const emit = defineEmits(['update:form', 'search', 'select', 'swap', 'find'])

const updateField = (index, value) => {
  const newForm = [...props.form]
  newForm[index] = { ...newForm[index], name: value }
  emit('update:form', newForm)
}

// Уникальный ключ текущего поиска (для предотвращения дублей)
const lastSearchKey = ref('')

// Комбинация выбранных станций
const searchKey = computed(() => 
  `${props.form[0]?.code || ''}-${props.form[1]?.code || ''}`
)

// Автопоиск когда обе станции выбраны
watch(searchKey, (newKey) => {
  const bothSelected = props.form[0]?.code && props.form[1]?.code
  const isNewSearch = newKey !== lastSearchKey.value
  
  if (bothSelected && isNewSearch) {
    lastSearchKey.value = newKey
    // Небольшая задержка для плавности
    setTimeout(() => {
      emit('find')
    }, 10)
  }
})
</script>

<template>
  <header 
    :class="[
      'sticky top-0 z-50 transition-all duration-300',
      isCompact ? 'py-3 bg-[#0a0a0b]/95 backdrop-blur-xl border-b border-white/10' : 'py-6 md:py-8'
    ]"
  >
    <div class="max-w-6xl mx-auto px-4">
      <!-- Заголовок (Скрыт в компакте) -->
      <div 
        v-if="!isCompact" 
        class="text-center mb-6 md:mb-8"
      >
        <h1 class="text-2xl md:text-4xl font-extrabold text-white tracking-tight">
          Куда отправимся сегодня?
        </h1>
        <p class="mt-2 text-sm md:text-base text-white/60 font-medium">
          Найдите лучшие маршруты, расписание и актуальные рейсы.
        </p>
      </div>

      <!-- Основной контейнер поиска -->
      <div 
        :class="[
          'relative bg-[#18181B] rounded-xl border border-white/10 shadow-2xl transition-all duration-300',
          isCompact ? 'max-w-4xl mx-auto p-1' : 'w-full md:w-4/6 mx-auto p-2 md:p-2'
        ]"
      >
        <!-- Фоновое свечение (Десктоп) -->
        <div 
          v-if="!isCompact"
          class="absolute inset-0 -z-1 scale-x-105 scale-y-110 blur-3xl opacity-20 bg-linear-to-bl from-purple-500 via-pink-500 to-orange-400 rounded-2xl"
        />

        <div class="relative z-1">
          <div class="flex flex-col md:flex-row gap-3 md:gap-2 items-stretch md:items-center">
            
            <!-- Поле ОТКУДА (A) -->
            <div class="flex items-center gap-1 flex-1 relative group">
              <!-- Индикатор A (Мобильный) -->
              <div class="md:hidden shrink-0 flex flex-col items-center gap-1">
                <div class="w-8 h-8 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-purple-400 font-bold text-4xs shadow-lg">
                  A
                </div>
              </div>

              <!-- Инпут -->
              <div class="w-full">
                <StationsSelect
                  :modelValue="form[0].name"
                  @update:modelValue="updateField(0, $event)"
                  :code="form[0].code"
                  :label="form[0].label"
                  :suggestions="activeInputIndex === 0 ? currentItems : []"
                  :isLoading="activeInputIndex === 0 && isLoading"
                  :compact="isCompact"
                  class="w-full"
                  @search="(q) => $emit('search', q, 0)"
                  @select="(s) => $emit('select', s, 0)"
                />
              </div>
            </div>

            <!-- Кнопка Swap (ДЕСКТОП ВЕРСИЯ) -->
            <button
              type="button"
              @click="$emit('swap')"
              class="hidden md:flex shrink-0 p-2.5 rounded-xl bg-white/5 hover:bg-white/10 
                     text-white/50 hover:text-white transition-all duration-200
                     hover:rotate-180 active:scale-90 border border-transparent hover:border-white/10"
              title="Поменять местами"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
            </button>

            <!-- Поле КУДА (B) + Кнопка Swap (МОБИЛЬНАЯ ВЕРСИЯ) -->
            <div class="flex items-center gap-3 flex-1">
              
              <!-- Контейнер Swap + B (Мобильный) -->
              <div class="md:hidden shrink-0 flex items-center justify-center w-8 h-8 relative z-10">
                 <!-- Кнопка Swap (Мобильная) -->
                 <button
                  type="button"
                  @click="$emit('swap')"
                  class="absolute w-8 h-8 flex items-center justify-center rounded-lg bg-[#27272a] border border-white/10 text-white/60 active:scale-90 active:text-white transition-all z-20 shadow-xl"
                >
                  <ArrowRightLeft :stroke-width="2" :size="20" class="text-white/60 rotate-90" />
                </button>
              </div>

               <!-- Реальный индикатор B (правее кнопки swap) -->
               <div class="md:hidden shrink-0 w-8 h-8 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-orange-400 font-bold text-4xs">
                  B
               </div>

              <!-- Инпут -->
              <div class="w-full relative">
                <StationsSelect
                  :modelValue="form[1].name"
                  @update:modelValue="updateField(1, $event)"
                  :code="form[1].code"
                  :label="form[1].label"
                  :suggestions="activeInputIndex === 1 ? currentItems : []"
                  :isLoading="activeInputIndex === 1 && isLoading"
                  :compact="isCompact"
                  class="w-full"
                  @search="(q) => $emit('search', q, 1)"
                  @select="(s) => $emit('select', s, 1)"
                />
              </div>
            </div>

            <!-- Кнопка поиска (ТОЛЬКО в обычном режиме) -->
            <div v-if="!isCompact" class="pt-2 md:pt-0">
              <SearchButton
                :disabled="!isSearchValid" 
                :compact="isCompact"
                @click="$emit('find')" 
              />
            </div>
            
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
@media (max-width: 768px) {
  :deep(label) {
    display: none !important;
  }
  :deep(.stations-select-container) {
    margin-top: 0;
  }
}
</style>