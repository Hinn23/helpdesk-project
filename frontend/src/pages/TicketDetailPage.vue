<template>
  <div>
    <Loader v-if="loading" />
    <ErrorMessage v-else-if="error" :message="error" />
    <div v-else-if="ticket" class="detail">
      <div class="header-section">
        <h1>#{{ ticket.id }} {{ ticket.title }}</h1>
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
          <span v-if="authorName && ticket.author_id" class="badge" style="background: var(--bg-input); color: var(--text-muted); border: 1px solid var(--border-light);">Автор: <router-link :to="`/users/${ticket.author_id}`" style="font-weight: 600;">{{ authorName }}</router-link></span>
          <span v-if="ticket.deadline && isOverdue(ticket.deadline)" class="badge" style="background: rgba(220,38,38,0.12); color: var(--danger);">Просрочено на {{ overdueDays(ticket.deadline) }} дн.</span>
          <button v-if="auth.isAuthenticated" class="btn btn-secondary btn-xs" @click="handleToggleSubscribe">{{ subscribed ? 'Отписаться' : 'Подписаться' }}</button>
          <div v-if="auth.isAdmin || Number(auth.userId) === ticket.author_id">
            <router-link :to="`/tasks/${ticket.id}/edit`" class="btn btn-primary btn-sm" style="margin-right: 4px;">Редактировать</router-link>
            <button class="btn btn-danger btn-sm" @click="handleDelete">Удалить</button>
          </div>
        </div>
      </div>
      <div class="card" style="animation-delay: 0.1s;">
        <div style="display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap;">
          <span class="badge" :class="'badge-' + ticket.status">{{ statusLabel(ticket.status) }}</span>
          <span class="badge" :class="'badge-' + ticket.priority">{{ priorityLabel(ticket.priority) }}</span>
          <span v-if="categoryName" class="badge" style="background: var(--bg-input); color: var(--text-muted); border: 1px solid var(--border-light);">{{ categoryName }}</span>
        </div>
        <div style="margin-bottom: 24px;">
          <div style="font-size: 11px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; margin-bottom: 8px;">Описание</div>
          <p style="font-size: 15px; line-height: 1.7; color: var(--text);">{{ ticket.description || 'Нет описания' }}</p>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding-top: 20px; border-top: 1px solid var(--border-light); font-size: 13px;">
          <div><span style="color: var(--text-dim);">Создан:</span> {{ formatDate(ticket.created_at) }}</div>
          <div><span style="color: var(--text-dim);">Обновлён:</span> {{ formatDate(ticket.updated_at) }}</div>
          <div v-if="assigneeName && ticket.assignee_id"><span style="color: var(--text-dim);">Исполнитель:</span> <router-link :to="`/users/${ticket.assignee_id}`">{{ assigneeName }}</router-link></div>
          <div v-if="ticket.deadline"><span style="color: var(--text-dim);">Дедлайн:</span> <span :style="{ color: isOverdue(ticket.deadline) ? 'var(--danger)' : 'inherit', fontWeight: isOverdue(ticket.deadline) ? 700 : 'inherit' }">{{ formatDate(ticket.deadline) }}</span></div>
        </div>
      </div>

      <div class="card" style="margin-top: 16px;">
        <div class="card-header"><h2>Файлы ({{ attachments.length }})</h2></div>
        <div v-if="auth.isAuthenticated" style="margin-bottom: 12px;">
          <input type="file" ref="fileInput" style="display:none" @change="handleFileUpload" />
          <button class="btn btn-secondary btn-sm" @click="$refs.fileInput.click()">+ Прикрепить файл</button>
        </div>
        <div v-if="!attachments.length" style="color: var(--text-dim); font-size: 13px;">Нет прикреплённых файлов</div>
        <div v-for="att in attachments" :key="att.id" style="padding: 8px 0; border-bottom: 1px solid var(--border-light);">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <a :href="`/api/tickets/${ticket.id}/attachments/${att.id}`" target="_blank" style="font-size: 13px; font-weight: 600;">{{ att.original_name }}</a>
            <span style="font-size: 11px; color: var(--text-dim);">{{ (att.file_size / 1024).toFixed(1) }} KB</span>
          </div>
          <a v-if="isImage(att.original_name)" style="display: block; margin-top: 6px; cursor: zoom-in;" @click="openLightbox(`/api/tickets/${ticket.id}/attachments/${att.id}`)">
            <img :src="`/api/tickets/${ticket.id}/attachments/${att.id}`" class="attachment-preview" :alt="att.original_name" />
          </a>
        </div>
      </div>

      <div class="card" style="margin-top: 16px;">
        <div class="card-header"><h2>История изменений</h2></div>
        <div v-if="!history.length" style="color: var(--text-dim); font-size: 13px;">История пуста</div>
        <div v-for="h in history" :key="h.id" style="padding: 6px 0; border-bottom: 1px solid var(--border-light); font-size: 13px; display: flex; gap: 8px;">
          <span style="color: var(--text-dim); white-space: nowrap;">{{ formatTime(h.created_at) }}</span>
          <span style="font-weight: 600;">{{ h.user_name || 'system' }}</span>
          <span v-if="h.action === 'created'">создал(а) заявку</span>
          <span v-else-if="h.action === 'notified'">{{ h.new_value }}</span>
          <span v-else>
            изменил(а) <em>{{ fieldLabel(h.field) }}</em>:
            <span style="color: var(--text-dim);">{{ h.old_value || '—' }}</span> &rarr;
            <span style="font-weight: 600;">{{ h.new_value }}</span>
          </span>
        </div>
      </div>

      <CommentSection :ticket-id="ticket.id" />
      <Lightbox :visible="lbVisible" :src="lbSrc" @update:visible="lbVisible = $event" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ticketsApi, categoriesApi, usersApi } from '../api/ticketsApi'
