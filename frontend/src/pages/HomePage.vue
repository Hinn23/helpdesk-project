<template>
  <div class="home">
    <div class="hero">
      <div class="hero-badge">Fullstack Project</div>
      <h1 class="hero-title">Helpdesk Lite</h1>
      <p class="hero-tagline">Где баги становятся фичами</p>
      <p class="hero-desc">Система управления тикетами на FastAPI + Vue 3</p>
      <div class="hero-actions">
        <router-link to="/tasks" class="btn btn-primary btn-lg">Смотреть заявки</router-link>
        <router-link v-if="auth.isAuthenticated" to="/tasks/create" class="btn btn-secondary btn-lg">Создать заявку</router-link>
      </div>
    </div>
    <div class="features">
      <div class="feature-card" style="animation-delay: 0.1s;">
        <div class="feature-icon"><ClipboardCheck :size="28" color="var(--primary)" /></div>
        <h3>Заявки</h3>
        <p>Создавайте и управляйте задачами со статусами, приоритетами и дедлайнами</p>
      </div>
      <div class="feature-card" style="animation-delay: 0.2s;">
        <div class="feature-icon"><MessageCircle :size="28" color="var(--primary)" /></div>
        <h3>Комментарии</h3>
        <p>Обсуждайте задачи внутри тикета. Вся история на одном экране</p>
      </div>
      <div class="feature-card" style="animation-delay: 0.3s;">
        <div class="feature-icon"><Folder :size="28" color="var(--primary)" /></div>
        <h3>Категории</h3>
        <p>Организуйте заявки по категориям для быстрой навигации</p>
      </div>
      <div class="feature-card" style="animation-delay: 0.4s;">
        <div class="feature-icon"><Lock :size="28" color="var(--primary)" /></div>
        <h3>JWT Auth</h3>
        <p>Роли admin, user, guest. Безопасность и разграничение доступа</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ClipboardCheck, MessageCircle, Folder, Lock } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
</script>

<style scoped>
.home {
  max-width: 720px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 80px 20px 50px;
  animation: fadeIn 0.6s ease-out;
}

.hero-badge {
  display: inline-block;
  padding: 4px 14px;
  background: rgba(var(--primary-rgb), 0.07);
  border: 1px solid rgba(var(--primary-rgb), 0.15);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 20px;
  letter-spacing: 0.3px;
}

.hero-title {
  font-size: 48px;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.hero-tagline {
  font-size: 18px;
  color: var(--primary);
  font-weight: 500;
  margin-bottom: 6px;
}

.hero-desc {
  color: var(--text-muted);
  font-size: 16px;
  margin-bottom: 32px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-lg {
  padding: 14px 32px;
  font-size: 16px;
}

.features {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding-bottom: 40px;
}

.feature-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  animation: cardFloat 5s ease-in-out infinite;
  transition: box-shadow 0.3s, transform 0.3s, border-color 0.3s, background 0.3s;
}

.feature-card:nth-child(2) { animation-delay: 0.6s; }
.feature-card:nth-child(3) { animation-delay: 1.2s; }
.feature-card:nth-child(4) { animation-delay: 1.8s; }

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  border-color: var(--border);
}

.feature-icon {
  margin-bottom: 16px;
}

.feature-card h3 {
  margin-bottom: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}

.feature-card p {
  color: var(--text-muted);
  font-size: 14px;
  line-height: 1.6;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes cardFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
</style>
