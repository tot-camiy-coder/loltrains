<script setup lang="ts">
import { X, Upload, Camera, Loader2 } from 'lucide-vue-next'
import type { User, ProfileForm } from '@/scripts/useProfile'

const props = defineProps<{
  user: User
  form: ProfileForm
  busy: boolean
}>()

const emit = defineEmits<{
  close: []
  save: []
  file: [event: Event, key: 'photo' | 'banner']
  'update:form': [form: ProfileForm]
}>()

const NICK_LIMIT = 16
const DESC_LIMIT = 256

const updateField = <K extends keyof ProfileForm>(key: K, value: ProfileForm[K]) => {
  emit('update:form', { ...props.form, [key]: value })
}

const updateNick = (e: Event) => {
  const value = (e.target as HTMLInputElement).value
  if (value.length <= NICK_LIMIT) {
    updateField('nick', value)
  }
}

const updateDesc = (e: Event) => {
  const value = (e.target as HTMLTextAreaElement).value
  if (value.length <= DESC_LIMIT) {
    updateField('desc', value)
  }
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="emit('close')">
    <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" />
    
    <div class="bg-[#0f0f0f] border border-white/10 w-full max-w-lg rounded-2xl shadow-2xl relative z-10 flex flex-col max-h-[90vh]">
      <!-- Header -->
      <div class="p-4 border-b border-white/5 flex justify-between items-center bg-[#151515]">
        <span class="text-white font-bold text-lg pl-2">Настройки</span>
        <button 
          @click="emit('close')"
          class="w-8 h-8 rounded-full hover:bg-white/10 flex items-center justify-center text-gray-400 hover:text-white"
        >
          <X :size="18" />
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 space-y-6 overflow-y-auto">
        <!-- Banner -->
        <div class="space-y-2">
          <label class="text-xs font-bold text-gray-500 uppercase ml-1">Обложка</label>
          <div 
            class="h-32 rounded-xl bg-cover bg-center relative group cursor-pointer"
            :style="{ backgroundImage: `url(${form.bUrl || user.banner})` }"
          >
            <input 
              type="file" 
              @change="emit('file', $event, 'banner')"
              class="absolute inset-0 opacity-0 cursor-pointer z-20" 
              accept="image/*"
            >
            <div class="absolute inset-0 rounded-xl flex items-center justify-center bg-black/60 opacity-0 group-hover:opacity-100 text-white z-10">
              <Upload :size="24" />
            </div>
          </div>
        </div>

        <!-- Avatar & Nickname -->
        <div class="flex gap-4 items-start">
          <div class="w-24 h-24 relative group shrink-0 cursor-pointer">
            <img 
              :src="form.pUrl || user.photo || '/img/default-avatar.png'"
              class="w-full h-full rounded-full object-cover border-2 border-white/10 bg-[#1a1a1a]"
            >
            <input 
              type="file" 
              @change="emit('file', $event, 'photo')"
              class="absolute inset-0 opacity-0 z-20 cursor-pointer rounded-full" 
              accept="image/*"
            >
            <div class="absolute inset-0 flex items-center justify-center bg-black/60 rounded-full text-white opacity-0 group-hover:opacity-100 z-10">
              <Camera :size="18" />
            </div>
          </div>

          <div class="flex-1 space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-xs font-bold text-gray-500 uppercase ml-1">Никнейм</label>
              <span 
                class="text-xs tabular-nums"
                :class="form.nick.length >= NICK_LIMIT ? 'text-red-400' : 'text-gray-500'"
              >
                {{ form.nick.length }}/{{ NICK_LIMIT }}
              </span>
            </div>
            <input 
              :value="form.nick"
              @input="updateNick"
              :maxlength="NICK_LIMIT"
              class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-purple-500/50"
              placeholder="Никнейм"
            >
          </div>
        </div>

        <!-- Description -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <label class="text-xs font-bold text-gray-500 uppercase ml-1">О себе</label>
            <span 
              class="text-xs tabular-nums"
              :class="form.desc.length >= DESC_LIMIT ? 'text-red-400' : 'text-gray-500'"
            >
              {{ form.desc.length }}/{{ DESC_LIMIT }}
            </span>
          </div>
          <textarea 
            :value="form.desc"
            @input="updateDesc"
            :maxlength="DESC_LIMIT"
            rows="4"
            class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-purple-500/50 resize-none custom-scrollbar"
            placeholder="Расскажите о себе..."
          />
        </div>
      </div>

      <!-- Footer -->
      <div class="p-4 bg-[#151515] border-t border-white/5 flex justify-end gap-3">
        <button 
          @click="emit('close')"
          class="px-4 py-2 rounded-xl text-sm text-gray-400 hover:text-white hover:bg-white/5"
        >
          Отмена
        </button>
        <button 
          @click="emit('save')"
          :disabled="busy"
          class="px-6 py-2 rounded-xl font-bold text-sm bg-white text-black disabled:opacity-50 flex items-center active:scale-95"
        >
          <Loader2 v-if="busy" :size="14" class="animate-spin mr-2" />
          {{ busy ? 'Сохранение' : 'Сохранить' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* Firefox */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.15) transparent;
}
</style>