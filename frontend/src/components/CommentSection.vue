<template>
  <div class="card" style="margin-top: 24px; animation-delay: 0.2s;">
    <div class="card-header">
      <h2>Ответы персонала ({{ responses.length }})</h2>
    </div>
    <div v-if="!responses.length" class="empty-state" style="padding: 20px; color: var(--text-dim); font-size: 13px;">Нет ответов</div>
    <div v-for="(c, i) in responses" :key="c.id" class="comment response-box" :style="{ animationDelay: `${i * 0.05}s` }">
      <div class="comment-header">
        <div style="display: flex; align-items: center; gap: 8px; min-width: 0;">
          <router-link v-if="c.author_id" :to="`/users/${c.author_id}`" class="comment-author">{{ c.author_name }}</router-link>
          <span v-else class="comment-author">{{ c.author_name }}</span>
          <span class="response-badge">Ответ</span>
        </div>
        <span style="font-size: 12px; color: var(--text-dim); white-space: nowrap;">{{ formatDate(c.created_at) }}</span>
      </div>
      <p class="comment-text">{{ c.text }}</p>
      <div style="display: flex; align-items: center; gap: 12px;">
        <button v-if="auth.isAuthenticated" class="thanks-btn" :class="{ thanked: c.is_thanked }" @click="handleThanks(c)">
          <Heart :size="14" :fill="c.is_thanked ? 'currentColor' : 'none'" />
          <span>{{ c.thanks_count || 0 }}</span>
        </button>
        <button v-if="auth.isAdmin || String(c.author_id) === auth.userId" class="btn btn-danger" style="padding: 2px 8px; font-size: 11px;" @click="handleDelete(c.id)">Удалить</button>
      </div>
    </div>

    <hr style="margin: 20px 0; border-color: var(--border-light);" />

    <div class="card-header">
      <h2>Комментарии ({{ userComments.length }})</h2>
    </div>
    <div v-if="!userComments.length" class="empty-state" style="padding: 20px; color: var(--text-dim); font-size: 13px;">Комментариев пока нет</div>
    <div v-for="(c, i) in userComments" :key="c.id" class="comment" :style="{ animationDelay: `${i * 0.05}s` }">
      <div class="comment-header">
        <div style="display: flex; align-items: center; gap: 8px; min-width: 0;">
          <router-link v-if="c.author_id" :to="`/users/${c.author_id}`" class="comment-author">{{ c.author_name }}</router-link>
          <span v-else class="comment-author">{{ c.author_name }}</span>
          <span class="user-title" :style="{ color: titleColor(c.thanks_count || 0) }">{{ userTitle(c.thanks_count || 0) }}</span>
        </div>
        <span style="font-size: 12px; color: var(--text-dim); white-space: nowrap;">{{ formatDate(c.created_at) }}</span>
      </div>
      <p class="comment-text">{{ c.text }}</p>
      <div style="display: flex; align-items: center; gap: 12px;">
        <button v-if="auth.isAuthenticated" class="thanks-btn" :class="{ thanked: c.is_thanked }" @click="handleThanks(c)">
          <Heart :size="14" :fill="c.is_thanked ? 'currentColor' : 'none'" />
          <span>{{ c.thanks_count || 0 }}</span>
        </button>
        <span v-else class="thanks-count-only">{{ c.thanks_count || 0 }} спасибо</span>
        <button v-if="auth.isAdmin || String(c.author_id) === auth.userId" class="btn btn-danger" style="padding: 2px 8px; font-size: 11px;" @click="handleDelete(c.id)">Удалить</button>
        <button v-if="auth.isAuthenticated" class="btn btn-secondary" style="padding: 2px 8px; font-size: 11px;" @click="handleReply(c)">Ответить</button>
      </div>
    </div>
      <div v-if="auth.isAuthenticated" class="comment-form">
        <textarea v-model="newComment" class="form-control" rows="2" placeholder="Напишите комментарий..." @keydown.enter.ctrl="handleAdd" @input="autoResize"></textarea>
        <button class="btn btn-primary" @click="handleAdd" :disabled="!newComment.trim()">Отправить <span style="font-size: 11px; opacity: 0.6;">Ctrl+Enter</span></button>
      </div>
    <div v-else style="text-align: center; margin-top: 20px; padding: 20px; color: var(--text-dim); font-size: 14px;">
      <router-link to="/login">Войдите</router-link> чтобы оставлять комментарии
    </div>
  </div>
