<template>
  <div v-if="auth.isAuthenticated">
    <button class="sidebar-toggle" :class="{ 'has-requests': requests.length }" @click="toggle" :title="isOpen ? 'Скрыть' : 'Друзья'">
      <Users v-if="!isOpen" :size="16" />
      <X v-else :size="16" />
      <span v-if="requests.length" class="toggle-badge">{{ requests.length }}</span>
    </button>
    <Transition name="slide">
      <aside v-if="isOpen" class="friends-sidebar">
        <div v-if="requests.length" style="margin-bottom: 12px;">
          <div class="sidebar-header">
            <h3>Заявки</h3>
            <span class="friends-count" style="background: rgba(37,99,235,0.12); color: #2563eb;">{{ requests.length }}</span>
          </div>
          <div class="friends-list">
            <div v-for="r in requests" :key="r.id" class="request-item">
              <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
                <img v-if="r.avatar" :src="`/api/auth/${r.user_id}/avatar`" class="friend-avatar" />
                <div v-else class="friend-avatar-placeholder" :style="{ background: avatarColor(r.name) }">{{ r.name.slice(0, 2).toUpperCase() }}</div>
                <div class="friend-info" style="flex:1;">
                  <span class="friend-name">{{ r.name }}</span>
                  <span class="friend-meta">{{ roleBadge(r.role) }}</span>
                </div>
              </div>
              <div style="display: flex; gap: 2px; margin-top: 6px;">
                <button class="btn btn-primary btn-xs" style="flex:1; padding: 3px 6px; font-size: 11px;" @click="handleAccept(r.user_id)">Принять</button>
                <button class="btn btn-secondary btn-xs" style="padding: 3px 6px; font-size: 11px;" @click="handleReject(r.user_id)">✕</button>
                <button class="btn btn-danger btn-xs" style="padding: 3px 6px; font-size: 11px;" @click="handleBlock(r.user_id)" title="Заблокировать">🚫</button>
              </div>
            </div>
          </div>
          <hr style="margin: 12px 0; border-color: var(--border-light);" />
        </div>

        <div class="sidebar-header">
          <h3>Друзья</h3>
          <span class="friends-count">{{ friends.length }}</span>
        </div>
        <div v-if="loading" class="sidebar-loading">
          <div v-for="i in 3" :key="i" class="friend-skeleton">
            <div class="sk-avatar"></div>
            <div class="sk-name"></div>
          </div>
        </div>
        <div v-else-if="!friends.length" class="sidebar-empty">
          <Users :size="24" :strokeWidth="1.5" style="opacity: 0.3;" />
          <p>Добавьте друзей</p>
        </div>
        <div v-else class="friends-list">
          <div v-for="f in friends" :key="f.id" class="friend-item-wrap">
            <router-link :to="`/users/${f.id}`" class="friend-item" @contextmenu.prevent="openContextMenu($event, f)">
              <div class="friend-avatar-wrap">
                <img v-if="f.avatar" :src="`/api/auth/${f.id}/avatar`" class="friend-avatar" />
                <div v-else class="friend-avatar-placeholder" :style="{ background: avatarColor(f.name) }">{{ f.name.slice(0, 2).toUpperCase() }}</div>
              </div>
              <div class="friend-info">
                <span class="friend-name">{{ f.name }}</span>
                <span class="friend-meta">{{ roleBadge(f.role) }}</span>
              </div>
            </router-link>
          </div>
        </div>
      </aside>
    </Transition>

    <Teleport to="body">
      <div v-if="ctxMenu.visible" class="ctx-menu" :style="{ left: ctxMenu.x + 'px', top: ctxMenu.y + 'px' }" @click.stop @contextmenu.prevent>
        <div class="ctx-item" @click="handleRemoveFriend(ctxMenu.user.id); ctxMenu.visible = false">Удалить из друзей</div>
        <div class="ctx-item ctx-danger" @click="handleBlockFriend(ctxMenu.user.id); ctxMenu.visible = false">Заблокировать</div>
      </div>
      <div v-if="ctxMenu.visible" class="ctx-overlay" @click="ctxMenu.visible = false"></div>
    </Teleport>
  </div>
</template>

<script setup>
import { Users, X } from 'lucide-vue-next'
import { ref, onMounted, onUnmounted, onActivated } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import api from '../api/axios'

const toast = useToastStore()

const auth = useAuthStore()
const friends = ref([])
const requests = ref([])
const loading = ref(true)
const showConfirm = ref(false)
const isOpen = ref(false)
const ctxMenu = ref({ visible: false, x: 0, y: 0, user: null })

function toggle() { isOpen.value = !isOpen.value; if (isOpen.value) loadData() }

window.__openFriendsSidebar = () => { isOpen.value = true; loadData() }

const COLORS = ['#0d9488','#059669','#d97706','#dc2626','#7c3aed','#0891b2','#db2777','#2563eb']

function avatarColor(name) {
  let hash = 0
  for (const c of (name || '')) hash = c.charCodeAt(0) + ((hash << 5) - hash)
  return COLORS[Math.abs(hash) % COLORS.length]
}

