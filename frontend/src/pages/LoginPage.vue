<template>
  <div class="auth-page">
    <div class="card" style="width: 420px; padding: 36px;">
      <div style="text-align: center; margin-bottom: 28px;">
        <h1 style="font-size: 26px; font-weight: 800; margin-bottom: 4px; color: var(--text);">Вход</h1>
        <p style="color: var(--text-muted); font-size: 14px;">Добро пожаловать обратно</p>
      </div>
      <ErrorMessage :message="error" />
      <form @submit.prevent="handleLogin" novalidate>
        <div class="form-group">
          <label>Эл. почта</label>
          <input v-model="email" type="text" class="form-control" placeholder="your@email.com" required />
        </div>
        <div class="form-group">
          <label>Пароль</label>
          <input v-model="password" type="password" class="form-control" placeholder="Введите пароль" required />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="submitting" style="width:100%; justify-content: center;">
          {{ submitting ? 'Вход...' : 'Войти' }}
        </button>
      </form>
      <p style="text-align: center; margin-top: 12px; font-size: 14px; color: var(--text-muted);">
        <router-link to="/forgot-password">Забыли пароль?</router-link>
      </p>
      <p style="text-align: center; margin-top: 12px; font-size: 14px; color: var(--text-muted);">
        Нет аккаунта? <router-link to="/register">Регистрация</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import ErrorMessage from '../components/ErrorMessage.vue'
import { useToastStore } from '../stores/toast'

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()
const email = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

function parseError(e) {
  const d = e.response?.data?.detail
  if (Array.isArray(d)) return d.map(x => x.msg.replace('Value error, ', '')).join('; ')
  return d || 'Произошла ошибка'
}

async function handleLogin() {
  error.value = ''
  if (!email.value.includes('@')) {
    error.value = 'Введите корректный email (с @)'
    return
  }
  submitting.value = true
  try {
    await auth.login(email.value, password.value)
    toast.success('Вы вошли в систему')
    router.push('/tasks')
  } catch (e) {
    error.value = parseError(e)
  } finally { submitting.value = false }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  padding-top: 60px;
}

.card {
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
