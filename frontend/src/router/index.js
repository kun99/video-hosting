import { createRouter, createWebHistory } from 'vue-router'
import NavBar from '@/components/NavBar.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/home',
      component: NavBar,
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/list',
      component: NavBar,
      name: 'list',
      component: () => import('../views/ListView.vue')
    },
    {
      path: '/upload',
      component: NavBar,
      name: 'upload',
      component: () => import('../views/UploadView.vue')
    },
    {
      path: '/',
      name: 'landing',
      component: () => import('../views/LandingView.vue')
    },
    {
      path: '/login',
      component: NavBar,
      name: 'login',
      component: () => import('../views/LoginView.vue')
    }, 
    {
      path: '/register',
      component: NavBar,
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/playback',
      component: NavBar,
      name: 'playback',
      component: () => import('../views/PlaybackView.vue')
    }
  ]
})

export default router
