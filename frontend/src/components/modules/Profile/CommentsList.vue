<script setup lang="ts">
import { MessageCircle } from 'lucide-vue-next'
import CommentCard from './CommentCard.vue'
import CommentForm from './CommentForm.vue'
import type { Comment, User } from '@/scripts/useProfile'

defineProps<{
  comments: Comment[]
  user: User
  viewer: User | null
  isOwner: boolean
  busy: boolean
  now: number
}>()

const emit = defineEmits<{
  send: [text: string]
  report: [comment: Comment]
}>()
</script>

<template>
  <div class="flex flex-col gap-4">
    <h3 class="text-xs font-bold text-gray-500 uppercase tracking-widest pl-2 flex items-center gap-2">
      <MessageCircle :size="14" />
      Стена ({{ comments.length }})
    </h3>

    <!-- Input -->
    <CommentForm 
      v-if="viewer" 
      :user="user"
      :viewer="viewer"
      :is-owner="isOwner"
      :busy="busy"
      @send="emit('send', $event)"
    />

    <!-- List -->
    <div v-if="comments.length" class="space-y-3">
      <CommentCard 
        v-for="c in comments" 
        :key="c.id"
        :comment="c"
        :viewer="viewer"
        :now="now"
        @report="emit('report', $event)"
      />
    </div>
    
    <div v-else class="text-center py-12 text-gray-700 text-xs">
      Здесь пока пусто...
    </div>
  </div>
</template>