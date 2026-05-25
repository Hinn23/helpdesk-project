<template>
  <div class="card card-form" style="max-width: 700px;">
    <div class="card-header">
      <h2>{{ isEdit ? 'Редактировать заявку' : 'Новая заявка' }}</h2>
    </div>
    <ErrorMessage :message="error" />
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>Название</label>
        <input v-model="form.title" class="form-control" placeholder="Что случилось?" required minlength="3" />
      </div>
      <div class="form-group">
        <label>Описание</label>
        <textarea v-model="form.description" class="form-control" rows="4" placeholder="Опишите проблему подробнее..." @input="autoResize"></textarea>
      </div>
      <div v-if="auth.isAdmin" class="row">
        <div class="form-group col">
          <label>Статус</label>
          <select v-model="form.status" class="form-control">
            <option value="new">Новая</option>
            <option value="on_moderation">На модерации</option>
            <option value="in_progress">В работе</option>
            <option value="done">Завершено</option>
            <option value="cancelled">Отменено</option>
            <option value="closed">Закрыто</option>
          </select>
        </div>
        <div class="form-group col">
          <label>Приоритет</label>
          <select v-model="form.priority" class="form-control">
            <option value="low">Низкий</option>
            <option value="medium">Средний</option>
            <option value="high">Высокий</option>
          </select>
        </div>
      </div>
      <div class="row">
        <div class="form-group col">
          <label>Категория <span style="color: var(--danger);">*</span></label>
          <select v-model="form.category_id" class="form-control" required>
            <option value="" disabled>-- Выберите категорию --</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div v-if="auth.isAdmin" class="form-group col">
          <label>Исполнитель</label>
          <select v-model="form.assignee_id" class="form-control">
            <option :value="null">-- Не назначен --</option>
            <option v-for="u in users" :key="u.id" :value="u.id">{{ u.name }}</option>
          </select>
        </div>
      </div>
      <div class="row">
        <div class="form-group col">
          <label>Дедлайн</label>
          <input type="datetime-local" v-model="deadlineLocal" class="form-control" />
        </div>
        <div class="form-group col"></div>
      </div>
      <div v-if="!isEdit" class="form-group">
        <label>Файлы и фото</label>
        <div class="drop-zone" @drop.prevent="onDrop" @dragover.prevent="dragOver = true" @dragleave.prevent="dragOver = false" :class="{ 'drag-over': dragOver }">
          <input type="file" ref="fileInput" multiple accept="image/*,.pdf,.doc,.docx,.xlsx,.zip" style="display:none" @change="onFilesSelect" />
          <button type="button" class="btn btn-secondary btn-sm" @click="$refs.fileInput.click()">+ Выбрать файлы</button>
          <span style="font-size: 12px; color: var(--text-dim); margin-left: 10px;">или перетащи сюда</span>
        </div>
        <div v-if="selectedFiles.length" class="file-previews">
          <div v-for="(f, i) in selectedFiles" :key="i" class="file-preview-item">
            <img v-if="f.isImage" :src="f.url" class="preview-thumb" />
            <div v-else class="preview-icon">
              <File :size="20" />
            </div>
            <span class="preview-name">{{ f.file.name }}</span>
            <button type="button" class="btn btn-danger btn-xs" @click="removeFile(i)">&times;</button>
          </div>
        </div>
      </div>
      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          {{ submitting ? 'Сохранение...' : (isEdit ? 'Сохранить' : 'Создать заявку') }}
        </button>
        <button type="button" class="btn btn-secondary" @click="$router.push('/tasks')">Отмена</button>
        <span style="margin-left: auto; font-size: 11px; color: var(--text-dim);">Ctrl+Enter — отправить</span>
      </div>
    </form>
  </div>
</template>

<script setup>
import { File } from 'lucide-vue-next'
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { ticketsApi, categoriesApi, usersApi } from '../api/ticketsApi'
import { useAuthStore } from '../stores/auth'
import ErrorMessage from './ErrorMessage.vue'
import { useToastStore } from '../stores/toast'
import api from '../api/axios'

const props = defineProps({ ticket: { type: Object, default: null } })
const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()
const isEdit = !!props.ticket

const form = ref({
  title: '',
  description: '',
  status: 'new',
  priority: 'medium',
  category_id: '',
  deadline: null,
})
const deadlineLocal = ref('')
const categories = ref([])
const users = ref([])
const error = ref('')
const submitting = ref(false)
const selectedFiles = ref([])
const fileInput = ref(null)
const dragOver = ref(false)

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

