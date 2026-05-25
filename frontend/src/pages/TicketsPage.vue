<template>
  <div>
    <div class="header-section">
      <h1>Заявки</h1>
      <div class="header-actions">
        <button v-if="auth.isAdmin" class="btn btn-secondary btn-xs" @click="handleExportCSV" :disabled="exportingCSV" title="Экспорт в CSV">
          <span v-if="exportingCSV" class="spinner"></span>
          <Download v-else :size="14" />
          CSV
        </button>
        <button v-if="auth.isAdmin" class="btn btn-secondary btn-xs" @click="handleExportXLSX" :disabled="exportingXLSX" title="Экспорт в Excel">
          <span v-if="exportingXLSX" class="spinner"></span>
          <XSquare v-else :size="14" />
          XLSX
        </button>
        <button class="btn btn-secondary btn-xs" @click="toggleView" :title="viewMode === 'table' ? 'Канбан' : 'Таблица'">
          <LayoutGrid v-if="viewMode === 'table'" :size="14" />
          <Table v-else :size="14" />
          {{ viewMode === 'table' ? 'Канбан' : 'Таблица' }}
        </button>
        <button class="btn btn-secondary btn-xs" :class="{ 'btn-primary': autoRefresh }" @click="autoRefresh = !autoRefresh" :title="autoRefresh ? 'Автообновление включено' : 'Автообновление выключено'">
          <RefreshCw :size="14" />
        </button>
        <router-link v-if="auth.isAuthenticated" to="/tasks/create" class="btn btn-primary">+ Новая заявка</router-link>
      </div>
    </div>

    <div class="tabs" style="display: flex; gap: 4px; margin-bottom: 12px; align-items: center;">
      <button class="btn btn-xs" :class="activeTab === 'all' ? 'btn-primary' : 'btn-secondary'" @click="setTab('all')">Все</button>
      <button v-if="auth.isAuthenticated" class="btn btn-xs" :class="activeTab === 'mine' ? 'btn-primary' : 'btn-secondary'" @click="setTab('mine')">Мои заявки</button>
      <button v-if="auth.isAdmin" class="btn btn-xs" :class="activeTab === 'moderation' ? 'btn-primary' : 'btn-secondary'" @click="setTab('moderation')">На модерации</button>
      <button v-if="auth.isAdmin" class="btn btn-xs btn-secondary" @click="setQuickFilter('today')" :class="{ 'btn-primary': quickFilter === 'today' }">Сегодня</button>
      <button v-if="auth.isAdmin" class="btn btn-xs btn-secondary" @click="setQuickFilter('overdue')" :class="{ 'btn-primary': quickFilter === 'overdue' }">Просроченные</button>
      <button v-if="auth.isAdmin" class="btn btn-xs btn-secondary" @click="showWorkflow = !showWorkflow" style="margin-left: auto;">{{ showWorkflow ? 'Скрыть воркфлоу' : 'Воркфлоу' }}</button>
    </div>
    <div v-if="showWorkflow && auth.isAdmin" class="card workflow-box" style="margin-bottom: 16px; padding: 14px 18px;">
      <div style="font-size: 13px; font-weight: 600; margin-bottom: 8px;">Статус-воркфлоу</div>
      <div class="workflow-steps">
        <div class="wf-step"><span class="badge badge-on_moderation">На модерации</span></div>
        <ChevronRight :size="16" color="var(--text-dim)" :strokeWidth="1.5" />
        <div class="wf-step"><span class="badge badge-new">Новая</span></div>
        <ChevronRight :size="16" color="var(--text-dim)" :strokeWidth="1.5" />
        <div class="wf-step"><span class="badge badge-in_progress">В работе</span></div>
        <ChevronRight :size="16" color="var(--text-dim)" :strokeWidth="1.5" />
        <div class="wf-step"><span class="badge badge-done">Завершено</span></div>
        <div style="margin: 0 4px; color: var(--text-dim);">|</div>
        <div class="wf-step"><span class="badge badge-cancelled">Отменено</span></div>
        <div style="margin: 0 4px; color: var(--text-dim);">|</div>
        <div class="wf-step"><span class="badge badge-closed">Закрыто</span></div>
      </div>
    </div>
    <div class="filters card" style="margin-bottom: 20px;">
      <div class="form-group">
        <label>Поиск</label>
        <input v-model="filters.search" class="form-control" placeholder="Поиск заявок... (#ID для поиска по номеру)" @input="debouncedSearch" />
      </div>
      <div class="form-group">
        <label>Статус</label>
        <select v-model="filters.status" class="form-control" @change="debouncedFilter">
          <option value="">Все</option>
          <option value="new">Новая</option>
          <option v-if="auth.isAdmin" value="on_moderation">На модерации</option>
          <option value="in_progress">В работе</option>
          <option value="done">Завершено</option>
        <option value="cancelled">Отменено</option>
        <option value="closed">Закрыто</option>
          </select>
        </div>
      <div class="form-group">
        <label>Приоритет</label>
        <select v-model="filters.priority" class="form-control" @change="debouncedFilter">
          <option value="">Все</option>
          <option value="low">Низкий</option>
          <option value="medium">Средний</option>
          <option value="high">Высокий</option>
        </select>
      </div>
      <div class="form-group">
        <label>Дата с</label>
        <input v-model="filters.date_from" type="date" class="form-control" @change="debouncedFilter" />
      </div>
      <div class="form-group">
        <label>Дата по</label>
        <input v-model="filters.date_to" type="date" class="form-control" @change="debouncedFilter" />
      </div>
    </div>

    <div v-if="auth.isAdmin && selectedIds.size > 0" class="bulk-bar">
      <span style="font-size: 13px; color: var(--text-secondary);">Выбрано: {{ selectedIds.size }}</span>
      <select v-model="bulkStatus" class="form-control" style="width: auto; padding: 4px 10px; font-size: 12px;">
        <option value="">— Статус —</option>
        <option value="new">Новая</option>
        <option value="in_progress">В работе</option>
        <option value="done">Завершено</option>
        <option value="cancelled">Отменено</option>
        <option value="closed">Закрыто</option>
      </select>
      <select v-model="bulkCategory" class="form-control" style="width: auto; padding: 4px 10px; font-size: 12px;">
        <option value="">— Категория —</option>
        <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <select v-model="bulkAssignee" class="form-control" style="width: auto; padding: 4px 10px; font-size: 12px;">
        <option value="">— Исполнитель —</option>
        <option v-for="u in users" :key="u.id" :value="u.id">{{ u.name }}</option>
      </select>
      <button class="btn btn-primary btn-xs" @click="handleBulkEdit">Применить</button>
      <button class="btn btn-danger btn-xs" @click="handleBulkDelete">Удалить</button>
      <button class="btn btn-secondary btn-xs" @click="clearSelection">Отменить</button>
    </div>

    <SkeletonTable v-if="loading && !tickets.length" :rows="6" />
    <ErrorMessage v-else-if="error" :message="error" />

    <template v-if="viewMode === 'kanban' && tickets.length">
      <div class="kanban-board">
          <div v-for="col in kanbanColumns" :key="col.key" class="kanban-column" :class="{ 'drag-over': dragOverCol === col.key }" @dragover.prevent="dragOverCol = col.key" @dragleave="dragOverCol = null" @drop="dragOverCol = null; onDrop($event, col.key)">
          <div class="kanban-col-header">
            <span class="badge" :class="'badge-' + col.key">{{ col.label }}</span>
            <span class="kanban-count">{{ groupedByStatus[col.key]?.length || 0 }}</span>
          </div>
          <div class="kanban-cards">
            <div v-for="t in (groupedByStatus[col.key] || [])" :key="t.id"
              class="kanban-card"
              draggable="true"
              @dragstart="onDragStart($event, t)"
              @dragend="onDragEnd">
              <div class="kanban-card-header">
                <span class="cell-id">#{{ t.id }}</span>
                <span v-if="auth.isAdmin" class="badge" :class="'badge-' + t.priority" style="font-size: 9px; padding: 2px 6px;">{{ priorityLabel(t.priority) }}</span>
              </div>
              <router-link :to="`/tasks/${t.id}`" class="kanban-card-title">{{ t.title }}</router-link>
              <div class="kanban-card-meta">
                <span v-if="categoryName(t.category_id) !== '-'">{{ categoryName(t.category_id) }}</span>
                <span v-if="t.deadline" :style="{ color: isOverdue(t.deadline) ? 'var(--danger)' : 'inherit' }">{{ formatDate(t.deadline) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <div v-if="tickets.length" class="card" style="padding: 0; overflow: hidden;">
        <div class="table-wrap">
          <table class="desktop-table">
            <thead>
              <tr>
                <th v-if="auth.isAdmin" style="width: 36px;"><input type="checkbox" :checked="allSelected" @change="toggleSelectAll" /></th>
                <th class="sortable" @click="handleSort('id')">
                  ID
                  <span v-if="sortField === 'id'" class="sort-icon">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th class="sortable" @click="handleSort('title')">
                  Название
                  <span v-if="sortField === 'title'" class="sort-icon">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th v-if="auth.isAdmin" class="sortable" @click="handleSort('status')">
                  Статус
                  <span v-if="sortField === 'status'" class="sort-icon">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th v-if="auth.isAdmin" class="sortable" @click="handleSort('priority')">
                  Приоритет
                  <span v-if="sortField === 'priority'" class="sort-icon">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th>Категория</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in tickets" :key="t.id">
                <td v-if="auth.isAdmin"><input type="checkbox" :checked="selectedIds.has(t.id)" @change="toggleSelect(t.id)" /></td>
                <td class="cell-id">#{{ t.id }}</td>
                <td><router-link :to="`/tasks/${t.id}`" class="ticket-title-link">{{ t.title }}</router-link></td>
                <td v-if="auth.isAdmin">
                  <select class="badge-select" :class="'badge-' + t.status" :value="t.status" @change="handleInlineEdit(t.id, 'status', $event.target.value)">
                    <option value="new">Новая</option>
                    <option value="on_moderation">На модерации</option>
                    <option value="in_progress">В работе</option>
                    <option value="done">Завершено</option>
                    <option value="cancelled">Отменено</option>
                    <option value="closed">Закрыто</option>
                  </select>
                </td>
                <td v-if="auth.isAdmin">
                  <select class="badge-select" :class="'badge-' + t.priority" :value="t.priority" @change="handleInlineEdit(t.id, 'priority', $event.target.value)">
                    <option value="low">Низкий</option>
                    <option value="medium">Средний</option>
                    <option value="high">Высокий</option>
                  </select>
                </td>
                <td><span class="cat-prefix" :style="categoryStyle(t.category_id)">{{ categoryName(t.category_id) }}</span></td>
                <td>
                  <div class="cell-actions">
                    <router-link :to="`/tasks/${t.id}`" class="btn btn-primary btn-xs">Открыть</router-link>
                    <router-link v-if="auth.isAdmin || Number(auth.userId) === t.author_id" :to="`/tasks/${t.id}/edit`" class="btn btn-secondary btn-xs">Редактировать</router-link>
                    <button v-if="auth.isAdmin || Number(auth.userId) === t.author_id" class="btn btn-danger btn-xs" @click="handleDelete(t.id)">Удалить</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="tickets.length" class="mobile-list">
        <div v-for="t in tickets" :key="'m' + t.id" class="mobile-ticket-card">
          <div class="mtc-header">
            <div style="display: flex; align-items: center; gap: 8px;">
              <input type="checkbox" :checked="selectedIds.has(t.id)" @change="toggleSelect(t.id)" />
              <span class="cell-id">#{{ t.id }}</span>
            </div>
            <div class="mtc-badges">
              <span v-if="auth.isAdmin" class="badge" :class="'badge-' + t.status">{{ statusLabel(t.status) }}</span>
              <span v-if="auth.isAdmin" class="badge" :class="'badge-' + t.priority">{{ priorityLabel(t.priority) }}</span>
            </div>
          </div>
          <router-link :to="`/tasks/${t.id}`" class="mtc-title">{{ t.title }}</router-link>
          <div class="mtc-meta">
            <span>{{ categoryName(t.category_id) }}</span>
          </div>
          <div class="mtc-actions">
            <router-link :to="`/tasks/${t.id}`" class="btn btn-primary btn-xs">Открыть</router-link>
            <router-link v-if="auth.isAdmin || Number(auth.userId) === t.author_id" :to="`/tasks/${t.id}/edit`" class="btn btn-secondary btn-xs">Редактировать</router-link>
            <button v-if="auth.isAdmin || Number(auth.userId) === t.author_id" class="btn btn-danger btn-xs" @click="handleDelete(t.id)">Удалить</button>
          </div>
        </div>
      </div>

      <div v-if="!tickets.length && !loading" class="card empty-state">
        <h3>{{ activeTab === 'mine' ? 'У вас пока нет заявок' : activeTab === 'moderation' ? 'Заявок на модерации нет' : 'Заявок нет' }}</h3>
        <p>{{ activeTab === 'mine' ? 'Создайте первую заявку' : 'Попробуйте изменить параметры фильтра' }}</p>
      </div>
    </template>

    <ConfirmDialog :visible="showConfirm" title="Подтверждение" :message="confirmMsg" :danger="confirmDanger" confirmText="Да" @confirm="onConfirmYes" @cancel="showConfirm = false" />
    <div class="pagination" v-if="totalPages > 1">
      <button :disabled="page <= 1" @click="goTo(1)" title="Первая">&laquo;</button>
      <button :disabled="page <= 1" @click="goTo(page - 1)">Назад</button>
      <button v-for="p in visiblePages" :key="p" :class="{ active: p === page }" @click="goTo(p)">{{ p }}</button>
      <button :disabled="page >= totalPages" @click="goTo(page + 1)">Вперёд</button>
      <button :disabled="page >= totalPages" @click="goTo(totalPages)" title="Последняя">&raquo;</button>
    </div>
  </div>
</template>

<script setup>
import { Download, XSquare, LayoutGrid, Table, RefreshCw, ChevronRight } from 'lucide-vue-next'
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ticketsApi, categoriesApi } from '../api/ticketsApi'
import api from '../api/axios'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import SkeletonTable from '../components/SkeletonTable.vue'
import ErrorMessage from '../components/ErrorMessage.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const toast = useToastStore()
const tickets = ref([])
const categories = ref([])
const loading = ref(true)
const error = ref('')
const page = ref(1)
const totalPages = ref(0)
const limit = 10
const activeTab = ref('all')
const sortField = ref('created_at')
const sortOrder = ref('desc')
const viewMode = ref('table')
const selectedIds = ref(new Set())
const draggingTicket = ref(null)
const dragOverCol = ref(null)
const exportingCSV = ref(false)
const exportingXLSX = ref(false)
const showConfirm = ref(false)
const bulkStatus = ref('')
const bulkCategory = ref('')
const bulkAssignee = ref('')
const autoRefresh = ref(false)
const showWorkflow = ref(false)
const quickFilter = ref('')
let autoRefreshTimer = null
const confirmMsg = ref('')
const confirmDanger = ref(false)
let confirmAction = null

function askConfirm(msg, danger = false) {
  return new Promise((resolve) => {
    confirmMsg.value = msg
    confirmDanger.value = danger
    confirmAction = resolve
    showConfirm.value = true
  })
}
function onConfirmYes() {
  showConfirm.value = false
  if (confirmAction) confirmAction(true)
}
function onConfirmNo() {
  showConfirm.value = false
  if (confirmAction) confirmAction(false)
}

const filters = ref({ search: '', status: '', priority: '', date_from: '', date_to: '' })
let searchTimeout = null

function syncToUrl() {
  const q = {}
  if (filters.value.search) q.search = filters.value.search
  if (filters.value.status) q.status = filters.value.status
  if (filters.value.priority) q.priority = filters.value.priority
  if (filters.value.date_from) q.date_from = filters.value.date_from
  if (filters.value.date_to) q.date_to = filters.value.date_to
  if (activeTab.value !== 'all') q.tab = activeTab.value
  if (page.value > 1) q.page = String(page.value)
  if (sortField.value !== 'created_at') q.sort = sortField.value
  if (sortOrder.value !== 'desc') q.order = sortOrder.value
  if (viewMode.value !== 'table') q.view = viewMode.value
  if (quickFilter.value) q.quick = quickFilter.value
  router.replace({ query: q })
}

watch([filters, activeTab, page, sortField, sortOrder, viewMode, quickFilter], () => {
  syncToUrl()
}, { deep: true })

function readFromUrl() {
  const q = route.query
  if (q.search) filters.value.search = q.search
  if (q.status) filters.value.status = q.status
  if (q.priority) filters.value.priority = q.priority
  if (q.date_from) filters.value.date_from = q.date_from
  if (q.date_to) filters.value.date_to = q.date_to
  if (q.tab) activeTab.value = q.tab
  if (q.page) page.value = Number(q.page)
  if (q.sort) sortField.value = q.sort
  if (q.order) sortOrder.value = q.order
  if (q.view) viewMode.value = q.view
  if (q.quick) quickFilter.value = q.quick
}

const kanbanColumns = computed(() => {
  const cols = [
    { key: 'new', label: 'Новые' },
    { key: 'in_progress', label: 'В работе' },
    { key: 'done', label: 'Завершено' },
    { key: 'cancelled', label: 'Отменено' },
    { key: 'closed', label: 'Закрыто' },
  ]
  if (auth.isAdmin) cols.splice(1, 0, { key: 'on_moderation', label: 'На модерации' })
  return cols
})

const groupedByStatus = computed(() => {
  const groups = {}
  for (const col of kanbanColumns) groups[col.key] = []
  for (const t of tickets.value) {
    if (groups[t.status]) groups[t.status].push(t)
  }
  return groups
})

const allSelected = computed(() => tickets.value.length > 0 && tickets.value.every(t => selectedIds.value.has(t.id)))

const visiblePages = computed(() => {
  const total = totalPages.value
  const curr = page.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  if (curr <= 3) return [1, 2, 3, 4, '...', total]
  if (curr >= total - 2) return [1, '...', total - 3, total - 2, total - 1, total]
  return [1, '...', curr - 1, curr, curr + 1, '...', total]
})

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    const m = filters.value.search.match(/^#(\d+)$/)
    if (m) {
      router.push(`/tasks/${m[1]}`)
      return
    }
    page.value = 1; loadTickets()
  }, 300)
}