</template>

<script setup>
import { Heart } from 'lucide-vue-next'
import { ref, computed, onMounted } from 'vue'
import { commentsApi } from '../api/ticketsApi'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import api from '../api/axios'

const props = defineProps({ ticketId: { type: [Number, String], required: true } })
const auth = useAuthStore()
const toast = useToastStore()
const comments = ref([])
const newComment = ref('')

const responses = computed(() => comments.value.filter(c => c.is_response))
const userComments = computed(() => comments.value.filter(c => !c.is_response))

onMounted(() => loadComments())

async function loadComments() {
  try { comments.value = await commentsApi.getList(props.ticketId) } catch {}
}

async function handleAdd() {
  try {
    const c = await commentsApi.create(props.ticketId, { text: newComment.value })
    comments.value.push(c)
    newComment.value = ''
    toast.success('Комментарий добавлен')
  } catch {}
}

function handleReply(c) {
  const quote = c.text.split('\n').map(l => `> ${l}`).join('\n')
  newComment.value = `${quote}\n\n`
  import('vue').then(({ nextTick }) => {
    nextTick(() => {
      const ta = document.querySelector('.comment-form textarea')
      if (ta) { ta.focus(); ta.style.height = 'auto'; ta.style.height = ta.scrollHeight + 'px' }
    })
  })
}

async function handleDelete(id) {
  try {
    await commentsApi.delete(props.ticketId, id)
    comments.value = comments.value.filter(c => c.id !== id)
    toast.success('Комментарий удалён')
  } catch {}
}

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('ru-RU')
}

function userTitle(thanks) {
  if (thanks >= 50) return 'Легенда'
  if (thanks >= 20) return 'Старожил'
  if (thanks >= 10) return 'Активный'
  if (thanks >= 5) return 'Постоянный'
  if (thanks >= 1) return 'Новичок'
  return 'Новенький'
}
function titleColor(thanks) {
  if (thanks >= 50) return '#f59e0b'
  if (thanks >= 20) return '#8b5cf6'
  if (thanks >= 10) return '#3b82f6'
  if (thanks >= 5) return '#10b981'
  if (thanks >= 1) return '#6b7280'
  return '#9ca3af'
}

async function handleThanks(comment) {
  try {
    const resp = await api.post(`/tickets/${props.ticketId}/comments/${comment.id}/thanks`)
    comment.is_thanked = resp.data.thanked
    comment.thanks_count = resp.data.thanks_count
  } catch { toast.error('Ошибка') }
}
</script>

<style scoped>
.comment {
  background: var(--bg-input);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 10px;
  animation: fadeInUp 0.3s ease-out both;
  transition: border-color 0.2s, background 0.3s;
}

.comment:hover {
  border-color: var(--border);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-text {
  font-size: 14px;
  color: var(--text);
  margin-bottom: 8px;
  line-height: 1.5;
}

.comment-form {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  flex-direction: column;
}

.comment-author { font-weight: 700; font-size: 14px; color: var(--text); text-decoration: none; }
.comment-author:hover { color: var(--primary); text-decoration: underline; }
.user-title { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; white-space: nowrap; }
.thanks-btn {
  display: inline-flex; align-items: center; gap: 4px; padding: 2px 10px;
  border: 1px solid var(--border); border-radius: 6px; background: var(--bg-card);
  color: var(--text-muted); font-size: 12px; font-weight: 600; cursor: pointer;
  transition: all 0.2s; font-family: inherit;
}
.thanks-btn:hover { color: var(--danger); border-color: var(--danger); }
.thanks-btn.thanked { color: var(--danger); background: rgba(239,68,68,0.06); border-color: var(--danger); }
.thanks-count-only { font-size: 12px; color: var(--text-muted); }
.response-box { border-left: 3px solid var(--primary); background: rgba(var(--primary-rgb), 0.03); }
.response-badge { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; color: var(--primary); background: rgba(var(--primary-rgb), 0.1); padding: 1px 6px; border-radius: 4px; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
