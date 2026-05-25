<template>
  <div id="app">
    <NavBar />
    <div v-if="auth.isWarned" class="warn-banner">
      <TriangleAlert :size="14" />
      <span>У вас есть предупреждение. Нарушение правил может привести к блокировке.</span>
    </div>
    <FriendsSidebar />
    <ToastNotification />
    <main class="container">
      <router-view v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" :key="$route.path" />
        </Transition>
      </router-view>
    </main>
    <footer class="footer">
      Helpdesk Lite v0.3.0
    </footer>
    <button v-if="showScrollTop" class="scroll-top" @click="scrollToTop" title="Наверх">
      <ChevronUp :size="18" :strokeWidth="2.5" />
    </button>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { useToastStore } from './stores/toast'
import { useNotifyStore } from './stores/notify'
import { TriangleAlert, ChevronUp } from 'lucide-vue-next'
import NavBar from './components/NavBar.vue'
import FriendsSidebar from './components/FriendsSidebar.vue'
import ToastNotification from './components/ToastNotification.vue'
import { useThemeStore } from './stores/theme'
useThemeStore()

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()
const notify = useNotifyStore()

const routeTitles = {
  'home': 'Главная',
  'feed': 'Лента',
  'tickets': 'Заявки',
  'ticket-create': 'Новая заявка',
  'ticket-detail': 'Заявка',
  'ticket-edit': 'Редактирование',
  'dashboard': 'Дашборд',
  'about': 'О проекте',
  'profile': 'Профиль',
  'login': 'Вход',
  'register': 'Регистрация',
  'forgot-password': 'Сброс пароля',
  'reset-password': 'Новый пароль',
  'user-profile': 'Пользователь',
}

const showScrollTop = ref(false)
function scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }) }

watch(() => router.currentRoute.value, (route) => {
  const name = routeTitles[route.name] || 'Helpdesk Lite'
  document.title = `${name} · Helpdesk Lite`
  window.scrollTo({ top: 0 })
}, { immediate: true })

onMounted(() => {
  window.addEventListener('scroll', () => { showScrollTop.value = window.scrollY > 300 })
  auth.checkAuth()
})
onUnmounted(() => {
  window.removeEventListener('scroll', () => {})
})

function handleKeydown(e) {
  if (e.key === 'Escape') {
    const bulk = document.querySelector('.bulk-bar')
    if (bulk) { const ev = new Event('click'); bulk.querySelector('.btn-secondary')?.dispatchEvent(ev); return }
  }
  if (!e.ctrlKey && !e.metaKey) return
  if (e.key === 'n' || e.key === 'N' || e.key === 'ы' || e.key === 'Ы') {
    e.preventDefault()
    if (auth.isAuthenticated) router.push('/tasks/create')
  }
  if (e.key === 'f' || e.key === 'F' || e.key === 'а' || e.key === 'А') {
    e.preventDefault()
    const input = document.querySelector('.filters input')
    if (input) { input.focus(); input.select() }
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  const es = new EventSource('/api/events')
  es.addEventListener('ticket_created', (e) => {
    try { const d = JSON.parse(e.data); toast.info(`Новая заявка: #${d.id} ${d.title}`); notify.add({ text: `Новая заявка: #${d.id} ${d.title}`, time: 'только что' }) } catch {}
  })
  es.addEventListener('ticket_updated', (e) => {
    try { const d = JSON.parse(e.data); toast.info(`#${d.id} ${d.title}: изменено ${d.changed?.join(', ')}`); notify.add({ text: `#${d.id} ${d.title}: изменено ${d.changed?.join(', ')}`, time: 'только что' }) } catch {}
  })
  es.addEventListener('friend_request', (e) => {
    try { const d = JSON.parse(e.data); if (Number(auth.userId) === d.from_user_id) return; notify.add({ text: `Заявка в друзья от ${d.from_user_name}`, time: 'только что', action: 'open_friends' }); toast.info(`Заявка в друзья от ${d.from_user_name}`) } catch {}
  })
  es.addEventListener('friend_accepted', (e) => {
    try { const d = JSON.parse(e.data); if (Number(auth.userId) === d.by_user_id) return; notify.add({ text: `${d.by_user_name} принял(а) заявку в друзья`, time: 'только что', action: 'open_friends' }); toast.success(`${d.by_user_name} принял(а) заявку в друзья`) } catch {}
  })
  es.addEventListener('user_warning', (e) => {
    try { const d = JSON.parse(e.data); if (Number(auth.userId) !== d.user_id) return; notify.add({ text: `Предупреждение от ${d.admin_name}: ${d.reason}`, time: 'только что' }); toast.info(`Предупреждение от ${d.admin_name}: ${d.reason}`) } catch {}
  })
  es.addEventListener('user_status', (e) => {
    try { const d = JSON.parse(e.data); if (Number(auth.userId) !== d.user_id) return; notify.add({ text: `Ваш статус изменён: ${d.action}`, time: 'только что' }); toast.info(`Ваш статус изменён: ${d.action}`) } catch {}
  })
  es.addEventListener('comment_deleted', (e) => {
    try { const d = JSON.parse(e.data); if (Number(auth.userId) !== d.user_id) return; notify.add({ text: `Ваш комментарий удалён модератором ${d.by_user_name}`, time: 'только что' }); toast.info(`Ваш комментарий удалён модератором ${d.by_user_name}`) } catch {}
  })
  es.addEventListener('new_message', (e) => {
    try { const d = JSON.parse(e.data); if (Number(auth.userId) !== d.to_user_id) return; notify.add({ text: `Сообщение от ${d.from_user_name}`, time: 'только что' }); toast.info(`Сообщение от ${d.from_user_name}`); if (window.__reloadMessages) window.__reloadMessages() } catch {}
  })
  es.onerror = () => {}
  window.__sse = es
})
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  if (window.__sse) window.__sse.close()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --bg: #f0fdfa;
  --bg-card: #ffffff;
  --bg-input: #f7fcf9;
  --bg-hover: #e6f7f0;
  --bg-table-header: #f0fdfa;
  --text: #134e4a;
  --text-secondary: #2c7a6a;
  --text-muted: #5ca490;
  --text-dim: #94cab8;
  --border: #c5e8d8;
  --border-input: #a8d5c5;
  --border-light: #d9f0e5;
  --primary: #0d9488;
  --primary-hover: #0f766e;
  --primary-shadow: rgba(13, 148, 136, 0.2);
  --danger: #ef4444;
  --danger-hover: #dc2626;
  --danger-shadow: rgba(239, 68, 68, 0.2);
  --nav-bg: rgba(240, 253, 250, 0.9);
  --nav-border: #c5e8d8;
  --footer-border: #c5e8d8;
  --scrollbar-thumb: #a8d5c5;
  --scrollbar-thumb-hover: #5ca490;
  --code-bg: #134e4a;
  --code-text: #e2e8f0;
  --primary-rgb: 13, 148, 136;
}