import api from '../api/axios'
import { useAuthStore } from '../stores/auth'
import Loader from '../components/Loader.vue'
import ErrorMessage from '../components/ErrorMessage.vue'
import CommentSection from '../components/CommentSection.vue'
import Lightbox from '../components/Lightbox.vue'
import { useToastStore } from '../stores/toast'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const ticket = ref(null)
const loading = ref(true)
const error = ref('')
const categoryName = ref('')
const authorName = ref('')
const assigneeName = ref('')
const toast = useToastStore()
const subscribed = ref(false)
const attachments = ref([])
const history = ref([])
const fileInput = ref(null)
const lbVisible = ref(false)
const lbSrc = ref('')
function openLightbox(src) { lbSrc.value = src; lbVisible.value = true }

onMounted(async () => {
  try {
    const t = await ticketsApi.getById(route.params.id)
    ticket.value = t
    try {
      const [cats, users] = await Promise.all([
        categoriesApi.getList(),
        usersApi.getList(),
      ])
      if (t.category_id) {
        const c = cats.find(c => c.id === t.category_id)
        if (c) categoryName.value = c.name
      }
      if (t.author_id) {
        const u = users.find(u => u.id === t.author_id)
        if (u) authorName.value = u.name
      }
      if (t.assignee_id) {
        const u = users.find(u => u.id === t.assignee_id)
        if (u) assigneeName.value = u.name
      }
    } catch {}
    if (auth.isAuthenticated) {
      try {
        const r = await api.get(`/tickets/${route.params.id}/subscriptions`)
        subscribed.value = r.data.subscribed
      } catch {}
    }
    try {
      const r = await api.get(`/tickets/${route.params.id}/attachments`)
      attachments.value = r.data
    } catch {}
    try {
      const r = await api.get(`/tickets/${route.params.id}/history`)
      history.value = r.data
    } catch {}
  } catch {
    error.value = 'Заявка не найдена'
  }
  finally { loading.value = false }
})

async function handleDelete() {
  if (!confirm('Удалить эту заявку?')) return
  try {
    await ticketsApi.delete(ticket.value.id)
    toast.success('Заявка удалена')
    router.push('/tasks')
  } catch { error.value = 'Ошибка удаления' }
}

async function handleToggleSubscribe() {
  try {
    if (subscribed.value) {
      await api.delete(`/tickets/${route.params.id}/subscriptions`)
      subscribed.value = false
      toast.success('Отписались')
    } else {
      await api.post(`/tickets/${route.params.id}/subscriptions`)
      subscribed.value = true
      toast.success('Подписались')
    }
  } catch { toast.error('Ошибка') }
}

async function handleFileUpload() {
  const file = fileInput.value?.files?.[0]
  if (!file) return
  const form = new FormData()
  form.append('file', file)
  try {
    await api.post(`/tickets/${ticket.value.id}/attachments`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    toast.success('Файл загружен')
    const r = await api.get(`/tickets/${ticket.value.id}/attachments`)
    attachments.value = r.data
  } catch { toast.error('Ошибка загрузки файла') }
  fileInput.value.value = ''
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('ru-RU')
}

function formatTime(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function isOverdue(d) { return new Date(d) < new Date() }
function overdueDays(d) { return Math.floor((Date.now() - new Date(d)) / 86400000) }

function isImage(name) { return /\.(jpg|jpeg|png|gif|webp)$/i.test(name) }
function statusLabel(s) {
  return { new: 'Новая', on_moderation: 'На модерации', in_progress: 'В работе', done: 'Завершено', cancelled: 'Отменено' }[s] || s
}
function priorityLabel(p) {
  return { low: 'Низкий', medium: 'Средний', high: 'Высокий' }[p] || p
}
function fieldLabel(f) {
  return { title: 'Название', status: 'Статус', priority: 'Приоритет', description: 'Описание', assignee_id: 'Исполнитель', deadline: 'Дедлайн' }[f] || f
}
</script>

<style scoped>
.attachment-preview { max-width: 100%; max-height: 300px; border-radius: 8px; object-fit: contain; background: var(--bg-input); cursor: zoom-in; transition: opacity 0.2s; }
.attachment-preview:hover { opacity: 0.85; }
</style>
