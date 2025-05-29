import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import SignupView from '@/views/SignupView.vue'
import AboutView from '@/views/AboutView.vue'
import GearsView from '@/views/GearsView.vue'
import BorrowView from '@/views/BorrowView.vue'
import SlipsView from '@/views/SlipsView.vue'
import LogsView from '@/views/LogsView.vue'
import { isAuthenticated } from '../auth.js'

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
      meta: { requiresAuth: true },
    },
    {
      path: '/borrow',
      name: 'borrow',
      component: BorrowView,
      meta: { requiresAuth: true },
    },
    {
      path: '/slips',
      name: 'slips',
      component: SlipsView,
      meta: { requiresAuth: true },
    },
    {
      path: '/logs',
      name: 'logs',
      component: LogsView,
      meta: { requiresAuth: true },
    }
  ],
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