function roleBadge(r) {
  return { admin: 'Админ', junior_admin: 'Мл.админ', moderator: 'Модератор', user: 'Пользователь' }[r] || r
}

function closeMobile() {
  // noop for now
}

async function loadData() {
  if (!auth.isAuthenticated) { loading.value = false; return }
  try {
    const [f, r] = await Promise.all([
      api.get('/friends').then(r => r.data),
      api.get('/friends/requests').then(r => r.data),
    ])
    friends.value = f
    requests.value = r
  } catch {}
  finally { loading.value = false }
}

async function handleAccept(userId) {
  try { await api.post(`/friends/${userId}/accept`); requests.value = requests.value.filter(r => r.user_id !== userId); toast.success('Заявка принята') } catch { toast.error('Ошибка') }
}
async function handleReject(userId) {
  try { await api.post(`/friends/${userId}/reject`); requests.value = requests.value.filter(r => r.user_id !== userId); toast.success('Заявка отклонена') } catch { toast.error('Ошибка') }
}
function openContextMenu(e, user) {
  ctxMenu.value = { visible: true, x: e.clientX, y: e.clientY, user }
}
async function handleRemoveFriend(userId) {
  try { await api.delete(`/friends/${userId}`); friends.value = friends.value.filter(f => f.id !== userId); toast.success('Удалён из друзей') } catch { toast.error('Ошибка') }
}
async function handleBlockFriend(userId) {
  try { await api.post(`/friends/${userId}/block`); friends.value = friends.value.filter(f => f.id !== userId); requests.value = requests.value.filter(r => r.user_id !== userId); toast.success('Заблокирован') } catch { toast.error('Ошибка') }
}
async function handleBlock(userId) {
  try { await api.post(`/friends/${userId}/block`); requests.value = requests.value.filter(r => r.user_id !== userId); toast.success('Пользователь заблокирован') } catch { toast.error('Ошибка') }
}

onMounted(loadData)
</script>

<style scoped>
.sidebar-toggle {
  position: fixed; left: 12px; bottom: 20px; z-index: 60;
  width: 40px; height: 40px; border-radius: 50%;
  border: 1px solid var(--border); background: var(--bg-card);
  color: var(--text-muted); cursor: pointer; display: flex;
  align-items: center; justify-content: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  transition: all 0.2s;
}
.ctx-menu {
  position: fixed; z-index: 9999; min-width: 200px;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 10px; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  padding: 4px; animation: fadeIn 0.1s ease-out;
}
.ctx-item {
  padding: 8px 12px; font-size: 13px; font-weight: 500; color: var(--text);
  border-radius: 6px; cursor: pointer; transition: background 0.1s;
}
.ctx-item:hover { background: var(--bg-hover); }
.ctx-danger { color: var(--danger); }
.ctx-danger:hover { background: rgba(239,68,68,0.08); }
.ctx-overlay { position: fixed; inset: 0; z-index: 9998; }

.sidebar-toggle:hover { color: var(--primary); border-color: var(--primary); }
.sidebar-toggle.has-requests { border-color: var(--primary); color: var(--primary); }
.toggle-badge {
  position: absolute; top: -4px; right: -4px;
  background: var(--danger); color: #fff; font-size: 9px; font-weight: 800;
  min-width: 16px; height: 16px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; padding: 0 4px;
}

.friends-sidebar {
  position: fixed;
  left: 0;
  top: 60px;
  bottom: 0;
  width: 220px;
  background: var(--bg-card);
  border-right: 1px solid var(--border);
  padding: 16px 12px;
  padding-bottom: 70px;
  overflow-y: auto;
  z-index: 50;
  display: flex;
  flex-direction: column;
  transition: background 0.3s, border-color 0.3s;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(-100%);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.sidebar-header h3 {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.friends-count {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-dim);
  background: var(--bg-hover);
  padding: 2px 8px;
  border-radius: 10px;
}

.friends-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.friend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 10px;
  text-decoration: none !important;
  transition: background 0.15s;
}

.friend-item:hover {
  background: var(--bg-hover);
}

.friend-avatar-wrap {
  position: relative;
  flex-shrink: 0;
}

.friend-avatar,
.friend-avatar-placeholder {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
}

.friend-avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
}

.friend-online {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid var(--bg-card);
  background: var(--text-dim);
}

.friend-online.online {
  background: #22c55e;
}

.friend-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.friend-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.friend-meta {
  font-size: 10px;
  color: var(--text-dim);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.friend-skeleton {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
}

.sk-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-hover);
}

.sk-name {
  flex: 1;
  height: 12px;
  border-radius: 6px;
  background: var(--bg-hover);
}

.sidebar-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 40px 12px;
  text-align: center;
}

.request-item { padding: 8px 10px; background: rgba(37,99,235,0.04); border-radius: 10px; margin-bottom: 6px; }
.sidebar-empty p {
  font-size: 12px;
  color: var(--text-dim);
}

@media (max-width: 860px) {
  .friends-sidebar {
    display: none;
  }
}
</style>
