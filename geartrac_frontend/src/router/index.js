import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import SignupView from '@/views/SignupView.vue'
import AboutView from '@/views/AboutView.vue'
import GearsView from '@/views/GearsView.vue'
import BorrowView from '@/views/BorrowView.vue'
import SlipsView from '@/views/SlipsView.vue'
import LogsView from '@/views/LogsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView,
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
    },
    {
      path: '/gears',
      name: 'gears',
      component: GearsView,
    },
    {
      path: '/borrow',
      name: 'borrow',
      component: BorrowView,
    },
    {
      path: '/slips',
      name: 'slips',
      component: SlipsView,
    },
    {
      path: '/logs',
      name: 'logs',
      component: LogsView,
    }
  ],
})

export default router
