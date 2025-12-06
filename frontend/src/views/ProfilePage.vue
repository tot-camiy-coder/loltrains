<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Loader2, AlertTriangle } from 'lucide-vue-next'
import { useProfile } from '@/scripts/useProfile'

import ProfileCard from '@/components/modules/Profile/ProfileCard.vue'
import CommentsList from '@/components/modules/Profile/CommentsList.vue'
import ModalSettings from '@/components/modules/Profile/ModalSettings.vue'
import ModalReport, { type ReportPayload } from '@/components/modules/Report/ModalReport.vue'

const router = useRouter()

const {
  loading,
  error,
  busy,
  voting,
  user,
  viewer,
  modal,
  now,
  form,
  reportData,
  isOwner,
  myVote,
  canVote,
  save,
  vote,
  sendComment,
  sendReport,
  openReport,
  closeReport,
  onFile,
} = useProfile()

// Handlers
const handleSendComment = async (text: string) => {
  await sendComment(text)
}

const handleReportComment = (comment: any) => {
  openReport('comment', comment)
}

// Обновлённый обработчик для нового формата
const handleSubmitReport = async (payload: ReportPayload) => {
  await sendReport(payload)
}
</script>

<template>
  <div class="min-h-screen flex flex-col items-center text-gray-300 pb-20">
    
    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center">
      <div 
        class="brightness-80 h-100 min-w-80 bg-cover rounded-2xl shadow-lg shadow-black/50" 
        style="background-image: url(/api/media/public/loading.webp)"
      />
      <Loader2 :size="48" class="text-purple-500 animate-spin mt-10" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="mt-40 text-xl text-gray-400 text-center">
      <AlertTriangle :size="48" class="mx-auto mb-4" />
      {{ error }}
      <button 
        @click="router.push(error.includes('авториз') ? '/login' : '/')"
        class="block mx-auto mt-4 text-sm text-purple-400 hover:underline"
      >
        {{ error.includes('авториз') ? 'На страницу входа' : 'На главную' }}
      </button>
    </div>

    <!-- Profile -->
    <main v-else-if="user" class="w-full max-w-4xl px-4 -mt-16 md:mt-8 space-y-6 animate-fade">
      
      <!-- Profile Card -->
      <ProfileCard
        :user="user"
        :viewer="viewer"
        :is-owner="isOwner"
        :can-vote="canVote"
        :my-vote="myVote"
        :voting="voting"
        @vote="vote"
        @open-settings="modal = 'edit'"
        @open-report="openReport('profile', user)"
      />

      <!-- Comments -->
      <CommentsList
        :comments="user.comments || []"
        :user="user"
        :viewer="viewer"
        :is-owner="isOwner"
        :busy="busy"
        :now="now"
        @send="handleSendComment"
        @report="handleReportComment"
      />
    </main>

    <!-- Settings Modal -->
    <Transition name="modal">
      <ModalSettings
        v-if="modal === 'edit' && user"
        :user="user"
        :form="form"
        :busy="busy"
        @close="modal = null"
        @save="save"
        @file="onFile"
        @update:form="form = $event"
      />
    </Transition>

    <!-- Report Modal -->
    <ModalReport
      :visible="modal === 'report'"
      :data="reportData"
      :busy="busy"
      @close="closeReport"
      @submit="handleSubmitReport"
    />
  </div>
</template>

<style scoped>
.animate-fade { 
  animation: fade .6s cubic-bezier(.16,1,.3,1) 
}

@keyframes fade { 
  from { 
    opacity: 0; 
    transform: translateY(20px) 
  } 
}

.modal-enter-active, .modal-leave-active { 
  transition: opacity .3s, transform .3s cubic-bezier(.34,1.56,.64,1) 
}

.modal-enter-from, .modal-leave-to { 
  opacity: 0; 
  transform: scale(.95) translateY(10px) 
}
</style>