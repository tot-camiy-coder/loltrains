<script setup lang="ts">
import { ref, computed } from 'vue'
import { Settings, Flag, ThumbsUp, ThumbsDown, Calendar, Copy, Check, Loader2 } from 'lucide-vue-next'
import { roleClass, parseText } from '@/scripts/helpers'
import type { User } from '@/scripts/useProfile'

const props = defineProps<{
  user: User
  viewer: User | null
  isOwner: boolean
  canVote: boolean
  myVote?: number
  voting: boolean
}>()

const emit = defineEmits<{
  vote: [action: number]
  openSettings: []
  openReport: []
}>()

const copied = ref(false)

// Список запрещённых слов (базовый, можно расширить)
const badWords = [
  // Русский мат
  'хуй', 'хуя', 'хуе', 'хуё', 'хую', 'хуи',
  'пизд', 'пізд',
  'блять', 'блядь', 'бляд', 'блят',
  'ебат', 'ебан', 'ебал', 'ебну', 'ебёт', 'ебет', 'ебуч', 'ёб', 'еб',
  'сука', 'сучк', 'сучар',
  'мудак', 'мудач', 'мудил',
  'пидор', 'пидар', 'педик',
  'залуп', 'шлюх', 'давалк',
  'трах', 'нахуй', 'нахуя', 'похуй', 'похер',
  'жопа', 'жоп',
  'срать', 'срал', 'насрать', 'засран', 'обосра', 'высра', 'просра',
  'говно', 'говн', 'гавно', 'гавн',
  'дерьм', 'дерьмо',
  'чмо', 'чмош',
  'уёб', 'уеб', 'долбо', 'долбаё', 'долбае',
  'fuck', 'shit', 'bitch', 'asshole', 'dick', 'cock', 'pussy', 'whore', 'slut',
  'nigger', 'nigga', 'faggot', 'cunt',
]

// Функция цензуры текста - возвращает массив сегментов
interface TextSegment {
  text: string
  censored: boolean
}

const censorText = (text: string): TextSegment[] => {
  if (!text) return [{ text: '', censored: false }]
  
  // Создаём регулярку для поиска плохих слов
  const pattern = new RegExp(
    `(${badWords.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`,
    'gi'
  )
  
  const segments: TextSegment[] = []
  let lastIndex = 0
  let match
  
  while ((match = pattern.exec(text)) !== null) {
    // Добавляем текст до матча
    if (match.index > lastIndex) {
      segments.push({
        text: text.slice(lastIndex, match.index),
        censored: false
      })
    }
    
    // Добавляем зацензуренное слово
    segments.push({
      text: match[0],
      censored: true
    })
    
    lastIndex = pattern.lastIndex
  }
  
  // Добавляем остаток текста
  if (lastIndex < text.length) {
    segments.push({
      text: text.slice(lastIndex),
      censored: false
    })
  }
  
  return segments.length ? segments : [{ text, censored: false }]
}

// Цензурированное имя
const censoredNickname = computed(() => censorText(props.user.nickname))

// Функция для парсинга текста с цензурой
const parseTextWithCensor = (text: string) => {
  const parts = parseText(text)
  return parts.map(part => {
    if (part.startsWith('@')) {
      return { type: 'mention' as const, text: part }
    }
    return { type: 'text' as const, segments: censorText(part) }
  })
}

const copyLink = async () => {
  const link = `${window.location.origin}${window.location.pathname}?user=${props.user.username}`
  await navigator.clipboard.writeText(link)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}
</script>