function parseError(e) {
  const d = e.response?.data?.detail
  if (Array.isArray(d)) return d.map(x => x.msg.replace('Value error, ', '')).join('; ')
  return d || 'Не удалось сохранить заявку'
}

function onDrop(e) {
  dragOver.value = false
  const files = [...(e.dataTransfer.files || [])]
  for (const file of files) addFile(file)
}

function onFilesSelect(e) {
  const files = [...(e.target.files || [])]
  for (const file of files) addFile(file)
  if (fileInput.value) fileInput.value.value = ''
}

function addFile(file) {
  if (file.size > 10 * 1024 * 1024) { toast.error(`Файл "${file.name}" больше 10 МБ`); return }
  const isImage = file.type.startsWith('image/')
  selectedFiles.value.push({ file, isImage, url: isImage ? URL.createObjectURL(file) : '' })
}

function removeFile(i) {
  const f = selectedFiles.value[i]
  if (f.url) URL.revokeObjectURL(f.url)
  selectedFiles.value.splice(i, 1)
}

onMounted(async () => {
  try { categories.value = await categoriesApi.getList() } catch {}
  try { users.value = await usersApi.getList() } catch {}
    if (props.ticket) {
      form.value = { ...props.ticket, category_id: props.ticket.category_id ?? '' }
      if (props.ticket.deadline) {
        const d = new Date(props.ticket.deadline)
        if (!isNaN(d.getTime())) {
          const pad = n => String(n).padStart(2, '0')
          deadlineLocal.value = `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
        }
      }
    }
})

watch(deadlineLocal, (val) => {
  if (val) {
    form.value.deadline = val + ':00'
  } else {
    form.value.deadline = null
  }
})

const isDirty = ref(false)
watch(() => form.value, () => { if (!submitting.value) isDirty.value = true }, { deep: true })
watch(selectedFiles, () => { isDirty.value = true }, { deep: true })
onBeforeRouteLeave((to, from, next) => {
  if (isDirty.value) {
    if (!confirm('У вас есть несохранённые изменения. Покинуть страницу?')) { next(false); return }
  }
  next()
})

async function handleSubmit() {
  error.value = ''
  if (form.value.title.trim().length < 3) {
    error.value = 'Название должно содержать минимум 3 символа'
    return
  }
  if (!form.value.category_id) {
    error.value = 'Выберите категорию'
    return
  }
  submitting.value = true
  try {
    const payload = { ...form.value, deadline: form.value.deadline || null }
    if (isEdit) {
      await ticketsApi.update(props.ticket.id, payload)
      isDirty.value = false
      toast.success('Заявка обновлена')
      router.push(`/tasks/${props.ticket.id}`)
    } else {
      const ticket = await ticketsApi.create(payload)
      for (const f of selectedFiles.value) {
        const form = new FormData()
        form.append('file', f.file)
        await api.post(`/tickets/${ticket.id}/attachments`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
      }
      isDirty.value = false
      toast.success('Заявка создана' + (selectedFiles.value.length ? ` + ${selectedFiles.value.length} файл(ов)` : ''))
      router.push(`/tasks/${ticket.id}`)
    }
  } catch (e) {
    error.value = parseError(e)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.card-form {
  animation: slideInForm 0.5s ease-out;
}

@keyframes slideInForm {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.row { display: flex; gap: 16px; }
.col { flex: 1; }
.form-actions { display: flex; gap: 10px; margin-top: 24px; }
textarea { resize: vertical; }
.file-previews { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.file-preview-item {
  display: flex; align-items: center; gap: 8px;
  background: var(--bg-input); border: 1px solid var(--border);
  border-radius: 8px; padding: 6px 10px; font-size: 13px;
}
.preview-thumb { width: 40px; height: 40px; border-radius: 4px; object-fit: cover; }
.preview-icon { width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; color: var(--text-muted); }
.preview-name { max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-secondary); }
.drop-zone { display: flex; align-items: center; gap: 8px; padding: 12px 16px; border: 2px dashed var(--border); border-radius: 10px; background: var(--bg-input); transition: all 0.2s; }
.drop-zone.drag-over { border-color: var(--primary); background: rgba(79,70,229,0.04); }
</style>
