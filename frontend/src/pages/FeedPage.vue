<template>
  <div>
    <div class="header-section">
      <h1>Лента</h1>
    </div>

    <template v-if="loading">
      <div v-for="i in 5" :key="i" class="card feed-skeleton" style="margin-bottom: 12px;">
        <div style="display: flex; gap: 12px; align-items: center;">
          <div class="skeleton-circle"></div>
          <div style="flex: 1;"><div class="skeleton-line"></div><div class="skeleton-line" style="width: 60%;"></div></div>
        </div>
      </div>
    </template>

    <div v-else-if="!events.length" class="card empty-state">
      <h3>Лента пуста</h3>
      <p>Создайте первую заявку — и она появится здесь</p>
    </div>

    <div v-else class="feed-list">
      <div v-for="e in events" :key="e.id" class="feed-item card" :style="{ animationDelay: '0s' }">
        <div class="feed-icon" :class="'feed-' + e.type">
          <Plus v-if="e.type === 'ticket_created'" :size="16" />
          <MessageCircle v-else-if="e.type === 'comment'" :size="16" />
          <TrendingUp v-else :size="16" />
        </div>
        <div class="feed-body">
          <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;">
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <router-link v-if="e.user_id" :to="`/users/${e.user_id}`" class="feed-user">{{ e.user_name }}</router-link>
              <span v-else class="feed-user">{{ e.user_name }}</span>
              <span v-if="e.type === 'ticket_created'" class="feed-action">создал заявку</span>
              <span v-else-if="e.type === 'comment'" class="feed-action">прокомментировал</span>
              <span v-else-if="e.type === 'update' && e.action === 'created'" class="feed-action">создал заявку</span>
              <span v-else class="feed-action">изменил</span>
            </div>
            <span class="feed-time" :title="e.timestamp">{{ relativeTime(e.timestamp) }}</span>
          </div>

          <router-link v-if="e.ticket_title" :to="`/tasks/${e.ticket_id}`" class="feed-ticket">{{ e.ticket_title }}</router-link>
          <router-link v-else :to="`/tasks/${e.ticket_id}`" class="feed-ticket">#{{ e.ticket_id }}</router-link>

          <div v-if="e.type === 'comment' && e.text" class="feed-text">{{ e.text }}</div>

          <div v-if="e.type === 'update' && e.field && e.field !== 'subscription'" class="feed-changes">
            <span class="feed-field">{{ fieldLabel(e.field) }}:</span>
            <span class="feed-old">{{ e.old_value || '—' }}</span> → <span class="feed-new">{{ e.new_value }}</span>
          </div>

          <div v-if="e.type === 'update' && e.action === 'notified'" class="feed-text">{{ e.new_value }}</div>

          <div v-if="e.ticket_status" class="feed-badges">
            <span class="badge" :class="'badge-' + e.ticket_status">{{ statusLabel(e.ticket_status) }}</span>
            <span v-if="e.ticket_priority" class="badge" :class="'badge-' + e.ticket_priority">{{ priorityLabel(e.ticket_priority) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Plus, MessageCircle, TrendingUp } from 'lucide-vue-next'
import { ref, onMounted } from 'vue'
import api from '../api/axios'

const events = ref([])
const loading = ref(true)

function relativeTime(ts) {
  if (!ts) return ''
  const diff = Date.now() - new Date(ts).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'только что'
  if (mins < 60) return `${mins} мин. назад`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} ч. назад`
  const days = Math.floor(hours / 24)
  return `${days} дн. назад`
}

function statusLabel(s) { return { new: 'Новая', on_moderation: 'На модерации', in_progress: 'В работе', done: 'Завершено', cancelled: 'Отменено' }[s] || s }
function priorityLabel(p) { return { low: 'Низкий', medium: 'Средний', high: 'Высокий' }[p] || p }
function fieldLabel(f) { return { title: 'Название', status: 'Статус', priority: 'Приоритет', description: 'Описание', assignee_id: 'Исполнитель', category_id: 'Категория', deadline: 'Дедлайн' }[f] || f }

onMounted(async () => {
  try {
    const resp = await api.get('/feed?limit=50')
    events.value = resp.data
  } catch {}
  finally { loading.value = false }
})
</script>

<style scoped>
.feed-list { display: flex; flex-direction: column; gap: 10px; }
.feed-item { display: flex; gap: 14px; padding: 16px 20px; animation: none !important; }
.feed-icon {
  width: 36px; height: 36px; border-radius: 50%; display: flex;
  align-items: center; justify-content: center; flex-shrink: 0;
}
.feed-ticket_created { background: rgba(5, 150, 105, 0.1); color: #059669; }
.feed-comment { background: rgba(37, 99, 235, 0.1); color: #2563eb; }
.feed-update { background: rgba(217, 119, 6, 0.1); color: #d97706; }
.feed-body { flex: 1; min-width: 0; }
.feed-user { font-weight: 600; font-size: 14px; color: var(--primary); }
.feed-action { font-size: 13px; color: var(--text-muted); }
.feed-time { font-size: 11px; color: var(--text-dim); white-space: nowrap; }
.feed-ticket { display: block; font-weight: 700; font-size: 15px; margin: 4px 0; color: var(--text); }
.feed-ticket:hover { color: var(--primary); }
.feed-text { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
.feed-changes { font-size: 13px; margin-top: 4px; color: var(--text-muted); }
.feed-field { font-weight: 600; color: var(--text-secondary); }
.feed-old { color: var(--danger); text-decoration: line-through; }
.feed-new { color: var(--success, #059669); font-weight: 600; }
.feed-badges { display: flex; gap: 4px; margin-top: 6px; }

.feed-skeleton { padding: 16px 20px; }
.skeleton-circle { width: 36px; height: 36px; border-radius: 50%; background: var(--bg-hover); }
.skeleton-line { height: 12px; background: var(--bg-hover); border-radius: 6px; margin-bottom: 6px; }
</style>
