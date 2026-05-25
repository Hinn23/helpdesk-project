from datetime import datetime, timedelta, timezone
from app.database import SessionLocal, engine, Base
from app.models import User, Ticket, Comment, Category
from app.auth import hash_password


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

Base.metadata.create_all(bind=engine)

db = SessionLocal()

if db.query(User).first():
    print("== Данные уже есть, сид пропущен ==")
    db.close()
    exit()

admin = User(name="Admin", email="admin@gmail.com", password=hash_password("admin123"), role="admin")
user1 = User(name="Алиса", email="alice@gmail.com", password=hash_password("alice123"), role="user")
user2 = User(name="Боб", email="bob@mail.ru", password=hash_password("bob123"), role="user")
db.add_all([admin, user1, user2])
db.commit()

cat1 = Category(name="Баги", description="Не баги, а сюрпризы")
cat2 = Category(name="Улучшения", description="Хотим всё и сразу")
cat3 = Category(name="Поддержка", description="Спасите-помогите")
cat4 = Category(name="Документация", description="Где это написано?")
db.add_all([cat1, cat2, cat3, cat4])
db.commit()

tickets_data = [
    Ticket(title="Страница логина падает в обморок", description="При нажатии 'Войти' сервер говорит 'нет' и падает с 500. Хотя пароль я помню, честно!", status="in_progress", priority="high", assignee_id=user1.id, author_id=admin.id, category_id=cat1.id, deadline=_utcnow() + timedelta(days=2)),
    Ticket(title="Хочу тёмную тему — глаза выжигает", description="Светлая тема — враг фронтендера. Дайте мрак!", status="new", priority="low", assignee_id=user2.id, author_id=user1.id, category_id=cat2.id, deadline=_utcnow() + timedelta(days=14)),
    Ticket(title="Письмо для сброса пароля улетело в космос", description="Нажал 'сбросить пароль' — тишина. Ни письма, ни ошибки. Только экзистенциальная пустота.", status="done", priority="high", assignee_id=user1.id, author_id=admin.id, category_id=cat1.id),
    Ticket(title="Дока API: пишем новую, старую забыли", description="Эндпоинты новые есть, а в документации — только привет, мир", status="new", priority="medium", assignee_id=user2.id, author_id=user2.id, category_id=cat4.id, deadline=_utcnow() + timedelta(days=5)),
    Ticket(title="Список заявок грузится как на 56k модеме", description="5 секунд на 1000 записей. В 2026 такое простительно только если сервер на картошке работает", status="in_progress", priority="high", assignee_id=user1.id, author_id=admin.id, category_id=cat1.id),
    Ticket(title="Хочу экспорт в CSV — начальник требует отчёт", description="Excel сам себя не заполнит. А начальник сам не успокоится", status="new", priority="medium", assignee_id=user2.id, author_id=user1.id, category_id=cat2.id, deadline=_utcnow() + timedelta(days=7)),
    Ticket(title="Аватарка не грузится — 413 Entity Too Large", description="Пытался загрузить фото в 4K. Ок, я понял, надо сжать. Но ошибка могла бы быть подобрее", status="cancelled", priority="medium", assignee_id=user1.id, author_id=user2.id, category_id=cat1.id),
    Ticket(title="Поиск заявок по номеру — срочно!", description="У нас 5000 заявок, искать глазами — боль. Ctrl+F не помогает", status="new", priority="low", assignee_id=user2.id, author_id=admin.id, category_id=cat2.id),
    Ticket(title="Настроить бэкапы — чтобы не плакать потом", description="Если упадёт база — я увольняюсь. Давайте сделаем бекап ежедневным", status="new", priority="medium", assignee_id=user1.id, author_id=user2.id, category_id=cat3.id, deadline=_utcnow() + timedelta(days=10)),
    Ticket(title="Мобильная версия едет криво", description="На телефоне всё наползает друг на друга. Выглядит как современное искусство, но пользователи не оценили", status="new", priority="high", assignee_id=user2.id, author_id=admin.id, category_id=cat2.id, deadline=_utcnow() + timedelta(days=3)),
    Ticket(title="Уведомления на почту — хочу спам по делу", description="Когда заявку обновляют — пусть приходит письмо. А не как сейчас: тишина и надежда", status="new", priority="medium", assignee_id=user1.id, author_id=user1.id, category_id=cat2.id, deadline=_utcnow() + timedelta(days=6)),
    Ticket(title="Компоненты-заглушки для загрузки", description="Пока данные грузятся — показывать скелетоны. А не белый экран смерти", status="new", priority="low", assignee_id=user2.id, author_id=admin.id, category_id=cat2.id),
]
db.add_all(tickets_data)
db.commit()

comments_data = [
    Comment(ticket_id=1, author_id=2, author_name="Алиса", text="Нашла баг — mystrcmp сравнивает не те строки. Чиню"),
    Comment(ticket_id=1, author_id=1, author_name="Админ", text="Горит! Это ж прод. Давай быстрее, я в тебя верю"),
    Comment(ticket_id=3, author_id=3, author_name="Боб", text="SMTP-сервер лежал. Поднял. Письма полетели"),
    Comment(ticket_id=3, author_id=1, author_name="Админ", text="Боб — герой дня. Закрываю"),
    Comment(ticket_id=5, author_id=2, author_name="Алиса", text="Добавила индекс на created_at. Теперь летает — 200мс"),
    Comment(ticket_id=5, author_id=1, author_name="Админ", text="Красота! Понаблюдаем недельку и можно забыть об этом"),
    Comment(ticket_id=6, author_id=3, author_name="Боб", text="Начал. Пока только читаю документацию к openpyxl"),
    Comment(ticket_id=6, author_id=1, author_name="Админ", text="Боб, docs — это хорошо, но код пиши тоже"),
    Comment(ticket_id=10, author_id=3, author_name="Боб", text="Там flexbox едет. Надо брейкпоинты фиксить"),
    Comment(ticket_id=10, author_id=1, author_name="Админ", text="Юзай media queries. Без bootstrap — мы не в 2015"),
    Comment(ticket_id=11, author_id=2, author_name="Алиса", text="Шаблон письма наметила. Покажи пример, что писать"),
    Comment(ticket_id=11, author_id=1, author_name="Админ", text="Придумай что-нибудь тёплое и ламповое, но по делу"),
    Comment(ticket_id=11, author_id=2, author_name="Алиса", text="Готово! Шаблон: 'Ваша заявка номер N обновлена. Подробнее: ссылка'. Лаконично и с душой"),
]
db.add_all(comments_data)
db.commit()

db.close()
print("== Сид завершён ==")
print(f"  Пользователей:  3")
print(f"  Категорий:      4")
print(f"  Заявок:         {len(tickets_data)}")
print(f"  Комментариев:   {len(comments_data)}")
