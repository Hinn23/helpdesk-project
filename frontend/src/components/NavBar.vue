<template>
  <nav class="navbar">
    <div class="nav-inner">
      <router-link to="/" class="nav-brand">Helpdesk Lite</router-link>
      <button class="burger" @click="menuOpen = !menuOpen" :title="menuOpen ? 'Закрыть меню' : 'Открыть меню'">
        <span :class="{ open: menuOpen }"></span>
      </button>
      <div class="nav-content" :class="{ open: menuOpen }">
        <div class="nav-links">
          <router-link to="/feed" @click="menuOpen = false">Лента</router-link>
          <router-link to="/tasks" @click="menuOpen = false">Заявки</router-link>
          <router-link v-if="auth.isAdmin" to="/dashboard" @click="menuOpen = false">Дашборд</router-link>
          <router-link v-if="auth.isAdmin" to="/audit" @click="menuOpen = false">Журнал</router-link>
          <router-link to="/about" @click="menuOpen = false">О проекте</router-link>
        </div>
        <div class="nav-right">
          <div class="user-search" v-if="auth.isAuthenticated">
            <input v-model="searchQuery" @input="debouncedSearch" @focus="searchOpen = true" @blur="onSearchBlur" placeholder="Поиск #ID, пользователей..." class="search-input" />
            <div v-if="searchOpen && (searchUsers.length || searchTickets.length)" class="search-results">
              <div v-if="searchTickets.length" style="padding: 6px 12px 2px; font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.3px;">Заявки</div>
              <router-link v-for="t in searchTickets" :key="'t'+t.id" :to="`/tasks/${t.id}`" class="search-result-item" @click="clearSearch">
                <span class="cell-id" style="margin-right: 8px;">#{{ t.id }}</span>
                <span class="search-name" style="flex:1;" v-html="highlight(t.title, searchQuery)"></span>
                <span class="badge" :class="'badge-' + t.status" style="font-size: 8px;">{{ statusLabel(t.status) }}</span>
              </router-link>
              <div v-if="searchUsers.length && searchTickets.length" style="border-top: 1px solid var(--border-light);"></div>
              <div v-if="searchUsers.length" style="padding: 6px 12px 2px; font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.3px;">Пользователи</div>
              <router-link v-for="u in searchUsers" :key="u.id" :to="`/users/${u.id}`" class="search-result-item" @click="clearSearch">
                <img v-if="u.avatar" :src="`/api/auth/${u.id}/avatar`" class="search-avatar" />
                <div v-else class="search-avatar-placeholder">{{ u.name.slice(0, 2).toUpperCase() }}</div>
                <div>
                  <div class="search-name" v-html="highlight(u.name, searchQuery)"></div>
                  <div class="search-email" v-html="highlight(u.email, searchQuery)"></div>
                </div>
              </router-link>
            </div>
          </div>
          <button class="theme-toggle" @click="theme.toggle()" :title="theme.current === 'dark' ? 'Светлая тема' : 'Тёмная тема'">
            <Moon v-if="theme.current === 'light'" :size="16" />
            <Sun v-else :size="16" />
          </button>
          <button v-if="auth.isAuthenticated" class="notif-btn" @click="showMsg = !showMsg" title="Сообщения">
            <MessageCircle :size="16" />
          </button>
          <button v-if="auth.isAuthenticated" class="notif-btn" @click="showNotif = !showNotif" :title="notify.count ? `${notify.count} уведомлений` : 'Нет уведомлений'">
            <Bell :size="16" />
            <span v-if="notify.hasUnread" class="notif-badge">{{ notify.count > 9 ? '9+' : notify.count }}</span>
            <div v-if="showNotif" class="notif-dropdown">
              <div v-if="!notify.items.length" style="padding: 12px 16px; color: var(--text-dim); font-size: 13px;">Нет уведомлений</div>
              <div v-for="n in notify.items.slice(0, 10)" :key="n.id" class="notif-item" :class="{ unread: !n.read, clickable: n.action }" @click="handleNotifClick(n)">
                <span style="font-size: 13px;">{{ n.text }}</span>
                <span style="font-size: 10px; color: var(--text-dim);">{{ n.time }}</span>
              </div>
              <div v-if="notify.items.length" style="padding: 8px 16px; border-top: 1px solid var(--border);">
                <button class="btn btn-xs btn-secondary" style="width:100%;" @click="notify.markRead()">Отметить прочитанным</button>
              </div>
            </div>
          </button>
          <template v-if="auth.isAuthenticated">
            <router-link to="/profile" class="nav-user" @click="menuOpen = false">{{ auth.userName || auth.userRole }}</router-link>
            <button class="btn-outline" @click="showLogout = true">Выйти</button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn-link" @click="menuOpen = false">Войти</router-link>
            <router-link to="/register" class="btn-outline" @click="menuOpen = false">Регистрация</router-link>
          </template>
        </div>
      </div>
    </div>
    <ConfirmDialog :visible="showLogout" title="Выход" message="Вы уверены, что хотите выйти?" confirmText="Выйти" :danger="true" @confirm="handleLogout" @cancel="showLogout = false" />
    <MessagesModal ref="msgModalRef" :visible="showMsg" @update:visible="showMsg = $event" />
  </nav>
