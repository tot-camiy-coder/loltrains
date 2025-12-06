import { ref } from 'vue'

// API helper
export const api = async (url: string, method = 'GET', body: FormData | null = null) => {
  const res = await fetch(url, { method, ...(body && { body }) })
  const data = await res.json().catch(() => ({ detail: res.statusText }))
  if (!res.ok) throw data
  return data
}

// Relative time
export const relTime = (d: string | undefined, now: number) => {
  if (!d) return ''
  const diff = Math.max(0, (now - new Date(d).getTime()) / 1000)
  if (diff < 60) return 'только что'
  if (diff < 3600) return `${Math.floor(diff / 60)} мин. назад`
  if (diff < 86400) return `${Math.floor(diff / 3600)} ч. назад`
  if (diff < 604800) return `${Math.floor(diff / 86400)} дн. назад`
  return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}

// Parse @mentions
export const parseText = (t: string | undefined): string[] => t?.split(/(@[\w\d_-]+)/g) || []

// Role classes
export const roleClass: Record<string, string> = {
  OWNER: 'bg-rose-900/20 text-rose-400 border-rose-500/20',
  SADMIN: 'bg-pink-900/20 text-pink-400 border-pink-500/20',
  ADMIN: 'bg-purple-900/20 text-purple-400 border-purple-500/20',
  SMODER: 'bg-cyan-900/20 text-cyan-400 border-cyan-500/20',
  JMODER: 'bg-yellow-900/20 text-yellow-400 border-yellow-500/20',
}

