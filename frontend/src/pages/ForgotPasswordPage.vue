<template>
  <div class="auth-page">
    <div class="card" style="width: 420px; padding: 36px;">
      <div style="text-align: center; margin-bottom: 28px;">
        <h1 style="font-size: 26px; font-weight: 800; margin-bottom: 4px;">Сброс пароля</h1>
        <p style="color: var(--text-muted); font-size: 14px;">Введите email, привязанный к аккаунту</p>
      </div>
      <ErrorMessage :message="error" />
      <div v-if="success" class="success-box">{{ success }}</div>
      <form @submit.prevent="handleForgot">
        <div class="form-group">
          <label>Эл. почта</label>
          <input v-model="email" type="text" class="form-control" placeholder="@gmail.com" required />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="submitting" style="width:100%; justify-content: center;">
          {{ submitting ? 'Отправка...' : 'Получить токен' }}
        </button>
      </form>
      <p style="text-align: center; margin-top: 20px; font-size: 14px; color: var(--text-muted);">
        Вспомнили? <router-link to="/login">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/axios'
import ErrorMessage from '../components/ErrorMessage.vue'

const email = ref('')
const error = ref('')
const success = ref('')
const submitting = ref(false)

async function handleForgot() {
  error.value = ''
  success.value = ''
  if (!email.value.includes('@')) {
    error.value = 'Введите корректный email'
    return
  }
  submitting.value = true
  try {
    const resp = await api.post('/auth/forgot-password', { email: email.value })
    success.value = resp.data.message + (resp.data.reset_token ? ` Токен: ${resp.data.reset_token}` : '')
  } catch {
    error.value = 'Ошибка при запросе сброса пароля'
  } finally { submitting.value = false }
}
</script>

<style scoped>
.auth-page { display: flex; justify-content: center; padding-top: 60px; }
.card { animation: slideUp 0.5s ease-out; }
.success-box {
  background: rgba(5, 150, 105, 0.1); color: #059669;
  padding: 12px 16px; border-radius: 8px; font-size: 13px; margin-bottom: 16px;
  word-break: break-all;
}
@keyframes slideUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }
</style>
