import { ref } from 'vue';

// --- ГЛОБАЛЬНОЕ СОСТОЯНИЕ ---
// Объявляем переменные ВНЕ функции, чтобы они были общими для всего приложения (Singleton)
const user = ref<any | null>(null);
const isLoading = ref(false);

export function useAuth() {

  // Функция обновления данных (вызывается при загрузке сайта и после входа)
  const refreshUser = async () => {
    isLoading.value = true;
    try {
      // 1. Проверяем авторизацию
      const checkRes = await fetch('/api/check');
      
      if (checkRes.ok) {
        const isAuthorized = await checkRes.json(); // Ожидаем true/false

        if (isAuthorized === true) {
          // 2. Если авторизован — запрашиваем профиль
          const infoRes = await fetch('/api/info');
          if (infoRes.ok) {
            user.value = await infoRes.json();
          } else {
            user.value = null;
          }
        } else {
          // Если check вернул false
          user.value = null;
        }
      } else {
        user.value = null;
      }
    } catch (error) {
      console.error('Auth error:', error);
      user.value = null;
    } finally {
      isLoading.value = false;
    }
  };

  // Функция выхода (очищает состояние на клиенте)
  const logout = () => {
    user.value = null;
    // Тут можно добавить fetch('/api/logout')
  };

  return {
    user,
    isLoading,
    refreshUser,
    logout
  };
}