[data-theme="dark"] {
  --bg: #0d1512;
  --bg-card: #16231f;
  --bg-input: #1c2d27;
  --bg-hover: #21362e;
  --bg-table-header: #16231f;
  --text: #ccfbf1;
  --text-secondary: #5eead4;
  --text-muted: #2dd4bf;
  --text-dim: #14b8a6;
  --border: #1f3d35;
  --border-input: #2a4f43;
  --border-light: #1a3229;
  --primary: #14b8a6;
  --primary-hover: #2dd4bf;
  --primary-shadow: rgba(20, 184, 166, 0.3);
  --danger: #ef4444;
  --danger-hover: #f87171;
  --danger-shadow: rgba(239, 68, 68, 0.3);
  --nav-bg: rgba(13, 21, 18, 0.9);
  --nav-border: #1f3d35;
  --footer-border: #1f3d35;
  --scrollbar-thumb: #2a4f43;
  --scrollbar-thumb-hover: #3a6b5a;
  --code-bg: #0a120e;
  --code-text: #e2e8f0;
  --primary-rgb: 20, 184, 166;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  line-height: 1.6;
  transition: background 0.3s, color 0.3s;
}

.container {
  max-width: 1040px;
  margin: 0 auto;
  padding: 32px 24px;
  min-height: calc(100vh - 100px);
  transition: margin-left 0.3s;
}


a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

a:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}

button {
  cursor: pointer;
  font-family: inherit;
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
  animation: cardIn 0.5s ease-out both;
  transition: box-shadow 0.3s, transform 0.3s, background 0.3s, border-color 0.3s;
}

.card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06), 0 2px 4px rgba(0, 0, 0, 0.04);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 13px;
}

.form-control {
  width: 100%;
  padding: 10px 14px;
  background: var(--bg-input);
  border: 1px solid var(--border-input);
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  color: var(--text);
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s, color 0.2s;
}

.form-control::placeholder {
  color: var(--text-dim);
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  background: var(--bg-card);
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.08);
}

select.form-control {
  appearance: auto;
  cursor: pointer;
}

textarea.form-control {
  resize: vertical;
}

