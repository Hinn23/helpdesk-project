import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import FeedPage from '../pages/FeedPage.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import TicketsPage from '../pages/TicketsPage.vue'
import TicketDetailPage from '../pages/TicketDetailPage.vue'
import TicketCreatePage from '../pages/TicketCreatePage.vue'
import TicketEditPage from '../pages/TicketEditPage.vue'
import AboutPage from '../pages/AboutPage.vue'
import LoginPage from '../pages/LoginPage.vue'
import RegisterPage from '../pages/RegisterPage.vue'
import ForgotPasswordPage from '../pages/ForgotPasswordPage.vue'
import ResetPasswordPage from '../pages/ResetPasswordPage.vue'
import NotFoundPage from '../pages/NotFoundPage.vue'
import ProfilePage from '../pages/ProfilePage.vue'
import UserProfilePage from '../pages/UserProfilePage.vue'
import AuditPage from '../pages/AuditPage.vue'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/feed', name: 'feed', component: FeedPage },
  { path: '/dashboard', name: 'dashboard', component: DashboardPage, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/audit', name: 'audit', component: AuditPage, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/tasks', name: 'tickets', component: TicketsPage },
  { path: '/tasks/create', name: 'ticket-create', component: TicketCreatePage, meta: { requiresAuth: true } },
  { path: '/tasks/:id', name: 'ticket-detail', component: TicketDetailPage },
  { path: '/tasks/:id/edit', name: 'ticket-edit', component: TicketEditPage },
  { path: '/about', name: 'about', component: AboutPage },
  { path: '/profile', name: 'profile', component: ProfilePage, meta: { requiresAuth: true } },
  { path: '/users/:id', name: 'user-profile', component: UserProfilePage },
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/register', name: 'register', component: RegisterPage },
  { path: '/forgot-password', name: 'forgot-password', component: ForgotPasswordPage },
  { path: '/reset-password', name: 'reset-password', component: ResetPasswordPage },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()
  if (auth.isAuthenticated) await auth.checkAuth()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next('/login')
    return
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    next('/')
    return
  }
  next()
})

export default router
