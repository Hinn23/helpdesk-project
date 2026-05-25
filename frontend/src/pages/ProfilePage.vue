<template>
  <div class="profile-page">
    <div class="header-section">
      <h1>Профиль</h1>
    </div>
    <Loader v-if="loading" />
    <div v-else class="card" style="max-width: 500px; animation-delay: 0.1s;">
        <div class="profile-avatar">
        <div class="avatar-wrap">
          <img v-if="avatarUrl" :src="avatarUrl" class="avatar-img" alt="avatar" />
          <div v-else class="avatar-circle" :style="{ background: avatarColor }">{{ initials }}</div>
          <div class="avatar-actions">
            <button class="btn btn-secondary btn-xs" @click="$refs.avatarInput.click()" title="Загрузить аватар">
              <Upload :size="12" />
            </button>
            <button v-if="avatarUrl" class="btn btn-secondary btn-xs" @click="handleDeleteAvatar" title="Удалить аватар">
              <Trash2 :size="12" />
            </button>
          </div>
        </div>
        <div>
          <h2>{{ user.name }}</h2>
          <span class="badge" :class="'badge-' + (user.role === 'admin' ? 'high' : 'medium')">{{ roleLabel }}</span>
          <div style="margin-top: 8px; display: flex; gap: 16px; font-size: 14px;">
            <span style="color: var(--text-dim);">ID: {{ user.id }}</span>
            <span style="color: var(--text-dim);">Заявок: <strong style="color: var(--text);">{{ myTicketsCount }}</strong></span>
          </div>
        </div>
        <input ref="avatarInput" type="file" accept="image/png,image/jpeg,image/gif,image/webp" style="display:none" @change="handleAvatarUpload" />
      </div>

      <form @submit.prevent="handleSave" style="margin-top: 24px;">
        <ErrorMessage :message="error" />
        <div class="form-group">
          <label>Имя</label>
          <input v-model="form.name" class="form-control" required minlength="2" />
        </div>
        <div class="form-group">
          <label>Эл. почта</label>
          <input v-model="form.email" type="email" class="form-control" required />
        </div>
        <div style="display: flex; gap: 10px;">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Сохранение...' : 'Сохранить' }}
          </button>
        </div>
      </form>

      <hr style="margin: 28px 0; border-color: var(--border-light);" />

      <form @submit.prevent="handlePassword" style="margin-top: 4px;">
        <h3 style="margin-bottom: 16px;">Смена пароля</h3>
        <ErrorMessage :message="pwdError" />
        <div class="form-group">
          <label>Текущий пароль</label>
          <input v-model="pwdForm.current" type="password" class="form-control" required />
        </div>
        <div class="form-group">
          <label>Новый пароль</label>
          <input v-model="pwdForm.newPwd" type="password" class="form-control" required minlength="6" />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="pwdSaving">
          {{ pwdSaving ? 'Сохранение...' : 'Сменить пароль' }}
        </button>
      </form>

      <hr style="margin: 28px 0; border-color: var(--border-light);" />

      <div style="margin-bottom: 28px;">
        <h3 style="margin-bottom: 16px;">Подписки на пользователей ({{ userFollows.length }})</h3>
        <p v-if="followsLoading" style="color: var(--text-dim); font-size: 13px;">Загрузка...</p>
        <div v-else-if="!userFollows.length" style="color: var(--text-dim); font-size: 13px;">Вы ни на кого не подписаны. Зайдите в профиль пользователя и нажмите «Подписаться».</div>
        <div v-for="u in userFollows" :key="u.id" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border-light);">
          <div style="display: flex; align-items: center; gap: 10px;">
            <img v-if="u.avatar" :src="`/api/auth/${u.id}/avatar`" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;" />
            <div v-else class="mini-avatar" :style="{ background: getUserColor(u.name) }">{{ u.name.slice(0, 2).toUpperCase() }}</div>
            <router-link :to="`/users/${u.id}`" style="font-weight: 600;">{{ u.name }}</router-link>
            <span class="badge" :class="'badge-' + (u.role === 'admin' ? 'high' : 'medium')" style="font-size: 9px;">{{ u.role === 'admin' ? 'Админ' : 'Юзер' }}</span>
          </div>
          <button class="btn btn-secondary btn-xs" @click="handleUnfollowUser(u.id)">Отписаться</button>
        </div>
      </div>

      <hr style="margin: 28px 0; border-color: var(--border-light);" />

      <div>
        <h3 style="margin-bottom: 16px;">Подписки на заявки ({{ subscriptions.length }})</h3>
        <p v-if="subsLoading" style="color: var(--text-dim); font-size: 13px;">Загрузка...</p>
        <div v-else-if="!subscriptions.length" style="color: var(--text-dim); font-size: 13px;">Нет подписок. Подпишитесь на заявку, чтобы получать уведомления об изменениях.</div>
        <div v-for="s in subscriptions" :key="s.id" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border-light);">
          <div>
            <router-link :to="`/tasks/${s.ticket_id}`" style="font-weight: 600; font-size: 14px;">#{{ s.ticket_id }} {{ s.ticket_title }}</router-link>
            <span class="badge" :class="'badge-' + s.ticket_status" style="margin-left: 8px; font-size: 9px;">{{ statusLabel(s.ticket_status) }}</span>
          </div>
          <button class="btn btn-secondary btn-xs" @click="handleUnsubscribe(s.ticket_id)">Отписаться</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Upload, Trash2 } from 'lucide-vue-next'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import { authApi } from '../api/ticketsApi'
