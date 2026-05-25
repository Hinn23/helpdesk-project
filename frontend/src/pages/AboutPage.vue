<template>
  <div class="about">
    <div class="header-section">
      <h1>О проекте</h1>
    </div>
    <div class="card" style="animation-delay: 0.1s;">
      <div style="text-align: center; margin-bottom: 32px; padding-bottom: 28px; border-bottom: 1px solid var(--border-light);">
        <h2 style="font-size: 24px; font-weight: 800; margin-bottom: 4px; color: var(--text);">Helpdesk Lite</h2>
        <p style="color: var(--text-muted); font-size: 14px;">v0.3.0 — «Где баги становятся фичами»</p>
      </div>

      <div style="margin-bottom: 28px;">
        <div style="font-size: 11px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; margin-bottom: 12px;">Стек технологий</div>
        <div class="tech-grid">
          <div class="tech-item">
            <div class="tech-name">Python / FastAPI</div>
            <div class="tech-desc">Бэкенд + SQLAlchemy + Alembic</div>
          </div>
          <div class="tech-item">
            <div class="tech-name">Vue 3 / Vite</div>
            <div class="tech-desc">Фронтенд + Pinia + Vue Router</div>
          </div>
          <div class="tech-item">
            <div class="tech-name">PostgreSQL / SQLite</div>
            <div class="tech-desc">База данных (выбор через Docker)</div>
          </div>
          <div class="tech-item">
            <div class="tech-name">Docker / Compose</div>
            <div class="tech-desc">Контейнеризация</div>
          </div>
          <div class="tech-item">
            <div class="tech-name">JWT / bcrypt</div>
            <div class="tech-desc">Аутентификация + Refresh tokens</div>
          </div>
          <div class="tech-item">
            <div class="tech-name">pytest / Vitest</div>
            <div class="tech-desc">66 тестов (52 backend + 14 frontend)</div>
          </div>
        </div>
      </div>

      <div style="margin-bottom: 28px;">
        <div style="font-size: 11px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; margin-bottom: 12px;">Возможности</div>
        <div class="feature-list">
          <div class="feature-item">CRUD для заявок, комментариев, категорий</div>
          <div class="feature-item">Пагинация, фильтрация, поиск, сортировка</div>
          <div class="feature-item">JWT + Refresh tokens + Rate limiting</div>
          <div class="feature-item">Роли: admin, junior_admin, moderator, user, guest</div>
          <div class="feature-item">Модерация заявок (on_moderation → new)</div>
          <div class="feature-item">Бан + предупреждения пользователей</div>
          <div class="feature-item">Система друзей (заявки, блокировка)</div>
          <div class="feature-item">Лайки (спасибо) на комментариях</div>
          <div class="feature-item">Загрузка файлов и фото с превью</div>
          <div class="feature-item">Аватарки пользователей</div>
          <div class="feature-item">SSE real-time уведомления</div>
          <div class="feature-item">Экспорт в CSV/XLSX</div>
          <div class="feature-item">Канбан-доска + Дашборд с графиками</div>
          <div class="feature-item">Тёмная тема + адаптивный дизайн</div>
          <div class="feature-item">Подписки на заявки + уведомления</div>
          <div class="feature-item">Alembic миграции + CI (GitHub Actions)</div>
        </div>
      </div>

      <div>
        <div style="font-size: 11px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; margin-bottom: 12px;">Запуск</div>
        <div class="code-block">
          <div><span style="color: var(--text-muted);"># Docker (рекомендуется)</span></div>
          <div>docker compose up --build</div>
          <div style="height: 6px;"></div>
          <div><span style="color: var(--text-muted);"># Без Docker</span></div>
          <div>cd backend</div>
          <div>pip install -r requirements.txt</div>
          <div>alembic upgrade head</div>
          <div>python seed.py</div>
          <div>uvicorn app.main:app --reload</div>
          <div style="height: 6px;"></div>
          <div>cd frontend</div>
          <div>npm install</div>
          <div>npm run dev</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.about {
  max-width: 640px;
  margin: 0 auto;
}

.tech-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.tech-item {
  padding: 14px;
  background: var(--bg-input);
  border-radius: 8px;
  border: 1px solid var(--border-light);
  transition: border-color 0.2s, background 0.3s;
}

.tech-item:hover {
  border-color: var(--border);
}

.tech-name {
  font-weight: 700;
  font-size: 14px;
  color: var(--text);
  margin-bottom: 2px;
}

.tech-desc {
  font-size: 12px;
  color: var(--text-dim);
}

.feature-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.feature-item {
  font-size: 14px;
  padding: 6px 10px;
  color: var(--text);
  background: var(--bg-input);
  border-radius: 6px;
  transition: background 0.2s;
}

.feature-item:hover {
  background: var(--bg-hover);
}

.code-block {
  background: var(--code-bg);
  color: var(--code-text);
  border-radius: 8px;
  padding: 16px 20px;
  font-family: 'SF Mono', 'Consolas', 'Liberation Mono', monospace;
  font-size: 13px;
  line-height: 1.7;
  overflow-x: auto;
}
</style>
