<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Home, Heart, MessageCircle, LogIn, Train, Loader2, User } from 'lucide-vue-next'
import SearchForm from './SearchRoutes/Main/SearchForm.vue'
import { useAuth } from '@/scripts/useAuth'

const route = useRoute()
const router = useRouter()

// Авторизация через composable
const { user, isLoading: isCheckingAuth, refreshUser } = useAuth()

// Computed свойства для пользователя
const isAuthenticated = computed(() => !!user.value)

const userPhoto = computed(() => user.value?.viewer_user?.photo || null)

const userInitials = computed(() => {
  const u = user.value?.viewer_user
  const name = u?.nickname || u?.username || 'U'
  return name.slice(0, 2).toUpperCase()
})

// Обновляем при монтировании и смене маршрута
onMounted(refreshUser)
watch(() => route.path, () => {
  if (['/', '/profile'].includes(route.path)) {
    refreshUser()
  }
})

// Навигация
const navItems = [
  { path: '/', label: 'Главная', icon: Home },
  { path: '/favorites', label: 'Избранное', icon: Heart },
  { path: '/chat', label: 'Чат', icon: MessageCircle }
]

const isActive = (path) => path === '/' ? route.path === '/' : route.path.startsWith(path)
const isProfileActive = computed(() => ['/profile', '/login'].includes(route.path))
const hasSearched = computed(() => route.query.from && route.query.to)
const handleAuthClick = () => router.push(isAuthenticated.value ? '/profile' : '/login')

// Props & Emits
defineProps({
  form: { type: Array, default: () => [{ name: '', code: '', label: 'Откуда' }, { name: '', code: '', label: 'Куда' }] },
  activeInputIndex: Number,
  currentItems: Array,
  isLoading: Boolean,
  isSearchValid: Boolean
})
defineEmits(['update:form', 'search', 'select', 'swap', 'find'])
</script>

<template>
  <!-- DESKTOP -->
  <header class="fixed top-0 inset-x-0 z-50 hidden lg:block bg-[#0A0A0B]/80 backdrop-blur-xl border-b border-white/5">
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center gap-6">
      <router-link to="/" class="flex items-center gap-3 group shrink-0">
        <span class="text-xl font-bold text-white hidden xl:block">LOLTrains</span>
      </router-link>

      <div class="flex-1 max-w-2xl">
        <SearchForm v-if="hasSearched" v-bind="$props" :isCompact="true"
          @update:form="$emit('update:form', $event)" @search="(q,i) => $emit('search',q,i)"
          @select="(s,i) => $emit('select',s,i)" @swap="$emit('swap')" @find="$emit('find')" />
      </div>

      <nav class="flex items-center gap-1">
        <router-link v-for="item in navItems" :key="item.path" :to="item.path"
          class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all"
          :class="isActive(item.path) ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'">
          <component :is="item.icon" :size="18" />
          <span class="hidden xl:inline">{{ item.label }}</span>
        </router-link>

        <div class="w-px h-6 bg-white/10 mx-2" />

        <button @click="handleAuthClick" class="relative w-10 h-10 rounded-full overflow-hidden transition-all"
          :class="isAuthenticated ? 'ring-2 ring-indigo-500/50 hover:ring-indigo-500' : 'bg-white/10 hover:bg-white/20'">
          <Loader2 v-if="isCheckingAuth" :size="18" class="text-white/60 animate-spin mx-auto" />
          <img v-else-if="isAuthenticated && userPhoto" :src="userPhoto" class="w-full h-full object-cover" @error="user.viewer_user.photo = null" />
          <div v-else-if="isAuthenticated" class="w-full h-full bg-linear-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-sm font-semibold text-white">{{ userInitials }}</div>
          <LogIn v-else :size="18" class="text-white/60 mx-auto" />
        </button>
      </nav>
    </div>
  </header>
  <div class="hidden lg:block h-16" />

  <!-- MOBILE -->
  <nav class="fixed bottom-0 inset-x-0 z-50 lg:hidden bg-[#0A0A0B]/90 backdrop-blur-xl border-t border-white/5 pb-[env(safe-area-inset-bottom)]">
    <div class="flex justify-around h-16">
      <router-link v-for="item in navItems" :key="item.path" :to="item.path"
        class="flex flex-col items-center justify-center min-w-16" :class="isActive(item.path) ? 'text-white' : 'text-white/40'">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center" :class="''">
          <component :is="item.icon" :size="20" />
        </div>
        <span class="text-[10px] font-medium -mt-2">{{ item.label }}</span>
      </router-link>

      <button @click="handleAuthClick" class="flex flex-col items-center justify-center min-w-16" :class="isProfileActive ? 'text-white' : 'text-white/40'">
        <div class="relative w-8 h-8 rounded-full overflow-hidden flex items-center justify-center" :class="'bg-white/5'">
          <Loader2 v-if="isCheckingAuth" :size="18" class="animate-spin" />
          <img v-else-if="isAuthenticated && userPhoto" :src="userPhoto" class="w-full h-full object-cover" @error="user.viewer_user.photo = null" />
          <div v-else-if="isAuthenticated" class="w-full h-full bg-linear-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-xs font-semibold">{{ userInitials }}</div>
          <User v-else :size="20" />
        </div>
        <span class="text-[10px] font-medium -mt-1">{{ isAuthenticated ? 'Профиль' : 'Войти' }}</span>
      </button>
    </div>
  </nav>
  <div class="lg:hidden h-20" />
</template>