import api from '../api/axios'
import Loader from '../components/Loader.vue'
import ErrorMessage from '../components/ErrorMessage.vue'

const COLORS = ['#0d9488','#059669','#d97706','#dc2626','#7c3aed','#0891b2','#db2777','#2563eb']

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const user = ref(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const myTicketsCount = ref(0)
const subscriptions = ref([])
const subsLoading = ref(false)
const userFollows = ref([])
const followsLoading = ref(false)

function getUserColor(name) {
  let hash = 0
  for (const c of (name || '')) hash = c.charCodeAt(0) + ((hash << 5) - hash)
  return COLORS[Math.abs(hash) % COLORS.length]
}
const avatarUrl = ref('')

const form = ref({ name: '', email: '' })

const pwdForm = ref({ current: '', newPwd: '' })
const pwdSaving = ref(false)
const pwdError = ref('')

const initials = computed(() => {
  const name = user.value?.name || ''
  return name.slice(0, 2).toUpperCase()
})

const avatarColor = computed(() => {
  let hash = 0
  for (const c of (user.value?.name || '')) hash = c.charCodeAt(0) + ((hash << 5) - hash)
  return COLORS[Math.abs(hash) % COLORS.length]
})

const roleLabel = computed(() => {
  if (!user.value) return ''
  return user.value.role === 'admin' ? 'Администратор' : 'Пользователь'
})

onMounted(async () => {
  if (!auth.isAuthenticated) {
    router.push('/login')
    return
  }
  try {
    const data = await authApi.getMe()
    user.value = data
    form.value.name = data.name
    form.value.email = data.email
    if (data.avatar) avatarUrl.value = `/api/auth/${data.id}/avatar?t=${Date.now()}`
    const stats = await api.get('/auth/me/tickets').then(r => r.data)
    myTicketsCount.value = stats.total
    try {
      subsLoading.value = true
      const subs = await api.get('/subscriptions').then(r => r.data)
      subscriptions.value = subs
    } catch { /* подписки не критичны */ }
    finally { subsLoading.value = false }
    try {
      followsLoading.value = true
      const follows = await api.get(`/users/${user.value.id}/following`).then(r => r.data)
      userFollows.value = follows
    } catch { /* follows не критичны */ }
    finally { followsLoading.value = false }
  } catch {
    error.value = 'Не удалось загрузить профиль'
  } finally {
    loading.value = false
  }
})

async function handleSave() {
  error.value = ''
  saving.value = true
  try {
    const updated = await api.put('/auth/me', {
      name: form.value.name,
      email: form.value.email,
    }).then(r => r.data)
    user.value = updated
    toast.success('Профиль обновлён')
  } catch (e) {
    const d = e.response?.data?.detail
    error.value = Array.isArray(d) ? d.map(x => x.msg).join('; ') : (d || 'Ошибка сохранения')
  } finally {
    saving.value = false
  }
}

async function handlePassword() {
  pwdError.value = ''
  if (pwdForm.value.newPwd.length < 6) {
    pwdError.value = 'Пароль должен быть минимум 6 символов'
    return
  }
  pwdSaving.value = true
  try {
    await api.put('/auth/me/password', {
      current_password: pwdForm.value.current,
      new_password: pwdForm.value.newPwd,
    })
    toast.success('Пароль изменён')
    pwdForm.value = { current: '', newPwd: '' }
  } catch (e) {
    pwdError.value = e.response?.data?.detail || 'Ошибка смены пароля'
  } finally {
    pwdSaving.value = false
  }
}

function statusLabel(s) {
  return { new: 'Новая', on_moderation: 'На модерации', in_progress: 'В работе', done: 'Завершено', cancelled: 'Отменено' }[s] || s
}

async function handleUnsubscribe(ticketId) {
  try {
    await api.delete(`/tickets/${ticketId}/subscriptions`)
    subscriptions.value = subscriptions.value.filter(s => s.ticket_id !== ticketId)
    toast.success('Подписка отменена')
  } catch {
    toast.error('Ошибка при отписке')
  }
}

async function handleUnfollowUser(userId) {
  try {
    const resp = await api.post(`/users/${userId}/follow`)
    userFollows.value = userFollows.value.filter(u => u.id !== userId)
    toast.success('Отписка оформлена')
  } catch {
    toast.error('Ошибка при отписке')
  }
}

function validateImage(file) {
  return new Promise((resolve) => {
    if (file.size > 2 * 1024 * 1024) { toast.error('Файл больше 2 МБ'); resolve(false); return }
    if (!['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)) {
      toast.error('Разрешены только JPG, PNG, GIF, WebP'); resolve(false); return
    }
    const img = new Image()
    const url = URL.createObjectURL(file)
    img.onload = () => { URL.revokeObjectURL(url); resolve(true) }
    img.onerror = () => { URL.revokeObjectURL(url); toast.error('Файл не является изображением'); resolve(false) }
    img.src = url
  })
}

async function handleAvatarUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (!(await validateImage(file))) return
  const form = new FormData()
  form.append('file', file)
  try {
    const resp = await api.post('/auth/me/avatar', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    avatarUrl.value = `/api/auth/${user.value.id}/avatar?t=${Date.now()}`
    toast.success('Аватар обновлён')
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Ошибка загрузки')
  }
}

async function handleDeleteAvatar() {
  try {
    await api.delete('/auth/me/avatar')
    avatarUrl.value = ''
    toast.success('Аватар удалён')
  } catch {
    toast.error('Ошибка удаления')
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 600px;
  margin: 0 auto;
}

.profile-avatar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-light);
}

.avatar-wrap { position: relative; width: 56px; height: 56px; flex-shrink: 0; }
.avatar-wrap:hover .avatar-actions { opacity: 1; }
.avatar-actions {
  position: absolute; bottom: -4px; right: -8px; display: flex; gap: 2px;
  opacity: 0; transition: opacity 0.2s;
}
.avatar-img { width: 56px; height: 56px; border-radius: 50%; object-fit: cover; border: 2px solid var(--border); }
.avatar-circle {
  width: 56px; height: 56px; border-radius: 50%;
  background: var(--primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 800; flex-shrink: 0;
}
.mini-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 11px; font-weight: 800; flex-shrink: 0;
}

.profile-avatar h2 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
  color: var(--text);
}
</style>
