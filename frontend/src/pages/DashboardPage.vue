<template>
  <div>
    <div class="header-section"><h1>Дашборд</h1></div>
    <Loader v-if="loading" />
    <div v-else class="dashboard">
      <div class="stats-grid">
        <div v-motion :initial="{ opacity: 0, y: 16 }" :enter="{ opacity: 1, y: 0, transition: { delay: 0 } }" class="stat-card"><div class="stat-num">{{ total }}</div><div class="stat-label">Всего заявок</div></div>
        <div v-motion :initial="{ opacity: 0, y: 16 }" :enter="{ opacity: 1, y: 0, transition: { delay: 60 } }" class="stat-card" style="--sc: #059669;"><div class="stat-num">{{ stats.new }}</div><div class="stat-label">Новые</div></div>
        <div v-motion :initial="{ opacity: 0, y: 16 }" :enter="{ opacity: 1, y: 0, transition: { delay: 120 } }" class="stat-card" style="--sc: #d97706;"><div class="stat-num">{{ stats.on_moderation }}</div><div class="stat-label">На модерации</div></div>
        <div v-motion :initial="{ opacity: 0, y: 16 }" :enter="{ opacity: 1, y: 0, transition: { delay: 180 } }" class="stat-card" style="--sc: #2563eb;"><div class="stat-num">{{ stats.in_progress }}</div><div class="stat-label">В работе</div></div>
        <div v-motion :initial="{ opacity: 0, y: 16 }" :enter="{ opacity: 1, y: 0, transition: { delay: 240 } }" class="stat-card" style="--sc: #7c3aed;"><div class="stat-num">{{ stats.done }}</div><div class="stat-label">Завершено</div></div>
        <div v-motion :initial="{ opacity: 0, y: 16 }" :enter="{ opacity: 1, y: 0, transition: { delay: 300 } }" class="stat-card" style="--sc: #dc2626;"><div class="stat-num">{{ stats.cancelled }}</div><div class="stat-label">Отменено</div></div>
      </div>

      <div class="dashboard-grid">
        <div v-motion :initial="{ opacity: 0, y: 24 }" :visibleOnce="{ opacity: 1, y: 0, transition: { duration: 500 } }" class="card chart-card">
          <div class="card-header"><h2>По приоритетам</h2></div>
          <div class="bar-chart">
            <div v-for="b in bars" :key="b.label" class="bar-row">
              <span class="bar-label">{{ b.label }}</span>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: b.pct + '%', background: b.color }" :data-tip="b.count + ' (' + b.pct + '%)'"></div>
              </div>
              <span class="bar-value">{{ b.count }}</span>
            </div>
          </div>
        </div>

        <div v-motion :initial="{ opacity: 0, y: 24 }" :visibleOnce="{ opacity: 1, y: 0, transition: { duration: 500, delay: 100 } }" class="card chart-card">
          <div class="card-header"><h2>По статусам</h2></div>
          <div class="donut">
            <svg viewBox="0 0 42 42" class="donut-svg">
              <circle v-for="(s, i) in donutData" :key="i" cx="21" cy="21" r="15.9"
                :stroke="s.color" :stroke-dasharray="donutDash(s)"
                :stroke-dashoffset="donutOffset(i)" fill="none" stroke-width="3"
                class="donut-segment" />
            </svg>
            <div class="donut-center">{{ total }}</div>
          </div>
          <div class="donut-legend">
            <div v-for="s in donutData" :key="s.label" class="legend-item">
              <span class="legend-dot" :style="{ background: s.color }"></span>
              <span class="legend-label">{{ s.label }}</span>
              <span class="legend-value">{{ s.count }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="overdue.length" v-motion :initial="{ opacity: 0, y: 24 }" :visibleOnce="{ opacity: 1, y: 0, transition: { duration: 500, delay: 200 } }" class="card" style="margin-top: 24px; border-left: 3px solid var(--danger);">
        <h3 style="color: var(--danger); margin-bottom: 12px;">Просроченные заявки ({{ overdue.length }})</h3>
        <div v-for="t in overdue" :key="t.id" style="padding: 8px 0; border-bottom: 1px solid var(--border-light); display: flex; justify-content: space-between; align-items: center;">
          <router-link :to="`/tasks/${t.id}`" style="font-weight: 600;">#{{ t.id }} {{ t.title }}</router-link>
          <span style="color: var(--text-dim); font-size: 13px;">{{ daysOverdue(t.deadline) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ticketsApi } from '../api/ticketsApi'
import Loader from '../components/Loader.vue'

const loading = ref(true)
const total = ref(0)
const stats = ref({ new: 0, on_moderation: 0, in_progress: 0, done: 0, cancelled: 0 })
const overdue = ref([])
const priorities = ref({ low: 0, medium: 0, high: 0 })

function daysOverdue(d) {
  const diff = Math.floor((Date.now() - new Date(d)) / 86400000)
  return diff === 0 ? 'Сегодня' : `Просрочено на ${diff} дн.`
}

const bars = computed(() => {
  const max = Math.max(...Object.values(priorities.value), 1)
  const colors = { low: '#059669', medium: '#d97706', high: '#dc2626' }
  const labels = { low: 'Низкий', medium: 'Средний', high: 'Высокий' }
  return Object.entries(priorities.value).map(([k, v]) => ({
    label: labels[k], count: v, color: colors[k],
    pct: Math.round((v / max) * 100),
  }))
})

const donutData = computed(() => {
  const colors = { new: '#059669', on_moderation: '#d97706', in_progress: '#2563eb', done: '#7c3aed', cancelled: '#dc2626' }
  const labels = { new: 'Новые', on_moderation: 'На модерации', in_progress: 'В работе', done: 'Завершено', cancelled: 'Отменено' }
  return Object.entries(stats.value).filter(([_, v]) => v > 0).map(([k, v]) => ({
    label: labels[k], count: v, color: colors[k], key: k,
  }))
})

const circumference = 2 * Math.PI * 15.9

function donutDash(s) {
  const totalCount = donutData.value.reduce((a, b) => a + b.count, 0)
  return totalCount ? `${(s.count / totalCount) * circumference} ${circumference}` : `0 ${circumference}`
}

function donutOffset(i) {
  let offset = 0
  for (let j = 0; j < i; j++) {
    const totalCount = donutData.value.reduce((a, b) => a + b.count, 0)
    offset += totalCount ? (donutData.value[j].count / totalCount) * circumference : 0
  }
  return -offset
}

onMounted(async () => {
  try {
    const all = await ticketsApi.getList({ limit: 1 })
    total.value = all.total
    const statuses = ['new', 'on_moderation', 'in_progress', 'done', 'cancelled']
    for (const s of statuses) {
      const r = await ticketsApi.getList({ status: s, limit: 1 })
      stats.value[s] = r.total
    }
    for (const p of ['low', 'medium', 'high']) {
      const r = await ticketsApi.getList({ priority: p, limit: 1 })
      priorities.value[p] = r.total
    }
    const allTickets = await ticketsApi.getList({ limit: 100 })
    overdue.value = (allTickets.items || []).filter(t => t.deadline && new Date(t.deadline) < new Date() && t.status !== 'done' && t.status !== 'cancelled')
  } catch {}
  finally { loading.value = false }
})
</script>

<style scoped>
.stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; margin-bottom: 24px; }
.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}
.stat-num { font-size: 32px; font-weight: 800; color: var(--sc, var(--text)); }
.stat-label { font-size: 13px; color: var(--text-dim); margin-top: 4px; }

.dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 720px) { .dashboard-grid { grid-template-columns: 1fr; } }

.chart-card { padding: 20px; }

.bar-chart { display: flex; flex-direction: column; gap: 12px; }
.bar-row { display: flex; align-items: center; gap: 10px; }
.bar-label { width: 70px; font-size: 13px; color: var(--text-secondary); text-align: right; }
.bar-track { flex: 1; height: 20px; background: var(--bg-hover); border-radius: 10px; overflow: hidden; }
.bar-fill {
  height: 100%; border-radius: 10px;
  transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative; cursor: pointer;
}
.bar-fill:hover::after {
  content: attr(data-tip);
  position: absolute; top: -28px; left: 50%; transform: translateX(-50%);
  background: var(--text); color: var(--bg-card);
  padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 600;
  white-space: nowrap; z-index: 10;
}
.bar-value { width: 30px; font-size: 14px; font-weight: 700; color: var(--text); text-align: right; }

.donut { position: relative; width: 140px; height: 140px; margin: 0 auto 16px; }
.donut-svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.donut-segment { transition: stroke-dasharray 0.6s ease-out, stroke-width 0.2s, opacity 0.2s; cursor: pointer; }
.donut-segment:hover { stroke-width: 4; opacity: 0.8; }
.donut-center {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-size: 28px; font-weight: 800; color: var(--text);
}
.donut-legend { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 13px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }
.legend-label { color: var(--text-secondary); }
.legend-value { font-weight: 700; color: var(--text); }
</style>
