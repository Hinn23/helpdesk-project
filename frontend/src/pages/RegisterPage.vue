<template>
  <div class="auth-page">
    <div class="card" style="width: 420px; padding: 36px;">
      <div style="text-align: center; margin-bottom: 28px;">
        <h1 style="font-size: 26px; font-weight: 800; margin-bottom: 4px; color: var(--text);">Регистрация</h1>
        <p style="color: var(--text-muted); font-size: 14px;">Создайте аккаунт</p>
      </div>
      <ErrorMessage :message="error" />
      <form v-if="!codeSent" @submit.prevent="handleRegister" novalidate>
        <div class="form-group">
          <label>Имя</label>
          <input v-model="name" class="form-control" placeholder="Минимум 3 символа" required />
        </div>
        <div class="form-group">
          <label>Эл. почта</label>
          <input v-model="email" type="text" class="form-control" placeholder="@gmail.com, @mail.ru, @yandex.ru" required />
        </div>
        <div class="form-group">
          <label>Пароль</label>
          <input v-model="password" type="password" class="form-control" placeholder="Минимум 6 символов" required />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="submitting" style="width:100%; justify-content: center;">
          {{ submitting ? 'Отправка...' : 'Получить код' }}
        </button>
      </form>
      <form v-else @submit.prevent="handleVerify" novalidate>
        <div class="success-box" style="margin-bottom: 16px;">Код отправлен на {{ email }}<br><span style="font-size: 11px; opacity: 0.7;">Если не пришло — проверьте MailHog http://localhost:8025</span></div>
        <div class="form-group">
          <label>Код из письма</label>
          <input v-model="code" type="text" class="form-control" placeholder="6 цифр" maxlength="6" required />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="submitting" style="width:100%; justify-content: center;">
          {{ submitting ? 'Подтверждение...' : 'Подтвердить' }}
        </button>
      </form>
      <p style="text-align: center; margin-top: 20px; font-size: 14px; color: var(--text-muted);">
        Уже есть аккаунт? <router-link to="/login">Войти</router-link>
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
import api from '../api/axios'

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()
const name = ref('')
const email = ref('')
const password = ref('')
const code = ref('')
const codeSent = ref(false)
const error = ref('')
const submitting = ref(false)

function parseError(e) {
  const d = e.response?.data?.detail
  if (Array.isArray(d)) return d.map(x => x.msg.replace('Value error, ', '')).join('; ')
  return d || 'Произошла ошибка'
}

async function handleRegister() {
  error.value = ''
  if (name.value.trim().length < 3) { error.value = 'Имя должно содержать минимум 3 символа'; return }
  if (!email.value.includes('@')) { error.value = 'Введите корректный email (с @)'; return }
  const allowed = ['gmail.com', 'mail.ru', 'yandex.ru']
  const domain = email.value.split('@')[1]?.toLowerCase()
  if (!domain || !allowed.includes(domain)) { error.value = 'Разрешены только домены: gmail.com, mail.ru, yandex.ru'; return }
  if (password.value.length < 6) { error.value = 'Пароль должен содержать минимум 6 символов'; return }
  submitting.value = true
  try {
    const resp = await api.post('/auth/register', { name: name.value, email: email.value, password: password.value })
    codeSent.value = true
    if (resp.data.code_for_test) {
      code.value = resp.data.code_for_test
      toast.success(`Код: ${resp.data.code_for_test}`)
    } else {
      toast.success('Код отправлен на почту!')
    }
  } catch (e) { error.value = parseError(e) }
  finally { submitting.value = false }
}

async function handleVerify() {
  if (!code.value) { error.value = 'Введите код'; return }
  submitting.value = true
  try {
    const resp = await api.post('/auth/verify-email', { email: email.value, code: code.value })
    auth.setAuth(resp.data)
    toast.success('Аккаунт создан. Добро пожаловать!')
    router.push('/tasks')
  } catch (e) { error.value = parseError(e) }
  finally { submitting.value = false }
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

.success-box {
  background: rgba(5, 150, 105, 0.1); color: #059669;
  padding: 12px 16px; border-radius: 8px; font-size: 13px; text-align: center;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
