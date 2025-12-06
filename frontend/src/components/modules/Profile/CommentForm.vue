<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { Loader2 } from 'lucide-vue-next'
import type { User } from '@/scripts/useProfile'

const props = defineProps<{
  user: User
  viewer: User
  isOwner: boolean
  busy: boolean
}>()

const emit = defineEmits<{
  send: [text: string]
}>()

const text = ref('')
const inputRef = ref<HTMLInputElement>()
const cursorPosition = ref(0)

// Mention state
const showMentions = ref(false)
const mentionQuery = ref('')
const mentionStart = ref(0)
const mentionResults = ref<Array<{
  id: string
  username: string
  nickname: string
  photo: string
}>>([])
const selectedIndex = ref(0)
const searchLoading = ref(false)

// Debounce timer
let searchTimeout: ReturnType<typeof setTimeout>

// Парсинг текста для подсветки @mentions
const parsedText = computed(() => {
  if (!text.value) return []
  
  const parts: Array<{ text: string; isMention: boolean }> = []
  const regex = /(^|\s)(@\w+)/g
  let lastIndex = 0
  let match
  
  while ((match = regex.exec(text.value)) !== null) {
    // Текст до упоминания (включая пробел перед @)
    const beforeMention = text.value.slice(lastIndex, match.index)
    if (beforeMention) {
      parts.push({ text: beforeMention, isMention: false })
    }
    
    // Пробел перед @ (если есть)
    if (match[1]) {
      parts.push({ text: match[1], isMention: false })
    }
    
    // Само упоминание
    parts.push({ text: match[2], isMention: true })
    
    lastIndex = match.index + match[0].length
  }
  
  // Остаток текста
  if (lastIndex < text.value.length) {
    parts.push({ text: text.value.slice(lastIndex), isMention: false })
  }
  
  return parts
})

// Detect @mention while typing
const checkForMention = () => {
  const input = inputRef.value
  if (!input) return
  
  const pos = input.selectionStart || 0
  const textBeforeCursor = text.value.slice(0, pos)
  
  // Find last @ that starts a mention
  const lastAtIndex = textBeforeCursor.lastIndexOf('@')
  
  if (lastAtIndex === -1) {
    showMentions.value = false
    return
  }
  
  // Check if @ is at start or after a space
  const charBefore = textBeforeCursor[lastAtIndex - 1]
  if (lastAtIndex > 0 && charBefore !== ' ' && charBefore !== '\n') {
    showMentions.value = false
    return
  }
  
  // Get query after @
  const query = textBeforeCursor.slice(lastAtIndex + 1)
  
  // If there's a space after @, mention is complete
  if (query.includes(' ')) {
    showMentions.value = false
    return
  }
  
  mentionStart.value = lastAtIndex
  mentionQuery.value = query
  cursorPosition.value = pos
  
  if (query.length >= 1) {
    searchUsers(query)
  } else {
    showMentions.value = false
  }
}

// Search users API
const searchUsers = async (query: string) => {
  clearTimeout(searchTimeout)
  
  searchTimeout = setTimeout(async () => {
    searchLoading.value = true
    selectedIndex.value = 0
    
    try {
      const res = await fetch(`/api/search?who=${encodeURIComponent(query)}`)
      if (res.ok) {
        mentionResults.value = await res.json()
        showMentions.value = mentionResults.value.length > 0
      }
    } catch (e) {
      console.error('Search failed:', e)
      showMentions.value = false
    } finally {
      searchLoading.value = false
    }
  }, 200)
}

// Insert selected mention
const insertMention = (user: { username: string; nickname: string }) => {
  const before = text.value.slice(0, mentionStart.value)
  const after = text.value.slice(cursorPosition.value)
  
  text.value = `${before}@${user.username} ${after}`
  showMentions.value = false
  
  nextTick(() => {
    inputRef.value?.focus()
    const newPos = mentionStart.value + user.username.length + 2
    inputRef.value?.setSelectionRange(newPos, newPos)
  })
}

// Keyboard navigation
const handleKeydown = (e: KeyboardEvent) => {
  if (!showMentions.value) {
    if (e.key === 'Enter') {
      e.preventDefault()
      submit()
    }
    return
  }
  
  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      selectedIndex.value = Math.min(
        selectedIndex.value + 1, 
        mentionResults.value.length - 1
      )
      break
    case 'ArrowUp':
      e.preventDefault()
      selectedIndex.value = Math.max(selectedIndex.value - 1, 0)
      break
    case 'Enter':
    case 'Tab':
      e.preventDefault()
      if (mentionResults.value[selectedIndex.value]) {
        insertMention(mentionResults.value[selectedIndex.value])
      }
      break
    case 'Escape':
      showMentions.value = false
      break
  }
}

const submit = () => {
  if (text.value.trim() && !props.busy) {
    emit('send', text.value)
    text.value = ''
    showMentions.value = false
  }
}

