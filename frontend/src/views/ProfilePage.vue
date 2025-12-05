<script setup>
import { onMounted, ref, watch, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/scripts/useAuth'
import { Edit3, LogOut, Flag, Settings, ThumbsUp, ThumbsDown, Calendar, MessageCircle, Camera, Upload, X, Loader2, AlertTriangle, Copy, Check } from 'lucide-vue-next'

const { refreshUser } = useAuth()
const route = useRoute()
const router = useRouter()

// State
const loading = ref(true)
const error = ref(null)
const busy = ref(false)
const voting = ref(false)
const user = ref(null)
const viewer = ref(null)
const modal = ref(null)
const commentText = ref('')
const now = ref(Date.now())
const form = ref({ nick: '', desc: '', photo: null, banner: null, pUrl: '', bUrl: '' })
const reportText = ref('')
const reportTarget = ref(null)
const copied = ref(false)

let timer = null

// Computed
const isOwner = computed(() => user.value?.is_owner)
const myVote = computed(() => user.value?.reputation?.users?.find(u => u.username === viewer.value?.username)?.action)
const canVote = computed(() => user.value?.can_vote)

// Helpers
const api = async (url, method = 'GET', body = null) => {
  const res = await fetch(url, { method, ...(body && { body }) })
  const data = await res.json().catch(() => ({ detail: res.statusText }))
  if (!res.ok) throw data
  return data
}

const relTime = d => {
  if (!d) return ''
  const diff = Math.max(0, (now.value - new Date(d)) / 1000)
  if (diff < 60) return 'только что'
  if (diff < 3600) return `${Math.floor(diff / 60)} мин. назад`
  if (diff < 86400) return `${Math.floor(diff / 3600)} ч. назад`
  if (diff < 604800) return `${Math.floor(diff / 86400)} дн. назад`
  return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}

const parseText = t => t?.split(/(@[\w\d_-]+)/g) || []

const roleClass = {
  OWNER: 'bg-rose-900/20 text-rose-400 border-rose-500/20',
  SADMIN: 'bg-pink-900/20 text-pink-400 border-pink-500/20',
  ADMIN: 'bg-purple-900/20 text-purple-400 border-purple-500/20',
  SMODER: 'bg-cyan-900/20 text-cyan-400 border-cyan-500/20',
  JMODER: 'bg-yellow-900/20 text-yellow-400 border-yellow-500/20',
}

// Copy username link
const copyLink = async () => {
  const link = `${window.location.origin}${window.location.pathname}?user=${user.value.username}`
  await navigator.clipboard.writeText(link)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

// Load profile
const load = async () => {
  loading.value = true
  error.value = null
  try {
    const who = route.query.user || ''
    const d = await api(who ? `/api/info?who=${who}` : '/api/info')
    if (d.status === 'NF' && !who) return router.replace('/login')
    if (d.status === 'NF') return error.value = 'Пользователь не найден'
    if (d.status === 'NA') { error.value = 'Необходима авторизация'; return refreshUser() }
    
    user.value = { ...d.target_user, is_owner: d.is_owner, comments: d.target_user.comments || [], reputation: { likes: 0, dislikes: 0, users: [], ...d.target_user.reputation } }
    viewer.value = d.viewer_user
    if (d.is_owner) form.value = { nick: user.value.nickname, desc: user.value.description, pUrl: user.value.photo, bUrl: user.value.banner }
  } catch { error.value = 'Ошибка соединения' }
  finally { loading.value = false }
}

// Actions
const save = async () => {
  busy.value = true
  const fd = new FormData()
  fd.append('nickname', form.value.nick)
  fd.append('description', form.value.desc || '')
  fd.append('target', user.value.username)
  if (form.value.photo instanceof File) fd.append('photo', form.value.photo)
  if (form.value.banner instanceof File) fd.append('banner', form.value.banner)
  try { await api('/api/profile/edit', 'POST', fd); modal.value = null; load(); refreshUser() }
  catch (e) { alert(e.detail || e) }
  finally { busy.value = false }
}

const vote = async action => {
  if (!canVote.value) return
  voting.value = true
  const fd = new FormData()
  fd.append('to', user.value.username)
  fd.append('action', action)
  try { await api('/api/profile/reputation', 'POST', fd); load() }
  catch (e) { alert(e.detail || e) }
  finally { voting.value = false }
}

const sendComment = async () => {
  if (!commentText.value.trim()) return
  busy.value = true
  const fd = new FormData()
  fd.append('body', commentText.value)
  fd.append('to', user.value.username)
  try { await api('/api/profile/add_comment', 'POST', fd); commentText.value = ''; load() }
  catch (e) { alert(e.detail || e) }
  finally { busy.value = false }
}

const sendReport = async () => {
  if (!reportText.value.trim()) return
  busy.value = true
  const fd = new FormData()
  fd.append('reason', reportText.value)
  if (reportTarget.value.type === 'profile') fd.append('to', reportTarget.value.data.username)
  else { fd.append('author', user.value.username); fd.append('comment_id', reportTarget.value.data.index) }
  try { await api(`/api/report/${reportTarget.value.type}`, 'POST', fd); alert('Жалоба отправлена'); modal.value = null }
  catch (e) { alert(e.detail || e) }
  finally { busy.value = false }
}

const openReport = (type, data) => { 
  if (type === 'profile' && isOwner.value) return
  reportTarget.value = { type, data }
  reportText.value = ''
  modal.value = 'report' 
}

const logout = async () => { await api('/api/logout', 'POST').catch(() => {}); router.push('/login'); refreshUser() }

const onFile = (e, k) => { 
  const f = e.target.files[0]
  if (f) { form.value[k] = f; form.value[k === 'photo' ? 'pUrl' : 'bUrl'] = URL.createObjectURL(f) } 
}

watch(() => route.query.user, load)
onMounted(() => { load(); timer = setInterval(() => now.value = Date.now(), 1000) })
onUnmounted(() => clearInterval(timer))
</script>

<template>
  <div class="min-h-screen flex flex-col items-center text-gray-300 pb-20">
    
    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center">
      <div class="brightness-80 h-100 min-w-80 bg-cover rounded-2xl shadow-lg shadow-black/50" style="background-image: url(/api/media/public/loading.webp)"></div>
      <Loader2 :size="48" class="text-purple-500 animate-spin mt-10"/>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="mt-40 text-xl text-gray-400 text-center">
      <AlertTriangle :size="48" class="mx-auto mb-4"/>
      {{ error }}
      <button @click="router.push(error.includes('авториз') ? '/login' : '/')" class="block mx-auto mt-4 text-sm text-purple-400 hover:underline">
        {{ error.includes('авториз') ? 'На страницу входа' : 'На главную' }}
      </button>
    </div>

    <!-- Profile -->
    <main v-else class="w-full max-w-4xl px-4 -mt-16 md:mt-8 space-y-6 animate-fade">
      
      <!-- Card -->
      <div class="bg-[#0a0a0a]/60 border border-white/5 rounded-3xl shadow-2xl relative backdrop-blur-sm">
        
        <!-- Banner -->
        <div class="h-48 md:h-[400px] bg-cover bg-center rounded-t-2xl relative" :style="{ backgroundImage: `url(${user.banner})` }">
          <div class="absolute inset-0 bg-linear-to-b from-transparent to-[#0a0a0a]/80"></div>
        </div>

        <div class="px-4 pb-6 relative flex flex-col md:flex-row gap-6 -mt-16 md:-mt-20 items-center md:items-start">
          <!-- Avatar -->
          <img :src="user.photo || '/img/default-avatar.png'" class="w-32 h-32 md:w-40 md:h-40 rounded-full border-4 border-[#0a0a0a] bg-[#151515] object-cover shadow-2xl z-10">

          <div class="flex-1 w-full text-center md:text-left pt-2 md:pt-24">
            <div class="flex flex-col md:flex-row justify-between items-center gap-4">
              <div>
                <h1 class="text-3xl font-bold text-white tracking-tight break-all">
                  {{ user.nickname }} 
                  
                  <!-- Username with copy -->
                  <span class="text-gray-500/60 text-lg font-normal md:-ml-2 block md:inline relative group cursor-pointer" @click="copyLink">
                    @{{ user.username }}
                    
                    <!-- Tooltip -->
                    <span class="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 rounded bg-white/10 text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none flex items-center gap-1">
                      <Check v-if="copied" :size="12" class="text-green-400"/>
                      <Copy v-else :size="12"/>
                      {{ copied ? 'Скопировано!' : 'Копировать ссылку' }}
                    </span>
                  </span>
                </h1>
                
                <div class="flex flex-wrap justify-center md:justify-start gap-3 mt-3 text-xs items-center font-medium">
                  <!-- Role -->
                  <span v-if="roleClass[user.role]" :class="`px-2.5 py-0.5 rounded border uppercase tracking-wider ${roleClass[user.role]}`">
                    {{ user.role }}
                  </span>
                  
                  <!-- Reputation -->
                  <div class="px-1 py-0.5 bg-white/5 rounded-full flex items-center border border-white/5 relative select-none">
                    <div v-if="voting" class="absolute inset-0 bg-[#0a0a0a]/80 flex items-center justify-center z-20 rounded-full">
                      <Loader2 :size="12" class="text-white animate-spin"/>
                    </div>

                    <button @click="vote(1)" :disabled="!canVote || voting"
                      :class="['flex items-center gap-1.5 px-3 py-1 transition-all', myVote === 1 ? 'text-green-400' : 'text-gray-400', canVote ? 'hover:text-green-400 active:scale-90' : 'opacity-80']">
                      <ThumbsUp :size="12" :class="myVote === 1 ? 'fill-current' : ''"/>
                      <span>{{ user.reputation?.likes || 0 }}</span>
                    </button>

                    <div class="w-px bg-white/10 h-4"></div>

                    <button @click="vote(-1)" :disabled="!canVote || voting"
                      :class="['flex items-center gap-1.5 px-3 py-1 transition-all', myVote === -1 ? 'text-red-400' : 'text-gray-400', canVote ? 'hover:text-red-400 hover:bg-white/5 active:scale-90' : 'opacity-80']">
                      <ThumbsDown :size="12" :class="myVote === -1 ? 'fill-current' : ''"/>
                      <span>{{ user.reputation?.dislikes || 0 }}</span>
                    </button>
                  </div>
                  
                  <span class="text-gray-500/60 flex items-center gap-1.5">
                    <Calendar :size="12"/> {{ user.date_created }}
                  </span>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex gap-2">
                <button v-if="isOwner" @click="modal = 'edit'" class="px-4 py-2 rounded-xl border border-white/10 hover:bg-white/10 transition-all active:scale-95 text-sm bg-white/5 text-gray-200 flex items-center gap-2">
                  <Settings :size="16" class="text-purple-400"/>Настройки
                </button>
                <button v-else-if="viewer" @click="openReport('profile', user)" class="px-4 py-2 rounded-xl border border-red-500/10 hover:bg-red-500/10 hover:text-red-400 transition-all active:scale-95 text-sm text-gray-500">
                  <Flag :size="14"/>
                </button>
              </div>
            </div>

            <!-- Description -->
            <div v-if="user.description" class="mt-6 text-sm text-gray-300 leading-relaxed bg-white/2 border border-white/5 p-4 rounded-xl whitespace-pre-wrap">
              <template v-for="(part, i) in parseText(user.description)" :key="i">
                <RouterLink v-if="part.startsWith('@')" :to="`?user=${part.slice(1)}`" class="text-purple-400 hover:underline">{{ part }}</RouterLink>
                <span v-else>{{ part }}</span>
              </template>
            </div>
            <div v-else class="mt-6 text-sm text-gray-600 italic">Пользователь не добавил описание.</div>
          </div>
        </div>
      </div>

      <!-- Comments -->
      <div class="flex flex-col gap-4">
        <h3 class="text-xs font-bold text-gray-500 uppercase tracking-widest pl-2 flex items-center gap-2">
          <MessageCircle :size="14"/> Стена ({{ user.comments?.length || 0 }})
        </h3>

        <!-- Input -->
        <div v-if="viewer" class="bg-[#0a0a0a]/60 border border-white/5 rounded-2xl p-4 flex gap-4">
          <img :src="isOwner ? user.photo : viewer.photo" class="w-10 h-10 rounded-full object-cover">
          <div class="flex-1">
            <input v-model="commentText" :placeholder="isOwner ? 'Напишите на стене...' : 'Оставьте комментарий...'" class="w-full bg-transparent text-sm text-white placeholder-gray-600 focus:outline-none h-8"/>
            <div class="flex justify-end pt-2 border-t border-white/20 mt-2">
              <button @click="sendComment" :disabled="busy || !commentText.trim()" class="px-4 py-1.5 rounded-lg text-xs font-bold bg-gray-200/80 text-black hover:bg-gray-100/90 disabled:opacity-50 flex items-center gap-2">
                <Loader2 v-if="busy" :size="12" class="animate-spin"/>
                {{ busy ? '...' : 'Отправить' }}
              </button>
            </div>
          </div>
        </div>

        <!-- List -->
        <div v-if="user.comments?.length" class="space-y-3">
          <div v-for="c in user.comments" :key="c.id" class="group relative bg-[#0a0a0a] border border-white/5 rounded-xl p-4 flex gap-4 hover:border-white/10 transition-colors">
            <button v-if="viewer && c.sender?.username !== viewer.username" @click="openReport('comment', c)" class="absolute top-3 right-3 text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all p-1">
              <Flag :size="12"/>
            </button>
            <img :src="c.sender?.photo" @click="router.push(`?user=${c.username}`)" class="w-10 h-10 rounded-full object-cover cursor-pointer border border-white/5">
            <div class="flex-1 text-sm pr-4">
              <div class="flex justify-between items-baseline mb-1">
                <span class="font-bold text-gray-200 hover:text-purple-400 cursor-pointer" @click="router.push(`?user=${c.sender?.username}`)">{{ c.sender?.nickname }}</span>
                <span class="text-[10px] text-gray-600 font-mono">{{ relTime(c.timestamp) }}</span>
              </div>
              <p class="text-gray-400 whitespace-pre-wrap">
                <template v-for="(part, i) in parseText(c.body)" :key="i">
                  <RouterLink v-if="part.startsWith('@')" :to="`?user=${part.slice(1)}`" class="text-purple-400 hover:underline">{{ part }}</RouterLink>
                  <span v-else>{{ part }}</span>
                </template>
              </p>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-12 text-gray-700 text-xs">Здесь пока пусто...</div>
      </div>
    </main>

    <!-- Edit Modal -->
    <Transition name="modal">
      <div v-if="modal === 'edit'" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="modal = null">
        <div class="absolute inset-0 bg-black/80 backdrop-blur-sm"></div>
        <div class="bg-[#0f0f0f] border border-white/10 w-full max-w-lg rounded-2xl shadow-2xl relative z-10 flex flex-col max-h-[90vh]">
          <div class="p-4 border-b border-white/5 flex justify-between items-center bg-[#151515]">
            <span class="text-white font-bold text-lg pl-2">Настройки</span>
            <button @click="modal = null" class="w-8 h-8 rounded-full hover:bg-white/10 flex items-center justify-center text-gray-400 hover:text-white"><X :size="18"/></button>
          </div>
          <div class="p-6 space-y-6 overflow-y-auto custom-scrollbar">
            <div class="space-y-2">
              <label class="text-xs font-bold text-gray-500 uppercase ml-1">Обложка</label>
              <div class="h-32 rounded-xl bg-cover bg-center border-2 border-dashed border-white/10 relative group cursor-pointer hover:border-purple-500/50" :style="{ backgroundImage: `url(${form.bUrl || user.banner})` }">
                <input type="file" @change="e => onFile(e, 'banner')" class="absolute inset-0 opacity-0 cursor-pointer z-20" accept="image/*">
                <div class="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 group-hover:opacity-100 text-white z-10"><Upload :size="24"/></div>
              </div>
            </div>
            <div class="flex gap-4 items-start">
              <div class="w-24 h-24 relative group shrink-0 cursor-pointer">
                <img :src="form.pUrl || user.photo || '/img/default-avatar.png'" class="w-full h-full rounded-full object-cover border-2 border-white/10 bg-[#1a1a1a]">
                <input type="file" @change="e => onFile(e, 'photo')" class="absolute inset-0 opacity-0 z-20 cursor-pointer rounded-full" accept="image/*">
                <div class="absolute inset-0 flex items-center justify-center bg-black/60 rounded-full text-white opacity-0 group-hover:opacity-100 z-10"><Camera :size="18"/></div>
              </div>
              <div class="flex-1 space-y-2">
                <label class="text-xs font-bold text-gray-500 uppercase ml-1">Никнейм</label>
                <input v-model="form.nick" class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-purple-500/50" placeholder="Никнейм">
              </div>
            </div>
            <div class="space-y-2">
              <label class="text-xs font-bold text-gray-500 uppercase ml-1">О себе</label>
              <textarea v-model="form.desc" rows="4" class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-purple-500/50 resize-none" placeholder="Расскажите о себе..."></textarea>
            </div>
          </div>
          <div class="p-4 bg-[#151515] border-t border-white/5 flex justify-end gap-3">
            <button @click="modal = null" class="px-4 py-2 rounded-xl text-sm text-gray-400 hover:text-white hover:bg-white/5">Отмена</button>
            <button @click="save" :disabled="busy" class="px-6 py-2 rounded-xl font-bold text-sm bg-white text-black disabled:opacity-50 flex items-center active:scale-95">
              <Loader2 v-if="busy" :size="14" class="animate-spin mr-2"/>{{ busy ? 'Сохранение' : 'Сохранить' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Report Modal -->
    <Transition name="modal">
      <div v-if="modal === 'report'" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="modal = null">
        <div class="absolute inset-0 bg-black/80 backdrop-blur-sm"></div>
        <div class="bg-[#0f0f0f] border border-white/10 w-full max-w-md rounded-2xl shadow-2xl relative z-10 flex flex-col">
          <div class="p-4 border-b border-white/5 flex justify-between items-center bg-[#151515]">
            <span class="text-white font-bold text-lg pl-2 flex items-center gap-2">
              <AlertTriangle :size="18" class="text-red-500"/>Жалоба
            </span>
            <button @click="modal = null" class="w-8 h-8 rounded-full hover:bg-white/10 flex items-center justify-center text-gray-400 hover:text-white"><X :size="18"/></button>
          </div>
          <div class="p-6 space-y-4">
            <p class="text-gray-400 text-sm">Опишите причину жалобы.</p>
            <textarea v-model="reportText" rows="4" class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-red-500/50 resize-none" placeholder="Оскорбление, спам..."></textarea>
          </div>
          <div class="p-4 bg-[#151515] border-t border-white/5 flex justify-end gap-3">
            <button @click="modal = null" class="px-4 py-2 rounded-xl text-sm text-gray-400 hover:text-white hover:bg-white/5">Отмена</button>
            <button @click="sendReport" :disabled="busy || !reportText.trim()" class="px-6 py-2 rounded-xl font-bold text-sm bg-red-600 text-white disabled:opacity-50 flex items-center active:scale-95">
              <Loader2 v-if="busy" :size="14" class="animate-spin mr-2"/>{{ busy ? 'Отправка' : 'Пожаловаться' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.animate-fade { animation: fade .6s cubic-bezier(.16,1,.3,1) }
@keyframes fade { from { opacity: 0; transform: translateY(20px) } }
.modal-enter-active, .modal-leave-active { transition: opacity .3s, transform .3s cubic-bezier(.34,1.56,.64,1) }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(.95) translateY(10px) }
.custom-scrollbar::-webkit-scrollbar { width: 4px }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #333; border-radius: 2px }
</style>