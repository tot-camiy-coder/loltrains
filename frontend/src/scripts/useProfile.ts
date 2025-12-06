import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/scripts/useAuth'
import { api, relTime } from '@/scripts/helpers'

export interface User {
  username: string
  nickname: string
  description?: string
  photo?: string
  banner?: string
  role?: string
  date_created?: string
  is_owner?: boolean
  can_vote?: boolean
  comments?: Comment[]
  reputation?: {
    likes: number
    dislikes: number
    users: Array<{ username: string; action: number }>
  }
}

export interface Comment {
  id: string
  index: number
  body: string
  timestamp: string
  username: string
  sender?: {
    username: string
    nickname: string
    photo?: string
  }
}

export interface ProfileForm {
  nick: string
  desc: string
  photo: File | null
  banner: File | null
  pUrl: string
  bUrl: string
}

export interface ReportData {
  type: 'profile' | 'comment'
  targetUsername: string
  commentId?: string | number
  commentIndex?: number
}

// Новый интерфейс для payload от модалки
export interface ReportPayload {
  reasonId: string
  reasonLabel: string
  details: string
  data: ReportData
}

export type ModalType = 'edit' | 'report' | null

export function useProfile() {
  const { refreshUser } = useAuth()
  const route = useRoute()
  const router = useRouter()

  // State
  const loading = ref(true)
  const error = ref<string | null>(null)
  const busy = ref(false)
  const voting = ref(false)
  const user = ref<User | null>(null)
  const viewer = ref<User | null>(null)
  const modal = ref<ModalType>(null)
  const now = ref(Date.now())
  const form = ref<ProfileForm>({ nick: '', desc: '', photo: null, banner: null, pUrl: '', bUrl: '' })
  
  // Report state
  const reportData = ref<ReportData | null>(null)

  let timer: number | null = null

  // Computed
  const isOwner = computed(() => user.value?.is_owner ?? false)
  const myVote = computed(() => 
    user.value?.reputation?.users?.find(u => u.username === viewer.value?.username)?.action
  )
  const canVote = computed(() => user.value?.can_vote ?? false)

  // Load profile
  const load = async () => {
    loading.value = true
    error.value = null
    
    try {
      const who = route.query.user as string || ''
      const d = await api(who ? `/api/info?who=${who}` : '/api/info')
      
      if (d.status === 'NF' && !who) {
        router.replace('/login')
        return
      }
      if (d.status === 'NF') {
        error.value = 'Пользователь не найден'
        return
      }
      if (d.status === 'NA') {
        error.value = 'Необходима авторизация'
        refreshUser()
        return
      }

      user.value = {
        ...d.target_user,
        is_owner: d.is_owner,
        comments: d.target_user.comments || [],
        reputation: { likes: 0, dislikes: 0, users: [], ...d.target_user.reputation }
      }
      viewer.value = d.viewer_user

      if (d.is_owner) {
        form.value = {
          nick: user.value.nickname,
          desc: user.value.description || '',
          photo: null,
          banner: null,
          pUrl: user.value.photo || '',
          bUrl: user.value.banner || ''
        }
      }
    } catch {
      error.value = 'Ошибка соединения'
    } finally {
      loading.value = false
    }
  }

  // Save profile
  const save = async () => {
    if (!user.value) return
    
    busy.value = true
    const fd = new FormData()
    fd.append('nickname', form.value.nick)
    fd.append('description', form.value.desc || '')
    fd.append('target', user.value.username)
    if (form.value.photo instanceof File) fd.append('photo', form.value.photo)
    if (form.value.banner instanceof File) fd.append('banner', form.value.banner)

    try {
      await api('/api/profile/edit', 'POST', fd)
      modal.value = null
      load()
      refreshUser()
    } catch (e: any) {
        if (e.status === "LN") alert("Ник слишком длинный :/")
        else if (e.status === "LD") alert("Вот это описание у тебя во 👍 \nНо оно слишком длинное ☹️")
      else alert(e.status || e)
    } finally {
      busy.value = false
    }
  }

  // Vote
  const vote = async (action: number) => {
    if (!canVote.value || !user.value) return
    
    voting.value = true
    const fd = new FormData()
    fd.append('to', user.value.username)
    fd.append('action', String(action))

    try {
      await api('/api/profile/reputation', 'POST', fd)
      load()
    } catch (e: any) {
      alert(e.detail || e)
    } finally {
      voting.value = false
    }
  }

  // Send comment
  const sendComment = async (text: string) => {
    if (!text.trim() || !user.value) return
    
    busy.value = true
    const fd = new FormData()
    fd.append('body', text)
    fd.append('to', user.value.username)

    try {
      await api('/api/profile/add_comment', 'POST', fd)
      load()
      return true
    } catch (e: any) {
      alert(e.detail || e)
      return false
    } finally {
      busy.value = false
    }
  }

  // ✅ ОБНОВЛЕНО: Send report с новым форматом payload
  const sendReport = async (payload: ReportPayload) => {
    if (!payload.reasonId) return
    
    busy.value = true
    const fd = new FormData()
    
    // Основные данные
    fd.append('reason_id', payload.reasonId)
    fd.append('reason_label', payload.reasonLabel)
    fd.append('details', payload.details)

    try {
      if (payload.data.type === 'profile') {
        // Жалоба на профиль
        fd.append('to', payload.data.targetUsername)
        await api('/api/report/profile', 'POST', fd)
      } else {
        // Жалоба на комментарий
        fd.append('author', payload.data.targetUsername)
        fd.append('comment_id', String(payload.data.commentId))
        await api('/api/report/comment', 'POST', fd)
      }
      
      alert('Жалоба отправлена. Спасибо за обращение!')
      modal.value = null
      reportData.value = null
    } catch (e: any) {
      alert(e.detail || e)
    } finally {
      busy.value = false
    }
  }

  // Open report modal
  const openReport = (type: 'profile' | 'comment', data: User | Comment) => {
    if (type === 'profile') {
      if (isOwner.value) return
      reportData.value = {
        type: 'profile',
        targetUsername: (data as User).username
      }
    } else {
      const comment = data as Comment
      reportData.value = {
        type: 'comment',
        targetUsername: user.value?.username || '',
        commentId: comment.id,
        commentIndex: comment.index
      }
    }
    modal.value = 'report'
  }

  // Close report modal
  const closeReport = () => {
    modal.value = null
    reportData.value = null
  }

  // Logout
  const logout = async () => {
    await api('/api/logout', 'POST').catch(() => {})
    router.push('/login')
    refreshUser()
  }

  // File handler
  const onFile = (e: Event, key: 'photo' | 'banner') => {
    const input = e.target as HTMLInputElement
    const file = input.files?.[0]
    if (file) {
      form.value[key] = file
      form.value[key === 'photo' ? 'pUrl' : 'bUrl'] = URL.createObjectURL(file)
    }
  }

  // Copy link
  const copyLink = async () => {
    if (!user.value) return false
    const link = `${window.location.origin}${window.location.pathname}?user=${user.value.username}`
    await navigator.clipboard.writeText(link)
    return true
  }

  // Lifecycle
  watch(() => route.query.user, load)

  onMounted(() => {
    load()
    timer = window.setInterval(() => { now.value = Date.now() }, 1000)
  })

  onUnmounted(() => {
    if (timer) clearInterval(timer)
  })

  return {
    // State
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
    // Computed
    isOwner,
    myVote,
    canVote,
    // Methods
    load,
    save,
    vote,
    sendComment,
    sendReport,
    openReport,
    closeReport,
    logout,
    onFile,
    copyLink,
  }
}