function debouncedFilter() {
  activeTab.value = 'all'
  page.value = 1; loadTickets()
}

function setTab(tab) {
  activeTab.value = tab
  filters.value.status = ''
  quickFilter.value = ''
  page.value = 1
  loadTickets()
}

function setQuickFilter(f) {
  if (quickFilter.value === f) { quickFilter.value = ''; activeTab.value = 'all'; page.value = 1; loadTickets(); return }
  quickFilter.value = f
  activeTab.value = 'all'
  filters.value.status = ''
  page.value = 1
  loadTickets()
}

function handleSort(field) {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
  page.value = 1
  loadTickets()
}

function toggleView() {
  viewMode.value = viewMode.value === 'table' ? 'kanban' : 'table'
}

function toggleSelect(id) {
  const s = new Set(selectedIds.value)
  if (s.has(id)) s.delete(id); else s.add(id)
  selectedIds.value = s
}

function clearSelection() { selectedIds.value = new Set() }

function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value = new Set()
  } else {
    selectedIds.value = new Set(tickets.value.map(t => t.id))
  }
}

function startAutoRefresh() {
  stopAutoRefresh()
  autoRefreshTimer = setInterval(() => { loadTickets(true) }, 15000)
}
function stopAutoRefresh() { if (autoRefreshTimer) { clearInterval(autoRefreshTimer); autoRefreshTimer = null } }
watch(autoRefresh, (v) => { if (v) startAutoRefresh(); else stopAutoRefresh() })
onMounted(async () => {
  readFromUrl()
  try { categories.value = await categoriesApi.getList() } catch {}
  await loadTickets()
})
onBeforeUnmount(() => stopAutoRefresh())