.btn {
  padding: 10px 22px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  line-height: 1;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn:active {
  transform: scale(0.96);
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none !important;
}

.btn-primary {
  background: var(--primary);
  color: #fff;
  box-shadow: 0 2px 8px var(--primary-shadow);
}

.btn-primary:hover {
  background: var(--primary-hover);
  color: #fff;
  box-shadow: 0 4px 16px var(--primary-shadow);
}

.btn-danger {
  background: var(--danger);
  color: #fff;
  box-shadow: 0 2px 8px var(--danger-shadow);
}

.btn-danger:hover {
  background: var(--danger-hover);
  color: #fff;
  box-shadow: 0 4px 16px var(--danger-shadow);
}

.btn-secondary {
  background: var(--bg-hover);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background: var(--bg-input);
  transform: translateY(-1px);
}

.btn-xs { padding: 4px 10px; font-size: 12px; border-radius: 6px; }
.btn-sm { padding: 6px 14px; font-size: 13px; }

.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.2px;
  text-transform: uppercase;
  transition: transform 0.2s;
}

.badge:hover {
  transform: scale(1.05);
}

.badge-new { background: rgba(5, 150, 105, 0.1); color: #059669; }
.badge-on_moderation { background: rgba(217, 119, 6, 0.1); color: #d97706; }
.badge-in_progress { background: rgba(37, 99, 235, 0.1); color: #2563eb; }
.badge-done { background: rgba(124, 58, 237, 0.1); color: #7c3aed; }
.badge-cancelled { background: rgba(220, 38, 38, 0.1); color: #dc2626; }
.badge-closed { background: rgba(107, 114, 128, 0.1); color: #6b7280; }
.badge-high { background: rgba(220, 38, 38, 0.1); color: #dc2626; }
.badge-medium { background: rgba(217, 119, 6, 0.1); color: #d97706; }
.badge-low { background: rgba(5, 150, 105, 0.1); color: #059669; }

[data-theme="dark"] .badge-new { background: rgba(52, 211, 153, 0.15); color: #34d399; }
[data-theme="dark"] .badge-on_moderation { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
[data-theme="dark"] .badge-in_progress { background: rgba(96, 165, 250, 0.15); color: #60a5fa; }
[data-theme="dark"] .badge-done { background: rgba(167, 139, 250, 0.15); color: #a78bfa; }
[data-theme="dark"] .badge-cancelled { background: rgba(248, 113, 113, 0.15); color: #f87171; }
[data-theme="dark"] .badge-closed { background: rgba(156, 163, 175, 0.15); color: #9ca3af; }
[data-theme="dark"] .badge-high { background: rgba(248, 113, 113, 0.15); color: #f87171; }
[data-theme="dark"] .badge-medium { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
[data-theme="dark"] .badge-low { background: rgba(52, 211, 153, 0.15); color: #34d399; }

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  animation: fadeIn 0.4s ease-out;
}

.header-section h1 {
  font-size: 28px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.3px;
}

.filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filters .form-group {
  margin-bottom: 0;
}

.filters .form-control {
  padding: 8px 12px;
  font-size: 13px;
  min-width: 170px;
}

.footer {
  text-align: center;
  padding: 24px;
  color: var(--text-dim);
  font-size: 13px;
  border-top: 1px solid var(--footer-border);
  transition: color 0.3s, border-color 0.3s;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-light);
}

th {
  color: var(--text-dim);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: var(--bg-table-header);
}

td {
  color: var(--text);
  font-size: 14px;
}

tbody tr {
  transition: background 0.2s;
}

tbody tr:hover td {
  background: var(--bg-hover);
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 6px;
  padding: 24px 0;
  animation: fadeIn 0.5s ease-out;
}

.pagination button {
  padding: 8px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination button:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--primary);
  color: var(--primary);
}

.pagination button.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
  box-shadow: 0 2px 8px var(--primary-shadow);
}

.pagination button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-dim);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-dim);
}

.empty-state h3 {
  margin-bottom: 8px;
  color: var(--text-muted);
  font-weight: 600;
}

.error-box {
  background: rgba(220, 38, 38, 0.08);
  color: var(--danger);
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  border: 1px solid rgba(220, 38, 38, 0.15);
  animation: slideIn 0.35s ease-out;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(-16px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.page-enter-active {
  transition: opacity 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.page-leave-active {
  transition: opacity 0.2s ease-in, transform 0.2s ease-in;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.98);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--scrollbar-thumb-hover); }

::selection { background: rgba(13, 148, 136, 0.15); }

.kanban-column.drag-over { border-color: var(--primary); background: rgba(var(--primary-rgb), 0.04); }
.kanban-card.dragging { opacity: 0.5; }

.avatar-circle {
  width: 56px; height: 56px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 800; flex-shrink: 0; color: #fff;
}

.warn-banner {
  background: rgba(217, 119, 6, 0.12);
  color: #d97706;
  padding: 8px 24px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  border-bottom: 1px solid rgba(217, 119, 6, 0.2);
}
</style>
