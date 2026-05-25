<template>
  <div class="user-page">
    <Loader v-if="loading" />
    <ErrorMessage v-else-if="error" :message="error" />
    <div v-else-if="profile" class="user-content">
      <div class="card user-header">
        <div class="user-avatar-section">
          <img v-if="profile.avatar" :src="`/api/auth/${profile.id}/avatar`" class="user-avatar-img" />
          <div v-else class="user-avatar-placeholder" :style="{ background: avatarColor }">{{ initials }}</div>
          <div class="user-info">
            <h1>{{ profile.name }}</h1>
            <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 6px;">
              <span class="badge" :class="'badge-' + (profile.role === 'admin' ? 'high' : 'medium')">{{ roleLabel(profile.role) }}</span>
              <span v-if="profile.status === 'banned'" class="badge" style="background: rgba(220,38,38,0.15); color: #dc2626;">Заблокирован</span>
              <span v-if="profile.status === 'warned'" class="badge" style="background: rgba(217,119,6,0.15); color: #d97706;">Предупреждение</span>
            </div>
            <div class="user-stats">
              <span>Заявок: <strong>{{ profile.tickets_count }}</strong></span>
              <span>Друзей: <strong>{{ profile.friends_count }}</strong></span>
              <span>❤ <strong>{{ profile.thanks_count }}</strong></span>
            </div>
          </div>
        </div>
        <div style="display: flex; gap: 6px; flex-wrap: wrap;">
          <template v-if="auth.isAuthenticated && profile.id !== auth.userIdAsNumber">
            <template v-if="profile.has_blocked">
              <button class="btn btn-secondary btn-sm" @click="handleUnblock">Разблокировать</button>
            </template>
            <template v-else>
              <button v-if="!isFriend" class="btn btn-primary btn-sm" @click="handleAddFriend">+ Друзья</button>
              <button v-if="isFriend" class="btn btn-secondary btn-sm" @click="handleRemoveFriend">В друзьях ✓</button>
              <button class="btn btn-secondary btn-sm" :class="profile.is_following ? 'btn-secondary' : 'btn-primary'" @click="handleToggleFollow">{{ profile.is_following ? 'Отписаться' : 'Подписаться' }}</button>
              <button class="btn btn-secondary btn-sm" @click="handleMessage">Написать</button>
              <button class="btn btn-danger btn-sm" @click="handleBlockUser">Заблокировать</button>
            </template>
          </template>
        </div>
      </div>

      <div v-if="auth.isAuthenticated && (auth.userRole === 'admin' || auth.userRole === 'junior_admin' || auth.userRole === 'moderator') && profile.id !== auth.userIdAsNumber" class="card" style="margin-top: 16px; border-left: 3px solid var(--primary);">
        <div class="card-header"><h2>Управление</h2></div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <template v-if="auth.userRole === 'admin'">
            <select v-model="adminRole" class="form-control" style="width: auto; padding: 4px 10px; font-size: 12px;">
              <option value="user">Пользователь</option>
              <option value="moderator">Модератор</option>
              <option value="junior_admin">Младший админ</option>
              <option value="admin">Админ</option>
            </select>
            <button class="btn btn-primary btn-xs" @click="handleSetRole">Сменить роль</button>
          </template>
          <button v-if="auth.userRole !== 'moderator'" class="btn btn-secondary btn-xs" @click="handleWarn">Выдать предупреждение</button>
          <button v-if="auth.userRole !== 'moderator' && profile.status !== 'banned'" class="btn btn-danger btn-xs" @click="handleBan">Заблокировать</button>
          <button v-if="auth.userRole !== 'moderator' && profile.status === 'banned'" class="btn btn-success btn-xs" @click="handleUnban">Разблокировать</button>
        </div>
        <div v-if="profile.warnings_count" style="margin-top: 10px;">
          <div style="font-size: 13px; color: var(--text-dim); margin-bottom: 8px;">Предупреждений: {{ profile.warnings_count }}</div>
          <button class="btn btn-xs btn-secondary" @click="showWarnings = !showWarnings">{{ showWarnings ? 'Скрыть историю' : 'Показать историю предупреждений' }}</button>
          <div v-if="showWarnings && warnings.length">
            <div v-for="w in warnings" :key="w.id" style="padding: 8px 10px; margin-top: 8px; border: 1px solid var(--border-light); border-radius: 8px; font-size: 13px;">
              <div style="display: flex; justify-content: space-between;">
                <span style="color: var(--text-dim);">{{ formatDate(w.created_at) }}</span>
                <span style="font-weight: 600;">от {{ w.admin_name || '#'+w.admin_id }}</span>
              </div>
              <div style="margin-top: 4px;">{{ w.reason }}</div>
            </div>
            <div v-if="!warnings.length" style="margin-top: 8px; font-size: 13px; color: var(--text-dim);">Нет предупреждений</div>
          </div>
        </div>
      </div>

      <div class="card" style="margin-top: 16px;">
        <div class="card-header"><h2>Заявки пользователя ({{ profile.tickets.length }})</h2></div>
        <div v-if="!profile.tickets.length" style="color: var(--text-dim); font-size: 13px; padding: 12px 0;">Нет заявок</div>
        <div v-for="t in profile.tickets" :key="t.id" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border-light);">
          <router-link :to="`/tasks/${t.id}`" style="font-weight: 600;">#{{ t.id }} {{ t.title }}</router-link>
          <div style="display: flex; gap: 6px;">
            <span class="badge" :class="'badge-' + t.status" style="font-size: 9px;">{{ statusLabel(t.status) }}</span>
            <span class="badge" :class="'badge-' + t.priority" style="font-size: 9px;">{{ priorityLabel(t.priority) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import Loader from '../components/Loader.vue'
import ErrorMessage from '../components/ErrorMessage.vue'

const COLORS = ['#0d9488','#059669','#d97706','#dc2626','#7c3aed','#0891b2','#db2777','#2563eb']

const route = useRoute()
const auth = useAuthStore()
const toast = useToastStore()

const profile = ref(null)
const loading = ref(true)
const error = ref('')

const initials = computed(() => (profile.value?.name || '').slice(0, 2).toUpperCase())
const avatarColor = computed(() => {
  let hash = 0
  for (const c of (profile.value?.name || '')) hash = c.charCodeAt(0) + ((hash << 5) - hash)
  return COLORS[Math.abs(hash) % COLORS.length]
})

const isFriend = ref(false)
const adminRole = ref('user')
const showWarnings = ref(false)
const warnings = ref([])

function statusLabel(s) { return { new: 'Новая', on_moderation: 'На модерации', in_progress: 'В работе', done: 'Завершено', cancelled: 'Отменено' }[s] || s }
function priorityLabel(p) { return { low: 'Низкий', medium: 'Средний', high: 'Высокий'}[p] || p }
function roleLabel(r) { return { admin: 'Администратор', junior_admin: 'Мл. админ', moderator: 'Модератор', user: 'Пользователь' }[r] || r }
function formatDate(d) { if (!d) return ''; return new Date(d).toLocaleString('ru-RU') }

async function loadWarnings() {
  try {
    const r = await api.get(`/admin/users/${route.params.id}/warnings`)
    warnings.value = r.data
  } catch {}
}

onMounted(async () => {
  try {
    const resp = await api.get(`/users/${route.params.id}/profile`)
    profile.value = resp.data
    isFriend.value = resp.data.is_friend
    adminRole.value = resp.data.role
  } catch (e) { error.value = e.response?.data?.detail || 'Пользователь не найден' }
  finally { loading.value = false }
})

watch(showWarnings, (v) => { if (v) loadWarnings() })

async function handleAddFriend() {
  try { await api.post(`/friends/${profile.value.id}`); isFriend.value = true; toast.success('Друг добавлен') }
  catch { toast.error('Ошибка') }
}
async function handleRemoveFriend() {
  try { await api.delete(`/friends/${profile.value.id}`); isFriend.value = false; toast.success('Друг удалён') }
  catch { toast.error('Ошибка') }
}
async function handleUnblock() {
  try { await api.post(`/friends/${profile.value.id}/unblock`); profile.value.has_blocked = false; toast.success('Пользователь разблокирован') }
  catch { toast.error('Ошибка') }
}
async function handleBlockUser() {
  try { await api.post(`/friends/${profile.value.id}/block`); profile.value.has_blocked = true; toast.success('Пользователь заблокирован') }
  catch (e) { toast.error(e.response?.data?.detail || 'Ошибка') }
}
function handleMessage() {
  if (window.__openMessages) window.__openMessages(profile.value.id, profile.value.name)
}
async function handleSetRole() {
  try { await api.put(`/admin/users/${profile.value.id}/role`, { role: adminRole.value }); toast.success('Роль изменена') }
  catch { toast.error('Ошибка') }
}
async function handleWarn() {
  const reason = prompt('Причина предупреждения:')
  if (!reason) return
  try { await api.post(`/admin/users/${profile.value.id}/warn`, { reason }); toast.success('Предупреждение выдано'); profile.value.warnings_count++ }
  catch { toast.error('Ошибка') }
}
async function handleBan() {
  try { await api.put(`/admin/users/${profile.value.id}/status`, { status: 'banned' }); profile.value.status = 'banned'; toast.success('Пользователь заблокирован') }
  catch { toast.error('Ошибка') }
}
async function handleUnban() {
  try { await api.put(`/admin/users/${profile.value.id}/status`, { status: 'active' }); profile.value.status = 'active'; toast.success('Пользователь разблокирован') }
  catch { toast.error('Ошибка') }
}

async function handleToggleFollow() {
  try {
    const resp = await api.post(`/users/${profile.value.id}/follow`)
    profile.value.is_following = resp.data.following
    profile.value.followers_count += resp.data.following ? 1 : -1
    toast.success(resp.data.message)
  } catch { toast.error('Ошибка') }
}
</script>

<style scoped>
.user-page { max-width: 700px; margin: 0 auto; }
.user-header {
  display: flex; justify-content: space-between; align-items: flex-start; gap: 16px;
}
.user-avatar-section { display: flex; gap: 20px; align-items: center; }
.user-avatar-img { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; border: 2px solid var(--border); }
.user-avatar-placeholder {
  width: 64px; height: 64px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 24px; font-weight: 800; flex-shrink: 0;
}
.user-info h1 { font-size: 22px; font-weight: 800; margin-bottom: 4px; color: var(--text); }
.user-stats { display: flex; gap: 16px; margin-top: 8px; font-size: 13px; color: var(--text-muted); }
.user-stats strong { color: var(--text); }
</style>
