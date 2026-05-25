# Helpdesk Lite

Fullstack-проект: расширенная система управления заявками (тикетами) с коммуникационным модулем.

**Стек:** Python 3.11 / FastAPI / SQLAlchemy / PostgreSQL / Vue 3 / Vite / Docker

---

## Быстрый старт (Docker)

```bash
cp backend/.env.example .env
docker compose up --build
```

Создайте корневой `.env` со следующими переменными:
```
SECRET_KEY=dev-secret-key
REFRESH_SECRET_KEY=dev-refresh-secret-key
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- **MailHog: http://localhost:8025** (письма с кодом регистрации и сбросом пароля)

## Без Docker

### Backend

```bash
cd backend
cp .env.example .env
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Тестовые пользователи

| Логин | Пароль | Роль |
|-------|--------|------|
| admin@gmail.com | admin123 | Админ |
| alice@gmail.com | alice123 | Пользователь |
| bob@mail.ru | bob123 | Пользователь |

## Регистрация и MailHog

Регистрация устроена через email-код подтверждения.  
При запуске через Docker код можно посмотреть в MailHog: [http://localhost:8025](http://localhost:8025)  
В режиме разработки код возвращается в ответе API (`code_for_test`) для удобства тестирования.

## Функции

### Ядро (Helpdesk)
- CRUD заявок с пагинацией, фильтрацией, поиском
- JWT-аутентификация + Refresh tokens
- Роли: admin, junior_admin, moderator, user, support, manager
- Модерация заявок (on_moderation → new)
- Закрытие заявок (closed — только для персонала)
- Комментарии и ответы персонала (раздельные блоки)
- Подписки на заявки
- Экспорт CSV/XLSX с учётом фильтров
- Канбан-доска + Дашборд с графиками
- Журнал действий (аудит)

### Коммуникационный модуль (социальные функции)
- **Друзья** — добавление, принятие, отклонение, блокировка
- **Личные сообщения** — чат между пользователями с историей диалогов
- **Лента событий** — подписки на пользователей и их активность
- **Лайки/Спасибо** — на комментариях + титулы пользователей
- **Аватарки и профили** — загрузка файлов с превью
- **Уведомления** — SSE (колокольчик в навбаре) с событиями

> Проект расширяет классический Helpdesk коммуникационным модулем — друзья, чаты, лента и лайки.  
> Это сделано для демонстрации навыков проектирования fullstack-приложения и не мешает основной функциональности.

### Дополнительно
- Тёмная тема + адаптивный дизайн
- Регистрация с подтверждением по email (MailHog)
- Сброс пароля
- Бан и предупреждения пользователей
- CI (GitHub Actions)

## Структура проекта

```
helpdesk-project/
├── backend/
│   ├── app/
│   │   ├── api/           # Эндпоинты
│   │   ├── models/        # SQLAlchemy модели
│   │   ├── schemas/       # Pydantic схемы
│   │   ├── services/      # Бизнес-логика
│   │   ├── repositories/  # Доступ к данным
│   │   ├── main.py        # Точка входа
│   │   ├── auth.py        # JWT + пароли
│   │   ├── config.py      # Конфигурация
│   │   ├── database.py    # Подключение к БД
│   │   └── ratelimit.py   # Rate limiter
│   ├── tests/             # Тесты (52 шт)
│   ├── alembic/           # Миграции
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/           # API-клиенты
│   │   ├── components/    # Компоненты
│   │   ├── pages/         # Страницы
│   │   ├── router/        # Маршруты
│   │   ├── stores/        # Pinia store
│   │   └── __tests__/     # Тесты (14 шт)
│   └── package.json
├── docs/                  # Документация
└── docker-compose.yml     # Docker Compose
```

## Тесты

```bash
# Backend (52 теста)
cd backend
pytest -v

# Frontend (14 тестов)
cd frontend
npm test
```