</template>

<script setup>
import { Moon, Sun, MessageCircle, Bell } from 'lucide-vue-next'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import { useNotifyStore } from '../stores/notify'
import ConfirmDialog from './ConfirmDialog.vue'
import MessagesModal from './MessagesModal.vue'
import api from '../api/axios'

const auth = useAuthStore()
const theme = useThemeStore()
const notify = useNotifyStore()
const router = useRouter()
const menuOpen = ref(false)
const showLogout = ref(false)
const showNotif = ref(false)
const showMsg = ref(false)
const msgModalRef = ref(null)
const searchQuery = ref('')
const searchUsers = ref([])
const searchTickets = ref([])
const searchOpen = ref(false)
let searchTimer = null
let blurTimer = null

function onSearchBlur() { blurTimer = setTimeout(() => { searchOpen.value = false }, 200) }

function debouncedSearch() {
  clearTimeout(searchTimer)
  const q = searchQuery.value.trim()
  if (!q) { searchUsers.value = []; searchTickets.value = []; return }
  const idMatch = q.match(/^#(\d+)$/)
  if (idMatch) {
    import('../router/index.js').then(({ default: router }) => {
      router.push(`/tasks/${idMatch[1]}`)
      clearSearch()
    })
    return
  }
  searchTimer = setTimeout(async () => {
    try {
      const [users, tickets] = await Promise.all([
        api.get(`/users/search?q=${encodeURIComponent(q)}&limit=3`).then(r => r.data),
        api.get(`/tickets/?search=${encodeURIComponent(q)}&limit=3`).then(r => r.data.items || []),
      ])
      searchUsers.value = users
      searchTickets.value = tickets
    } catch { searchUsers.value = []; searchTickets.value = [] }
  }, 300)
}

function highlight(text, query) {
  if (!query || !text) return text
  const idx = text.toLowerCase().indexOf(query.toLowerCase())
  if (idx === -1) return text
  return text.slice(0, idx) + '<strong>' + text.slice(idx, idx + query.length) + '</strong>' + text.slice(idx + query.length)
}

function clearSearch() { searchOpen.value = false; searchQuery.value = ''; searchUsers.value = []; searchTickets.value = [] }

function statusLabel(s) {
  return { new: 'Новая', on_moderation: 'На модерации', in_progress: 'В работе', done: 'Завершено', cancelled: 'Отменено', closed: 'Закрыто' }[s] || s
}

function handleNotifClick(n) {
  showNotif.value = false
  if (n.action === 'open_friends') {
    if (window.__openFriendsSidebar) window.__openFriendsSidebar()
  }
}

function handleLogout() {
  showLogout.value = false
  auth.logout()
  menuOpen.value = false
  router.push('/')
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--nav-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--nav-border);
  padding: 0 24px;
  transition: background 0.3s, border-color 0.3s;
}

.nav-inner {
  max-width: 1040px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 60px;
  gap: 28px;
}

.nav-brand {
  font-weight: 800;
  font-size: 18px;
  color: var(--text) !important;
  text-decoration: none !important;
  letter-spacing: -0.3px;
}

.burger {
  display: none;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-card);
  cursor: pointer;
  align-items: center;
  justify-content: center;
  margin-left: auto;
  position: relative;
}

.burger span,
.burger span::before,
.burger span::after {
  display: block;
  width: 18px;
  height: 2px;
  background: var(--text-muted);
  border-radius: 2px;
  transition: all 0.3s;
  position: absolute;
  left: 50%;
  margin-left: -9px;
}

.burger span { top: 50%; margin-top: -1px; }
.burger span::before { content: ''; top: -6px; }
.burger span::after { content: ''; top: 6px; }
.burger span.open { background: transparent; }
.burger span.open::before { top: 0; transform: rotate(45deg); }
.burger span.open::after { top: 0; transform: rotate(-45deg); }

