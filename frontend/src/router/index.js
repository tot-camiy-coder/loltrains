import AuthPage from '@/views/AuthPage.vue'
import ProfilePage from '@/views/ProfilePage.vue'
import RouteStops from '@/views/RouteStops.vue'
import HomeView from '@/views/SearchRoutes.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Main',
      component: HomeView
    },
    {
      path: '/route',
      name: 'Route',
      component: RouteStops
    },
    {
      path: '/login',
      name: 'Login',
      component: AuthPage
    },
    {
      path: '/profile',
      name: 'Profile',
      component: ProfilePage
    }
  ],
})

export default router
