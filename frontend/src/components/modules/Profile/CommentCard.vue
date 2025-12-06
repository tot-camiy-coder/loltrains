<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Flag } from 'lucide-vue-next'
import { parseText, relTime } from '@/scripts/helpers'
import type { Comment, User } from '@/scripts/useProfile'

const props = defineProps<{
  comment: Comment
  viewer: User | null
  now: number
}>()

const emit = defineEmits<{
  report: [comment: Comment]
}>()

const router = useRouter()

const canReport = props.viewer && props.comment.sender?.username !== props.viewer.username
</script>

<template>
  <div class="group relative bg-[#0a0a0a] border border-white/5 rounded-xl p-4 flex gap-4 hover:border-white/10 transition-colors">
    <!-- Report button -->
    <button 
      v-if="canReport"
      @click="emit('report', comment)" 
      class="absolute top-3 right-3 text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all p-1"
      title="Пожаловаться"
    >
      <Flag :size="12" />
    </button>

    <!-- Avatar -->
    <img 
      :src="comment.sender?.photo" 
      @click="router.push(`?user=${comment.sender?.username}`)"
      class="w-10 h-10 rounded-full object-cover cursor-pointer border border-white/5 hover:border-purple-500/50 transition-colors"
    >

    <div class="flex-1 text-sm pr-4">
      <div class="flex justify-between items-baseline mb-1">
        <span 
          class="font-bold text-gray-200 hover:text-purple-400 cursor-pointer transition-colors" 
          @click="router.push(`?user=${comment.sender?.username}`)"
        >
          {{ comment.sender?.nickname }}
        </span>
        <span class="text-[10px] text-gray-600 font-mono">
          {{ relTime(comment.timestamp, now) }}
        </span>
      </div>

      <p class="text-gray-400 whitespace-pre-wrap wrap-break-word">
        <template v-for="(part, i) in parseText(comment.body)" :key="i">
          <RouterLink 
            v-if="part.startsWith('@')" 
            :to="`?user=${part.slice(1)}`" 
            class="text-purple-400 hover:underline"
          >
            {{ part }}
          </RouterLink>
          <span v-else>{{ part }}</span>
        </template>
      </p>
    </div>
  </div>
</template>