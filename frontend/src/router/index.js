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
    }
  ],
})

export default router