.nav-content {
  display: flex;
  align-items: center;
  gap: 28px;
  flex: 1;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-links a {
  color: var(--text-muted) !important;
  font-size: 14px;
  font-weight: 500;
  padding: 6px 0;
  text-decoration: none !important;
  position: relative;
  transition: color 0.2s;
}

.nav-links a::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--primary);
  border-radius: 2px;
  transition: width 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.nav-links a:hover {
  color: var(--primary) !important;
  text-decoration: none !important;
}

.nav-links a:hover::after {
  width: 100%;
}

.nav-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.theme-toggle:hover {
  background: var(--bg-hover);
  color: var(--primary);
  border-color: var(--primary);
}

.nav-user {
  font-size: 13px;
  color: var(--text-muted) !important;
  font-weight: 500;
  background: var(--bg-hover);
  padding: 4px 12px;
  border-radius: 6px;
  text-decoration: none !important;
  transition: background 0.2s, color 0.2s;
}

.nav-user:hover { background: var(--bg-input); color: var(--primary) !important; }

.btn-link {
  color: var(--primary) !important;
  font-weight: 600;
  font-size: 14px;
  padding: 6px 12px;
  text-decoration: none !important;
  border-radius: 8px;
  transition: background 0.2s;
}

.btn-link:hover {
  background: rgba(var(--primary-rgb), 0.06);
  text-decoration: none !important;
}

.btn-outline {
  background: transparent;
  color: var(--text) !important;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none !important;
  display: inline-flex;
  align-items: center;
  line-height: 1;
}

.btn-outline:hover {
  background: var(--bg-hover);
  border-color: var(--primary);
  color: var(--primary) !important;
  text-decoration: none !important;
}

.notif-btn { position: relative; display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-card); color: var(--text-muted); cursor: pointer; transition: all 0.2s; }
.notif-btn:hover { background: var(--bg-hover); color: var(--primary); border-color: var(--primary); }
.notif-badge { position: absolute; top: -4px; right: -4px; background: var(--danger); color: #fff; font-size: 9px; font-weight: 800; min-width: 16px; height: 16px; border-radius: 8px; display: flex; align-items: center; justify-content: center; padding: 0 4px; }
.notif-dropdown { position: absolute; top: 44px; right: 0; width: 300px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.12); z-index: 200; max-height: 400px; overflow-y: auto; }
.notif-item { padding: 10px 16px; border-bottom: 1px solid var(--border-light); display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.notif-item.unread { background: var(--bg-hover); }
.notif-item.clickable { cursor: pointer; }
.notif-item.clickable:hover { background: var(--bg-hover); }
.notif-item:last-child { border-bottom: none; }

.user-search { position: relative; }
.search-input {
  width: 160px; padding: 6px 10px; border: 1px solid var(--border); border-radius: 8px;
  background: var(--bg-input); color: var(--text); font-size: 12px; font-family: inherit;
  outline: none; transition: border-color 0.2s, width 0.2s;
}
.search-input:focus { border-color: var(--primary); width: 200px; }
.search-results {
  position: absolute; top: 40px; right: 0; width: 260px; background: var(--bg-card);
  border: 1px solid var(--border); border-radius: 10px; box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  z-index: 200; max-height: 300px; overflow-y: auto;
}
.search-result-item {
  display: flex; align-items: center; gap: 10px; padding: 8px 12px;
  border-bottom: 1px solid var(--border-light); text-decoration: none !important;
  transition: background 0.15s;
}
.search-result-item:hover { background: var(--bg-hover); }
.search-avatar { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }
.search-avatar-placeholder {
  width: 28px; height: 28px; border-radius: 50%; background: var(--primary);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 800; flex-shrink: 0;
}
.search-name { font-size: 13px; font-weight: 600; color: var(--text); }
.search-email { font-size: 11px; color: var(--text-dim); }

@media (max-width: 720px) {
  .burger { display: flex; }
  .nav-content {
    display: none;
    position: absolute;
    top: 60px;
    left: 0;
    right: 0;
    background: var(--nav-bg);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--nav-border);
    flex-direction: column;
    padding: 16px 24px;
    gap: 12px;
  }
  .nav-content.open { display: flex; }
  .nav-links { flex-direction: column; gap: 4px; }
  .nav-links a { padding: 8px 0; }
  .nav-links a::after { display: none; }
  .nav-right { margin-left: 0; width: 100%; justify-content: flex-start; flex-wrap: wrap; }
}
</style>
