<script setup>
import StationsSelect from '../Main/StationsSelect.vue'
import SearchButton from '../Main/SearchButton.vue'
import { ArrowRightLeft } from 'lucide-vue-next'

const props = defineProps({
  form: {
    type: Array,
    required: true
  },
  activeInputIndex: Number,
  currentItems: Array,
  isLoading: Boolean,
  isSearchValid: Boolean,
  isCompact: {
    type: Boolean,
    default: true
  },
  showTitle: {
    type: Boolean,
    default: false
  },
  showGlow: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:form', 'search', 'select', 'swap', 'find'])

const updateField = (index, value) => {
  const newForm = [...props.form]
  newForm[index] = { ...newForm[index], name: value }
  emit('update:form', newForm)
}
</script>

<template>
  <div class="w-full">
    <!-- Поисковая форма -->
    <div 
      class="relative bg-[#18181B] rounded-xl border border-white/10 shadow-xl p-1"
      :class="isCompact ? 'max-w-3xl mx-auto' : 'max-w-3xl mx-auto'"
    >
      <!-- Фоновое свечение -->
      <div 
        v-if="showGlow" 
        class="absolute inset-0 -z-10 scale-105 blur-3xl opacity-20 bg-linear-to-r from-purple-500 via-pink-500 to-orange-400 rounded-2xl" 
      />

      <div class="relative">
        <div class="flex items-center gap-2">
          <!-- Откуда -->
          <div class="flex-1 pr-2">
            <StationsSelect
              :modelValue="form[0].name"
              @update:modelValue="updateField(0, $event)"
              :code="form[0].code"
              :label="form[0].label"
              :suggestions="activeInputIndex === 0 ? currentItems : []"
              :isLoading="activeInputIndex === 0 && isLoading"
              :compact="isCompact"
              @search="q => $emit('search', q, 0)"
              @select="s => $emit('select', s, 0)"
            />
          </div>

          <!-- Кнопка обмена -->
          <button
            @click="$emit('swap')"
            class="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors shrink-0"
          >
            <ArrowRightLeft 
              :stroke-width="2" 
              :size="20" 
              class="text-white/80" 
            />
          </button>

          <!-- Куда -->
          <div class="flex-1 pr-2">
            <StationsSelect
              :modelValue="form[1].name"
              @update:modelValue="updateField(1, $event)"
              :code="form[1].code"
              :label="form[1].label"
              :suggestions="activeInputIndex === 1 ? currentItems : []"
              :isLoading="activeInputIndex === 1 && isLoading"
              :compact="isCompact"
              @search="q => $emit('search', q, 1)"
              @select="s => $emit('select', s, 1)"
            />
          </div>

          <!-- Кнопка поиска -->
          <SearchButton class="max-w-[100px]"
            :disabled="!isSearchValid" 
            :compact="isCompact"
            @click="$emit('find')" 
          />
        </div>
      </div>
    </div>
  </div>
</template>