async function loadTickets(silent = false) {
  if (!silent) loading.value = true
  error.value = ''
  try {
    const params = {
      skip: (page.value - 1) * limit,
      limit,
      sort: sortField.value,
      order: sortOrder.value,
    }
    if (filters.value.search) {
      const m = filters.value.search.match(/^#(\d+)$/)
      if (!m) params.search = filters.value.search
    }
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.priority) params.priority = filters.value.priority
    if (filters.value.date_from) params.date_from = filters.value.date_from + 'T00:00:00'
    if (filters.value.date_to) params.date_to = filters.value.date_to + 'T23:59:59'
    if (activeTab.value === 'mine' && auth.userId) params.author_id = Number(auth.userId)
    if (activeTab.value === 'moderation') params.status = 'on_moderation'
    if (quickFilter.value === 'today') {
      const today = new Date(); params.date_from = today.toISOString().slice(0, 10) + 'T00:00:00'; params.date_to = today.toISOString().slice(0, 10) + 'T23:59:59'
    }
    if (quickFilter.value === 'overdue') {
      params.date_to = new Date().toISOString().slice(0, 10) + 'T23:59:59'
    }
    const data = await ticketsApi.getList(params)
    tickets.value = data.items
    totalPages.value = data.pages
  } catch {
    error.value = 'Не удалось загрузить заявки'
  } finally {
    loading.value = false
  }
}

