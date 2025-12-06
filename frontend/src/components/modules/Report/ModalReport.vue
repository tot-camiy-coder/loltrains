<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { X, AlertTriangle, Loader2, ChevronDown, Check, ArrowLeft } from 'lucide-vue-next'

export interface ReportData {
  type: 'profile' | 'comment'
  targetUsername: string
  commentId?: string | number
  commentIndex?: number
}

export interface ReportPayload {
  reasonId: string
  reasonLabel: string
  details: string
  data: ReportData
}

const props = defineProps<{
  visible: boolean
  data: ReportData | null
  busy?: boolean
}>()

const emit = defineEmits<{
  close: []
  submit: [payload: ReportPayload]
}>()

// Предустановленные причины
const REASONS = [
  { id: 'spam', label: 'Спам', icon: '📧', description: 'Рекламные сообщения, ссылки' },
  { id: 'offensive', label: 'Оскорбление', icon: '🤬', description: 'Оскорбительные высказывания' },
  { id: 'harassment', label: 'Травля / Преследование', icon: '😠', description: 'Систематическое преследование' },
  { id: 'fake', label: 'Фейковый аккаунт', icon: '🎭', description: 'Выдаёт себя за другого человека' },
  { id: 'nsfw', label: 'Неприемлемый контент (18+)', icon: '🔞', description: 'Контент для взрослых' },
  { id: 'violence', label: 'Призывы к насилию', icon: '⚠️', description: 'Угрозы, призывы к насилию' },
  { id: 'other', label: 'Другое', icon: '📝', description: 'Другая причина' },
] as const

type ReasonId = typeof REASONS[number]['id']

// Состояние
const step = ref<1 | 2>(1) // 1 = выбор причины, 2 = ввод деталей
const selectedReason = ref<ReasonId | null>(null)
const details = ref('')

// Reset on open
watch(() => props.visible, (v) => {
  if (v) {
    step.value = 1
    selectedReason.value = null
    details.value = ''
  }
})

const selectedReasonData = computed(() => {
  return REASONS.find(r => r.id === selectedReason.value)
})

const canSubmit = computed(() => {
  if (!selectedReason.value) return false
  // Для "Другое" детали обязательны
  if (selectedReason.value === 'other' && !details.value.trim()) return false
  return true
})

const selectReason = (id: ReasonId) => {
  selectedReason.value = id
  step.value = 2
}

const goBack = () => {
  step.value = 1
}

const submit = () => {
  if (!canSubmit.value || !props.data || !selectedReasonData.value) return
  
  emit('submit', {
    reasonId: selectedReason.value!,
    reasonLabel: selectedReasonData.value.label,
    details: details.value.trim(),
    data: props.data
  })
}

const reportTypeLabel = computed(() => {
  return props.data?.type === 'comment' ? 'комментарий' : 'профиль'
})