// Синхронизация скролла между input и overlay
const handleScroll = () => {
  const input = inputRef.value
  const backdrop = document.querySelector('.input-backdrop') as HTMLElement
  if (input && backdrop) {
    backdrop.scrollLeft = input.scrollLeft
  }
}
</script>

<template>
  <div 
    class="bg-[#0a0a0a]/60 border border-white/5 rounded-2xl p-4 flex gap-4"
    @click.stop
  >
    <img 
      :src="isOwner ? user.photo : viewer.photo" 
      class="w-10 h-10 rounded-full object-cover shrink-0"
    >
    
    <div class="flex-1 relative mention-container">
      <!-- Input wrapper с overlay -->
      <div class="relative h-8">
        <!-- Backdrop с подсвеченным текстом -->
        <div 
          class="input-backdrop absolute inset-0 pointer-events-none text-sm whitespace-pre overflow-hidden flex items-center"
          aria-hidden="true"
        >
          <template v-for="(part, i) in parsedText" :key="i">
            <span :class="part.isMention ? 'text-purple-400' : 'text-transparent'">
              {{ part.text }}
            </span>
          </template>
          <!-- Невидимый символ чтобы сохранить высоту при пустом тексте -->
          <span v-if="!text" class="text-transparent">​</span>
        </div>
        
        <!-- Настоящий input поверх -->
        <input 
        ref="inputRef"
        v-model="text"
        :placeholder="isOwner ? 'Напишите на стене...' : 'Оставьте комментарий...'"
        class="absolute inset-0 w-full bg-transparent text-sm placeholder-neutral-600 focus:outline-none"
        :style="text ? 'color: transparent; -webkit-text-fill-color: transparent; caret-color: white;' : 'caret-color: white;'"
        @input="checkForMention"
        @keydown="handleKeydown"
        @click="checkForMention"
        @scroll="handleScroll"
        />
        
        <!-- Видимый текст поверх всего (но тоже pointer-events-none) -->
        <div 
          class="absolute inset-0 pointer-events-none text-sm whitespace-pre overflow-hidden flex items-center"
        >
          <template v-for="(part, i) in parsedText" :key="i">
            <span :class="part.isMention ? 'text-purple-400' : 'text-white'">
              {{ part.text }}
            </span>
          </template>
        </div>
      </div>
      
      <!-- Mention Dropdown -->
      <Transition
        enter-active-class="transition duration-150 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div 
          v-if="showMentions"
          class="absolute bottom-full left-0 mb-2 w-72 bg-[#151515] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-50"
        >
          <!-- Loading -->
          <div v-if="searchLoading" class="p-3 flex items-center gap-2 text-gray-400">
            <Loader2 :size="14" class="animate-spin" />
            <span class="text-xs">Поиск...</span>
          </div>
          
          <!-- Results -->
          <template v-else>
            <button
              v-for="(result, index) in mentionResults"
              :key="result.id"
              @click="insertMention(result)"
              @mouseenter="selectedIndex = index"
              class="w-full p-2.5 flex items-center gap-3 transition-colors text-left"
              :class="index === selectedIndex ? 'bg-white/10' : 'hover:bg-white/5'"
            >
              <img 
                :src="result.photo || '/default-avatar.png'" 
                class="w-8 h-8 rounded-full object-cover"
              >
              <div class="flex-1 min-w-0">
                <p class="text-sm text-white font-medium truncate">
                  {{ result.nickname }}
                </p>
                <p class="text-xs text-gray-500 truncate">
                  @{{ result.username }}
                </p>
              </div>
            </button>
            
            <!-- No results -->
            <div 
              v-if="mentionResults.length === 0 && !searchLoading"
              class="p-3 text-center text-gray-500 text-xs"
            >
              Пользователи не найдены
            </div>
          </template>
          
          <!-- Hint -->
          <div class="px-3 py-2 border-t border-white/5 bg-black/30">
            <p class="text-[10px] text-gray-600">
              ↑↓ навигация • Enter выбрать • Esc закрыть
            </p>
          </div>
        </div>
      </Transition>
      
      <div class="flex justify-end pt-2 border-t border-white/20 mt-2">
        <button 
          @click="submit" 
          :disabled="busy || !text.trim()"
          class="px-4 py-1.5 rounded-lg text-xs font-bold bg-gray-200/80 text-black hover:bg-gray-100/90 disabled:opacity-50 flex items-center gap-2"
        >
          <Loader2 v-if="busy" :size="12" class="animate-spin" />
          {{ busy ? '...' : 'Отправить' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Убираем выделение текста в overlay чтобы не мешало */
.input-backdrop {
  user-select: none;
}

/* Синхронизируем шрифт */
.input-backdrop,
.input-backdrop + input,
.input-backdrop ~ div {
  font-family: inherit;
  font-size: 0.875rem;
  line-height: 1.25rem;
  letter-spacing: normal;
}
</style>