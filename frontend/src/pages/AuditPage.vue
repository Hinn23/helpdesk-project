<template>
  <div>
    <div class="header-section"><h1>Журнал действий</h1></div>
    <p v-if="loading" style="color: var(--text-dim);">Загрузка...</p>
    <p v-else-if="error" style="color: var(--danger);">{{ error }}</p>
    <p v-else-if="!logs.length" style="color: var(--text-dim);">Нет записей</p>
    <div v-for="l in logs" :key="l.id" class="card" style="margin-bottom: 8px; padding: 12px 16px;">
      <div style="display: flex; justify-content: space-between; font-size: 13px;">
        <div>
          <strong>{{ l.user_name }}</strong>
          <span style="color: var(--text-muted);">
            <template v-if="l.action === 'created'">создал заявку #{{ l.ticket_id }}</template>
            <template v-else-if="l.action === 'changed'">изменил {{ fieldLabel(l.field) }} в #{{ l.ticket_id }}: <span style="color: var(--danger); text-decoration: line-through;">{{ l.old_value }}</span> → <span style="color: #059669; font-weight: 600;">{{ l.new_value }}</span></template>
            <template v-else-if="l.action === 'notified'">{{ l.new_value }}</template>
            <template v-else>{{ l.action }} #{{ l.ticket_id }}</template>
          </span>
        </div>
        <span style="color: var(--text-dim); font-size: 11px;">{{ formatTime(l.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/axios'

const logs = ref([])
const loading = ref(true)
const error = ref('')
function fieldLabel(f) { return { title: 'Название', status: 'Статус', priority: 'Приоритет', description: 'Описание', assignee_id: 'Исполнитель', category_id: 'Категория', deadline: 'Дедлайн' }[f] || f }
function formatTime(ts) { if (!ts) return ''; return new Date(ts).toLocaleString('ru-RU') }

onMounted(async () => {
  try { const r = await api.get('/admin/users/audit'); logs.value = r.data; error.value = '' } catch (e) { error.value = 'Ошибка загрузки: ' + (e.response?.status || e.message) }
  finally { loading.value = false }
})
</script>