const detailsPlaceholder = computed(() => {
  if (selectedReason.value === 'other') {
    return 'Опишите причину жалобы подробнее... (обязательно)'
  }
  return 'Добавьте подробности, если необходимо... (опционально)'
})
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div 
        v-if="visible" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="emit('close')"
      >
        <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" />
        
        <div class="bg-[#0f0f0f] border border-white/10 w-full max-w-md rounded-2xl shadow-2xl relative z-10 flex flex-col overflow-hidden">
          <!-- Header -->
          <div class="p-4 border-b border-white/5 flex justify-between items-center bg-[#151515]">
            <div class="flex items-center gap-2">
              <!-- Back button on step 2 -->
              <button 
                v-if="step === 2"
                @click="goBack"
                class="w-8 h-8 rounded-full hover:bg-white/10 flex items-center justify-center text-gray-400 hover:text-white transition-colors"
              >
                <ArrowLeft :size="18" />
              </button>
              
              <span class="text-white font-bold text-lg flex items-center gap-2">
                <AlertTriangle :size="18" class="text-red-500" />
                <span v-if="step === 1">Жалоба на {{ reportTypeLabel }}</span>
                <span v-else>Детали жалобы</span>
              </span>
            </div>
            
            <button 
              @click="emit('close')"
              class="w-8 h-8 rounded-full hover:bg-white/10 flex items-center justify-center text-gray-400 hover:text-white transition-colors"
            >
              <X :size="18" />
            </button>
          </div>

          <!-- Content -->
          <div class="flex-1 overflow-hidden">
            <!-- Step 1: Choose reason -->
            <Transition name="slide-left" mode="out-in">
              <div v-if="step === 1" key="step1" class="p-4">
                <p class="text-gray-400 text-sm mb-4 px-1">
                  Выберите причину жалобы:
                </p>
                
                <div class="space-y-1">
                  <button
                    v-for="reason in REASONS"
                    :key="reason.id"
                    @click="selectReason(reason.id)"
                    class="w-full px-4 py-3.5 rounded-xl text-left flex items-center gap-3 hover:bg-white/5 transition-all group active:scale-[0.98]"
                  >
                    <span class="text-2xl">{{ reason.icon }}</span>
                    <div class="flex-1 min-w-0">
                      <div class="text-white font-medium">{{ reason.label }}</div>
                      <div class="text-gray-500 text-xs truncate">{{ reason.description }}</div>
                    </div>
                    <ChevronDown 
                      :size="16" 
                      class="text-gray-600 -rotate-90 opacity-0 group-hover:opacity-100 transition-opacity" 
                    />
                  </button>
                </div>
              </div>

              <!-- Step 2: Add details -->
              <div v-else key="step2" class="p-6 space-y-4">
                <!-- Selected reason card -->
                <div class="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3">
                  <span class="text-2xl">{{ selectedReasonData?.icon }}</span>
                  <div>
                    <div class="text-white font-medium">{{ selectedReasonData?.label }}</div>
                    <div class="text-red-400/70 text-xs">Выбранная причина</div>
                  </div>
                  <Check :size="18" class="text-red-500 ml-auto" />
                </div>

                <!-- Debug info -->
                <div v-if="data?.type === 'comment'" class="text-xs text-gray-600 bg-white/5 rounded-lg p-2">
                  ID комментария: <span class="text-gray-400 font-mono">{{ data.commentId }}</span>
                </div>

                <!-- Details textarea -->
                <div class="space-y-2">
                  <label class="text-sm text-gray-400 flex items-center gap-1">
                    Дополнительная информация
                    <span v-if="selectedReason === 'other'" class="text-red-500">*</span>
                  </label>
                  <textarea 
                    v-model="details"
                    rows="4"
                    class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-red-500/50 resize-none transition-colors placeholder:text-gray-600"
                    :placeholder="detailsPlaceholder"
                    autofocus
                  />
                  <p class="text-xs text-gray-600">
                    {{ details.length }} / 500 символов
                  </p>
                </div>

                <!-- Info text -->
                <p class="text-xs text-gray-500 bg-white/5 rounded-lg p-3">
                  💡 Чем подробнее вы опишете нарушение, тем быстрее мы сможем рассмотреть вашу жалобу.
                </p>
              </div>
            </Transition>
          </div>

          <!-- Footer -->
          <div class="p-4 bg-[#151515] border-t border-white/5 flex justify-between items-center gap-3">
            <!-- Step indicator -->
            <div class="flex items-center gap-2">
              <div 
                class="w-2 h-2 rounded-full transition-colors"
                :class="step === 1 ? 'bg-red-500' : 'bg-gray-600'"
              />
              <div 
                class="w-2 h-2 rounded-full transition-colors"
                :class="step === 2 ? 'bg-red-500' : 'bg-gray-600'"
              />
            </div>

            <div class="flex gap-3">
              <button 
                @click="emit('close')"
                class="px-4 py-2 rounded-xl text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
              >
                Отмена
              </button>
              
              <button 
                v-if="step === 2"
                @click="submit"
                :disabled="busy || !canSubmit"
                class="px-6 py-2 rounded-xl font-bold text-sm bg-red-600 text-white disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 hover:bg-red-500 active:scale-95 transition-all"
              >
                <Loader2 v-if="busy" :size="14" class="animate-spin" />
                {{ busy ? 'Отправка...' : 'Отправить жалобу' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { 
  transition: opacity .3s, transform .3s cubic-bezier(.34,1.56,.64,1) 
}
.modal-enter-from, .modal-leave-to { 
  opacity: 0; 
  transform: scale(.95) translateY(10px) 
}

/* Slide transitions for steps */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.25s ease-out;
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>