<script setup>
import RouteCard from './RouteCard.vue'

defineProps({
  routes: Array,
  info: Object,
  isLoading: Boolean
})

const emit = defineEmits(['select'])
</script>

<template>
  <div class="max-w-4xl mx-auto pb-8">
    <!-- Заголовок с информацией о маршруте -->
    <div v-if="info?.origin" class="mb-6">
      <h2 class="text-xl md:text-2xl font-bold text-white flex items-center gap-3">
        <span>{{ info.origin }}</span>
        <svg class="w-5 h-5 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
        </svg>
        <span>{{ info.destination }}</span>
      </h2>
      <p class="text-white/50 text-sm mt-1">
        {{ isLoading ? 'Загрузка...' : `Найдено ${routes?.length || 0} рейсов` }}
      </p>
    </div>

    <!-- Скелетон загрузки -->
    <div v-if="isLoading" class="space-y-4">
      <div 
        v-for="i in 5" 
        :key="i"
        class="h-28 bg-white/5 rounded-xl animate-pulse"
      />
    </div>

    <!-- Пустой результат -->
    <div 
      v-else-if="!routes?.length" 
      class="text-center py-16"
    >
      <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center">
        <svg class="w-8 h-8 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-white/70">Рейсы не найдены</h3>
      <p class="text-white/40 text-sm mt-1">Попробуйте изменить параметры поиска</p>
    </div>

    <!-- Список маршрутов -->
    <div v-else class="space-y-3">
      <RouteCard
        v-for="train in routes"
        :key="train.number + train.ts_dep"
        :train="train"
        @click="$emit('select', train)"
      />
    </div>
  </div>
</template>