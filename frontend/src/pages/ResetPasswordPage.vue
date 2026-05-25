<template>
  <div class="auth-page">
    <div class="card" style="width: 420px; padding: 36px;">
      <div style="text-align: center; margin-bottom: 28px;">
        <h1 style="font-size: 26px; font-weight: 800; margin-bottom: 4px;">Новый пароль</h1>
        <p style="color: var(--text-muted); font-size: 14px;">Введите новый пароль</p>
      </div>
      <ErrorMessage :message="error" />
      <div v-if="success" class="success-box">{{ success }}</div>
      <form @submit.prevent="handleReset">
        <div class="form-group">
          <label>Токен из письма</label>
          <input v-model="token" type="text" class="form-control" placeholder="Вставьте токен" required />
        </div>
        <div class="form-group">
          <label>Новый пароль</label>
          <input v-model="password" type="password" class="form-control" placeholder="Минимум 6 символов" required />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="submitting" style="width:100%; justify-content: center;">
          {{ submitting ? 'Сохранение...' : 'Сменить пароль' }}
        </button>
      </form>
      <p style="text-align: center; margin-top: 20px; font-size: 14px; color: var(--text-muted);">
        <router-link to="/login">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'
import ErrorMessage from '../components/ErrorMessage.vue'
import { useToastStore } from '../stores/toast'

const router = useRouter()
const toast = useToastStore()
const token = ref('')
const password = ref('')
const error = ref('')
const success = ref('')
const submitting = ref(false)

async function handleReset() {
  error.value = ''
  if (password.value.length < 6) {
    error.value = 'Пароль должен содержать минимум 6 символов'
    return
  }
  submitting.value = true
  try {
    await api.post('/auth/reset-password', { token: token.value, new_password: password.value })
    toast.success('Пароль изменён! Теперь можно войти.')
    router.push('/login')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка сброса пароля'
  } finally { submitting.value = false }
}
</script>

<style scoped>
.auth-page { display: flex; justify-content: center; padding-top: 60px; }
.card { animation: slideUp 0.5s ease-out; }
.success-box {
  background: rgba(5, 150, 105, 0.1); color: #059669;
  padding: 12px 16px; border-radius: 8px; font-size: 13px; margin-bottom: 16px;
}
@keyframes slideUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }
</style>