<template>
  <div class="bg-[#0a0a0a]/60 border border-white/5 rounded-3xl shadow-2xl relative backdrop-blur-sm">
    <!-- Banner -->
    <div 
      class="h-48 md:h-[400px] bg-cover bg-center rounded-t-2xl relative" 
      :style="{ backgroundImage: `url(${user.banner})` }"
    >
      <div class="absolute inset-0 bg-linear-to-b from-transparent to-[#0a0a0a]/80" />
    </div>

    <div class="px-4 pb-6 relative flex flex-col md:flex-row gap-6 -mt-16 md:-mt-20 items-center md:items-start">
      <!-- Avatar -->
      <img 
        :src="user.photo || '/img/default-avatar.png'" 
        class="w-32 h-32 md:w-40 md:h-40 rounded-full border-4 border-[#0a0a0a] bg-[#151515] object-cover shadow-2xl z-10"
      >

      <div class="flex-1 w-full text-center md:text-left pt-2 md:pt-24">
        <div class="flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <h1 class="text-3xl font-bold text-white tracking-tight break-all">
              <!-- Имя с цензурой -->
              <template v-for="(segment, i) in censoredNickname" :key="i">
                <span 
                  v-if="segment.censored" 
                  class="censored-word"
                  :title="'Цензура'"
                >
                  <span class="censored-text">{{ segment.text }}</span>
                </span>
                <template v-else>{{ segment.text }}</template>
              </template>
              
              <!-- Username with copy -->
              <span 
                class="text-gray-500/60 text-lg font-normal md:-ml-2 block md:inline relative group cursor-pointer" 
                @click="copyLink"
              >
                @{{ user.username }}
                
                <!-- Tooltip -->
                <span class="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 rounded bg-white/10 text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none flex items-center gap-1">
                  <Check v-if="copied" :size="12" class="text-green-400" />
                  <Copy v-else :size="12" />
                  {{ copied ? 'Скопировано!' : 'Копировать ссылку' }}
                </span>
              </span>
            </h1>

            <div class="flex flex-wrap justify-center md:justify-start gap-3 mt-3 text-xs items-center font-medium">
              <!-- Role -->
              <span 
                v-if="user.role && roleClass[user.role]" 
                :class="`px-2.5 py-0.5 rounded border uppercase tracking-wider ${roleClass[user.role]}`"
              >
                {{ user.role }}
              </span>

              <!-- Reputation -->
              <div class="px-1 py-0.5 bg-white/5 rounded-full flex items-center border border-white/5 relative select-none">
                <div 
                  v-if="voting" 
                  class="absolute inset-0 bg-[#0a0a0a]/80 flex items-center justify-center z-20 rounded-full"
                >
                  <Loader2 :size="12" class="text-white animate-spin" />
                </div>

                <button 
                  @click="emit('vote', 1)" 
                  :disabled="!canVote || voting"
                  :class="[
                    'flex items-center gap-1.5 px-3 py-1 transition-all',
                    myVote === 1 ? 'text-green-400' : 'text-gray-400',
                    canVote ? 'hover:text-green-400 active:scale-90' : 'opacity-80'
                  ]"
                >
                  <ThumbsUp :size="12" :class="myVote === 1 ? 'fill-current' : ''" />
                  <span>{{ user.reputation?.likes || 0 }}</span>
                </button>

                <div class="w-px bg-white/10 h-4" />

                <button 
                  @click="emit('vote', -1)" 
                  :disabled="!canVote || voting"
                  :class="[
                    'flex items-center gap-1.5 px-3 py-1 transition-all',
                    myVote === -1 ? 'text-red-400' : 'text-gray-400',
                    canVote ? 'hover:text-red-400 hover:bg-white/5 active:scale-90' : 'opacity-80'
                  ]"
                >
                  <ThumbsDown :size="12" :class="myVote === -1 ? 'fill-current' : ''" />
                  <span>{{ user.reputation?.dislikes || 0 }}</span>
                </button>
              </div>

              <span class="text-gray-500/60 flex items-center gap-1.5">
                <Calendar :size="12" /> {{ user.date_created }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2">
            <button 
              v-if="isOwner" 
              @click="emit('openSettings')"
              class="px-4 py-2 rounded-xl border border-white/10 hover:bg-white/10 transition-all active:scale-95 text-sm bg-white/5 text-gray-200 flex items-center gap-2"
            >
              <Settings :size="16" class="text-purple-400" />
              Настройки
            </button>
            <button 
              v-else-if="viewer" 
              @click="emit('openReport')"
              class="px-4 py-2 rounded-xl border border-red-500/10 hover:bg-red-500/10 hover:text-red-400 transition-all active:scale-95 text-sm text-gray-500"
            >
              <Flag :size="14" />
            </button>
          </div>
        </div>

        <!-- Description с цензурой -->
        <div 
          v-if="user.description" 
          class="mt-6 text-sm text-gray-300 leading-relaxed bg-white/2 border border-white/5 p-4 rounded-xl whitespace-pre-wrap"
        >
          <template v-for="(part, i) in parseTextWithCensor(user.description)" :key="i">
            <RouterLink 
              v-if="part.type === 'mention'" 
              :to="`?user=${part.text.slice(1)}`" 
              class="text-purple-400 hover:underline"
            >
              {{ part.text }}
            </RouterLink>
            <template v-else>
              <template v-for="(segment, j) in part.segments" :key="j">
                <span 
                  v-if="segment.censored" 
                  class="censored-word"
                  :title="'Цензура'"
                >
                  <span class="censored-text">{{ segment.text }}</span>
                </span>
                <template v-else>{{ segment.text }}</template>
              </template>
            </template>
          </template>
        </div>
        <div v-else class="mt-6 text-sm text-gray-600 italic">
          Пользователь не добавил описание.
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.censored-word {
  position: relative;
  display: inline-block;
  background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 4px;
  padding: 0 4px;
  margin: 0 1px;
  box-shadow: 
    0 0 8px rgba(239, 68, 68, 0.2),
    inset 0 0 12px rgba(0, 0, 0, 0.5);
  cursor: not-allowed;
  transition: all 0.2s ease;
}

.censored-word:hover {
  border-color: rgba(239, 68, 68, 0.5);
  box-shadow: 
    0 0 12px rgba(239, 68, 68, 0.3),
    inset 0 0 12px rgba(0, 0, 0, 0.5);
}

.censored-word::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 2px,
    rgba(239, 68, 68, 0.05) 2px,
    rgba(239, 68, 68, 0.05) 4px
  );
  border-radius: 3px;
  pointer-events: none;
}

.censored-text {
  color: #ef4444;
  font-weight: 600;
  text-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
  filter: blur(4px);
  user-select: none;
  transition: filter 0.3s ease;
}

/* Опционально: показать при долгом наведении */
.censored-word:hover .censored-text {
  filter: blur(3px);
}

/* Иконка предупреждения */
.censored-word::after {
  content: 'нет доступа';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 8px;
  font-weight: bold;
  color: rgba(239, 68, 68, 0.8);
  text-shadow: 0 0 4px rgba(0, 0, 0, 0.8);
  pointer-events: none;
  opacity: 0.8;
}
</style>