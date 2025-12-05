<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Eye, EyeOff, ArrowRight, Loader2, AlertTriangle } from 'lucide-vue-next'

const router = useRouter()

const mode = ref('login')
const form = ref({ username: '', password: '', confirmPassword: '' })
const loading = ref(false)
const showPassword = ref(false)
const error = ref(null)
const errors = ref({})

const validateForm = () => {
  errors.value = {}
  
  if (!form.value.username.trim()) {
    errors.value.username = 'Введите логин'
  } else if (mode.value === 'register' && form.value.username.length < 3) {
    errors.value.username = 'Минимум 3 символа'
  }

  if (!form.value.password) {
    errors.value.password = 'Введите пароль'
  } else if (form.value.password.length < 3) {
    errors.value.password = 'Минимум 3 символа'
  }

  if (mode.value === 'register' && form.value.password !== form.value.confirmPassword) {
    errors.value.confirmPassword = 'Пароли не совпадают'
  }

  return !Object.keys(errors.value).length
}

const config = computed(() => ({
  login: { title: 'Вход', subtitle: 'Добро пожаловать', button: 'Войти' },
  register: { title: 'Регистрация', subtitle: 'Создайте аккаунт', button: 'Создать' }
})[mode.value])

const handleSubmit = async () => {
  if (!validateForm()) return

  loading.value = true
  error.value = null

  try {
    const formData = new FormData()
    formData.append('username', form.value.username)
    formData.append('password', form.value.password)

    const res = await fetch(mode.value === 'login' ? '/api/login' : '/api/register', {
      method: 'POST',
      body: formData
    })
    const data = await res.json()

    if (data.status === 'OK') {
      router.push('/profile')
    } else {
      const msgs = { AL: 'Пользователь существует', NF: 'Не найден', WP: 'Неверный пароль' }
      error.value = msgs[data.status] || 'Ошибка'
    }
  } catch {
    error.value = 'Ошибка соединения'
  } finally {
    loading.value = false
  }
}

watch(mode, () => {
  form.value = { username: '', password: '', confirmPassword: '' }
  errors.value = {}
  error.value = null
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="w-full max-w-md animate-fade">
      
      <!-- Card -->
      <div class="bg-[#0f0f0f] border border-white/10 rounded-2xl shadow-2xl overflow-hidden">
        
        <!-- Header -->
        <div class="p-6 border-b border-white/5 bg-[#151515] text-center">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-purple-500/10 border border-purple-500/20 mb-4">
            <User :size="28" class="text-purple-400" />
          </div>
          <h1 class="text-2xl font-bold text-white">{{ config.title }}</h1>
          <p class="text-gray-500 text-sm mt-1">{{ config.subtitle }}</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="p-6 space-y-5">
          
          <!-- Error -->
          <div v-if="error" class="flex items-center gap-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20">
            <AlertTriangle :size="18" class="text-red-400 shrink-0" />
            <span class="text-sm text-red-400">{{ error }}</span>
          </div>

          <!-- Username -->
          <div class="space-y-2">
            <label class="text-xs font-bold text-gray-500 uppercase tracking-wide ml-1">Логин</label>
            <div class="relative">
              <User :size="16" class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-600" />
              <input
                v-model="form.username"
                type="text"
                placeholder="username"
                class="w-full bg-[#0a0a0a] border rounded-xl pl-11 pr-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none transition-colors"
                :class="errors.username ? 'border-red-500/50 focus:border-red-500/50' : 'border-white/10 focus:border-purple-500/50'"
              />
            </div>
            <p v-if="errors.username" class="text-xs text-red-400 ml-1">{{ errors.username }}</p>
          </div>

          <!-- Password -->
          <div class="space-y-2">
            <label class="text-xs font-bold text-gray-500 uppercase tracking-wide ml-1">Пароль</label>
            <div class="relative">
              <Lock :size="16" class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-600" />
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                class="w-full bg-[#0a0a0a] border rounded-xl pl-11 pr-12 py-3 text-white text-sm placeholder-gray-600 focus:outline-none transition-colors"
                :class="errors.password ? 'border-red-500/50 focus:border-red-500/50' : 'border-white/10 focus:border-purple-500/50'"
              />
              <button 
                type="button" 
                @click="showPassword = !showPassword" 
                class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-400 transition-colors"
              >
                <component :is="showPassword ? EyeOff : Eye" :size="16" />
              </button>
            </div>
            <p v-if="errors.password" class="text-xs text-red-400 ml-1">{{ errors.password }}</p>
          </div>

          <!-- Confirm Password -->
          <div v-if="mode === 'register'" class="space-y-2">
            <label class="text-xs font-bold text-gray-500 uppercase tracking-wide ml-1">Подтвердите пароль</label>
            <div class="relative">
              <Lock :size="16" class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-600" />
              <input
                v-model="form.confirmPassword"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                class="w-full bg-[#0a0a0a] border rounded-xl pl-11 pr-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none transition-colors"
                :class="errors.confirmPassword ? 'border-red-500/50 focus:border-red-500/50' : 'border-white/10 focus:border-purple-500/50'"
              />
            </div>
            <p v-if="errors.confirmPassword" class="text-xs text-red-400 ml-1">{{ errors.confirmPassword }}</p>
          </div>

          <!-- Link -->
          <div v-if="mode === 'login'" class="flex justify-end">
            <a href="https://t.me/snowlover4ever" target="_blank" class="text-sm text-purple-400 hover:text-purple-300 transition-colors">
              Связаться с автором
            </a>
          </div>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-sm bg-white text-black hover:bg-gray-100 disabled:opacity-50 transition-all active:scale-[0.98]"
          >
            <Loader2 v-if="loading" :size="16" class="animate-spin" />
            <template v-else>
              {{ config.button }}
              <ArrowRight :size="16" />
            </template>
          </button>
        </form>

        <!-- Footer -->
        <div class="p-4 bg-[#151515] border-t border-white/5 text-center">
          <p class="text-sm text-gray-500">
            {{ mode === 'login' ? 'Нет аккаунта?' : 'Уже есть аккаунт?' }}
            <button
              type="button"
              @click="mode = mode === 'login' ? 'register' : 'login'"
              class="text-purple-400 hover:text-purple-300 font-medium ml-1 transition-colors"
            >
              {{ mode === 'login' ? 'Создать' : 'Войти' }}
            </button>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade { 
  animation: fade .6s cubic-bezier(.16,1,.3,1) 
}
@keyframes fade { 
  from { opacity: 0; transform: translateY(20px) } 
}
</style>