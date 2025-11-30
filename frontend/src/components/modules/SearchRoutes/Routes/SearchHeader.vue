<script setup>
import { watch } from 'vue' // Импортируем watch
import StationsSelect from '../Main/StationsSelect.vue'
// SearchButton больше не нужен

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
  // При ручном вводе сбрасываем код, чтобы поиск не срабатывал на полуслове
  // Код установится только при событии @select в родителе
  newForm[index] = { ...newForm[index], name: value }
  emit('update:form', newForm)
}

// Автоматический поиск при наличии кодов станций
watch(
  () => props.form,
  (newForm) => {
    // Проверяем, что оба кода существуют и они не пустые
    if (newForm[0]?.code && newForm[1]?.code) {
      emit('find')
    }
  },
  { deep: true }
)
</script>

<template>
  <header 
    :class="[
      'sticky top-0 z-50 transition-all duration-300',
      isCompact ? 'py-3 bg-[#0a0a0b]/95 backdrop-blur-xl border-b border-white/10' : 'py-8'
    ]"
  >
    <div class="max-w-6xl mx-auto px-4">
      <div 
        v-if="!isCompact" 
        class="text-center mb-6"
      >
        <h1 class="text-2xl md:text-4xl font-extrabold text-white">
          Куда отправимся сегодня?
        </h1>
        <p class="mt-1 text-sm md:text-base text-white/60">
          Найдите лучшие маршруты, расписание и актуальные рейсы.
        </p>
      </div>

      <div 
        :class="[
          'relative p-2 bg-[#18181B] rounded-xl border border-white/10 shadow-2xl',
          isCompact ? 'max-w-4xl mx-auto' : 'w-full md:w-4/6 mx-auto'
        ]"
      >
        <div 
          v-if="!isCompact"
          class="absolute inset-0 -z-1 scale-x-105 scale-y-110 blur-3xl opacity-20 bg-linear-to-bl from-purple-500 via-pink-500 to-orange-400"
        />

        <div class="relative z-1">
          <!-- Основной контейнер: колонка на мобильном, ряд на десктопе -->
          <div class="flex flex-col md:flex-row gap-2 items-stretch md:items-center">
            
            <!-- Инпут ОТКУДА (занимает всю ширину на моб, часть на десктопе) -->
            <StationsSelect
              :modelValue="form[0].name"
              @update:modelValue="updateField(0, $event)"
              :code="form[0].code"
              :label="form[0].label"
              :suggestions="activeInputIndex === 0 ? currentItems : []"
              :isLoading="activeInputIndex === 0 && isLoading"
              :compact="isCompact"
              marker="A"
              class="w-full md:flex-1"
              @search="(q) => $emit('search', q, 0)"
              @select="(s) => $emit('select', s, 0)"
            />

            <!-- Обертка для Кнопки и Инпута КУДА -->
            <!-- На мобильном: flex-row (кнопка слева от инпута) -->
            <!-- На десктопе: contents (обертка исчезает, элементы встраиваются в общий ряд) -->
            <div class="flex flex-row gap-2 items-center md:contents">
              
              <button
                type="button"
                @click="$emit('swap')"
                class="shrink-0 p-2 h-[46px] w-[46px] flex items-center justify-center rounded-lg bg-white/5 hover:bg-white/10 
                       text-white/60 hover:text-white transition-all duration-200
                       hover:rotate-180 active:scale-90 mt-1 md:mt-0 border border-white/5 md:border-none"
                title="Поменять местами"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
              </button>

              <!-- Инпут КУДА -->
              <StationsSelect
                :modelValue="form[1].name"
                @update:modelValue="updateField(1, $event)"
                :code="form[1].code"
                :label="form[1].label"
                :suggestions="activeInputIndex === 1 ? currentItems : []"
                :isLoading="activeInputIndex === 1 && isLoading"
                :compact="isCompact"
                marker="B"
                class="flex-1 w-full"
                @search="(q) => $emit('search', q, 1)"
                @select="(s) => $emit('select', s, 1)"
              />
            </div>

            <!-- Кнопка поиска удалена, поиск автоматический -->
            
          </div>
        </div>
      </div>
    </div>
  </header>
</template>