function goTo(p) { if (p < 1 || p > totalPages.value || p === page.value) return; page.value = p; loadTickets() }

function statusLabel(s) {
  return { new: 'Новая', on_moderation: 'На модерации', in_progress: 'В работе', done: 'Завершено', cancelled: 'Отменено', closed: 'Закрыто' }[s] || s
}

function priorityLabel(p) {
  return { low: 'Низкий', medium: 'Средний', high: 'Высокий' }[p] || p
}

function categoryName(id) {
  if (!id) return '-'
  const c = categories.value.find(c => c.id === id)
  return c ? c.name : '-'
}
const CAT_COLORS = ['#0d9488','#059669','#d97706','#dc2626','#7c3aed','#0891b2','#db2777','#2563eb', '#65a30d', '#f97316']
function categoryStyle(id) {
  if (!id) return {}
  const idx = categories.value.findIndex(c => c.id === id)
  const color = CAT_COLORS[Math.abs(idx) % CAT_COLORS.length]
  return { background: color + '18', color, borderColor: color + '30', fontWeight: 600 }
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

function isOverdue(d) {
  return new Date(d) < new Date()
}

function exportParams() {
  const p = {}
  if (filters.value.status) p.status = filters.value.status
  if (filters.value.priority) p.priority = filters.value.priority
  if (filters.value.search) p.search = filters.value.search
  if (activeTab.value === 'mine' && auth.userId) p.author_id = Number(auth.userId)
  return p
}

async function handleExportXLSX() {
  exportingXLSX.value = true
  try {
    const resp = await api.get('/tickets/export/xlsx', { params: exportParams(), responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([resp.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }))
    const link = document.createElement('a')
    link.href = url
    link.download = `tickets_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(link); link.click(); document.body.removeChild(link)
    URL.revokeObjectURL(url)
    toast.success('XLSX скачан')
  } catch { toast.error('Ошибка экспорта') }
  finally { exportingXLSX.value = false }
}

async function handleExportCSV() {
  exportingCSV.value = true
  try {
    const resp = await api.get('/tickets/export/csv', { params: exportParams(), responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([resp.data], { type: 'text/csv' }))
    const link = document.createElement('a')
    link.href = url
    link.download = `tickets_${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    toast.success('CSV скачан')
  } catch {
    toast.error('Ошибка экспорта')
  }
  finally { exportingCSV.value = false }
}

async function handleDelete(id) {
  if (!(await askConfirm('Удалить эту заявку?', true))) return
  try {
    await ticketsApi.delete(id)
    toast.success('Заявка удалена')
    selectedIds.value.delete(id)
    selectedIds.value = new Set(selectedIds.value)
    await loadTickets()
  } catch { error.value = 'Ошибка удаления' }
}

async function handleInlineEdit(id, field, value) {
  try {
    await ticketsApi.update(id, { [field]: value })
    toast.success(`#${id} ${field === 'status' ? 'статус' : 'приоритет'} обновлён`)
    await loadTickets()
  } catch { toast.error('Ошибка обновления') }
}

async function handleBulkStatus() {
  const ids = [...selectedIds.value]
  if (!ids.length || !bulkStatus.value) return
  try {
    const resp = await api.post('/tickets/batch-status', { ids, status: bulkStatus.value })
    toast.success(`Статус изменён у ${resp.data.updated} заявок`)
    bulkStatus.value = ''
    selectedIds.value = new Set()
    await loadTickets()
  } catch { toast.error('Ошибка массового изменения статуса') }
}

async function handleBulkEdit() {
  const ids = [...selectedIds.value]
  if (!ids.length) return
  const updateData = {}
  if (bulkStatus.value) updateData.status = bulkStatus.value
  if (bulkCategory.value) updateData.category_id = Number(bulkCategory.value)
  if (bulkAssignee.value) updateData.assignee_id = Number(bulkAssignee.value)
  if (!Object.keys(updateData).length) return
  let updated = 0
  for (const id of ids) {
    try { await ticketsApi.update(id, updateData); updated++ } catch {}
  }
  toast.success(`Обновлено ${updated} заявок`)
  bulkStatus.value = ''; bulkCategory.value = ''; bulkAssignee.value = ''
  selectedIds.value = new Set()
  await loadTickets()
}

async function handleBulkDelete() {
  const ids = [...selectedIds.value]
  if (!ids.length || !(await askConfirm(`Удалить ${ids.length} заявок?`, true))) return
  try {
    await ticketsApi.batchDelete(ids)
    toast.success(`Удалено ${ids.length} заявок`)
    selectedIds.value = new Set()
    await loadTickets()
  } catch { toast.error('Ошибка массового удаления') }
}

function onDragStart(e, t) {
  draggingTicket.value = t
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('text/plain', String(t.id))
}
function onDragEnd() { draggingTicket.value = null }
async function onDrop(e, newStatus) {
  const t = draggingTicket.value
  if (!t || t.status === newStatus) return
  try {
    await ticketsApi.update(t.id, { status: newStatus })
    toast.success(`Статус #${t.id} изменён на «${statusLabel(newStatus)}»`)
    await loadTickets()
  } catch { toast.error('Ошибка изменения статуса') }
}
</script>

<style scoped>
.table-wrap { overflow-x: auto; }
.desktop-table { width: 100%; border-collapse: collapse; }
.desktop-table th.sortable { cursor: pointer; user-select: none; }
.desktop-table th.sortable:hover { color: var(--primary); }
.sort-icon { font-size: 10px; margin-left: 4px; }
.cell-id { color: var(--text-dim); font-family: monospace; font-size: 12px; }
.cell-category { color: var(--text-muted); }
.cat-prefix { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; border: 1px solid; white-space: nowrap; }
.cell-actions { display: flex; gap: 4px; }
.cell-actions .btn-xs { padding: 3px 8px; font-size: 11px; }
.ticket-title-link { font-weight: 600; }
.header-actions { display: flex; gap: 6px; align-items: center; }
.header-actions .btn-xs { padding: 4px 10px; font-size: 11px; }

.badge-select {
  appearance: none; border: none; border-radius: 6px;
  padding: 4px 18px 4px 10px; font-size: 11px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.2px;
  font-family: inherit; cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='8' height='8' viewBox='0 0 8 8'%3E%3Cpath fill='%23666' d='M0 0l4 4 4-4z'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 4px center; background-size: 8px;
  transition: transform 0.2s;
}
.badge-select:hover { transform: scale(1.05); }
.badge-select:focus { outline: 2px solid var(--primary); outline-offset: 2px; }
.badge-select option { font-weight: 400; text-transform: none; letter-spacing: 0; }

.bulk-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: var(--bg-card);
  border: 1px solid var(--primary);
  border-radius: 8px;
  margin-bottom: 12px;
}

.kanban-board {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 12px;
}
.kanban-column {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  min-height: 200px;
  min-width: 180px;
}
.kanban-col-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.kanban-count {
  font-size: 12px;
  color: var(--text-dim);
  font-weight: 700;
}
.kanban-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.kanban-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  cursor: grab;
  transition: box-shadow 0.2s, transform 0.2s;
}
.kanban-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transform: translateY(-1px);
}
.kanban-card:active { cursor: grabbing; }
.kanban-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.kanban-card-title {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--text);
  text-decoration: none !important;
  line-height: 1.4;
}
.kanban-card-title:hover { color: var(--primary); }
.kanban-card-meta {
  font-size: 11px;
  color: var(--text-dim);
  display: flex;
  justify-content: space-between;
}

.mobile-list { display: none; gap: 10px; flex-direction: column; }
.mobile-ticket-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.3s;
}
.mobile-ticket-card:hover {
  border-color: var(--primary);
  box-shadow: 0 2px 12px rgba(var(--primary-rgb), 0.08);
}
.mtc-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;
}
.mtc-badges { display: flex; gap: 4px; }
.mtc-title {
  display: block; font-weight: 600; font-size: 15px; margin-bottom: 6px;
  color: var(--text); text-decoration: none !important;
}
.mtc-title:hover { color: var(--primary); }
.mtc-meta { font-size: 13px; color: var(--text-muted); margin-bottom: 10px; }
.mtc-actions { display: flex; gap: 6px; }

@media (max-width: 720px) {
  .desktop-table { display: none; }
  .mobile-list { display: flex; }
  .filters { flex-direction: column; }
  .filters .form-control { min-width: 100%; }
  .kanban-board { grid-template-columns: repeat(5, 220px); }
}


.workflow-steps { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.wf-step { display: flex; align-items: center; }

@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  display: inline-block;
  width: 14px; height: 14px;
  border: 2px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
</style>
