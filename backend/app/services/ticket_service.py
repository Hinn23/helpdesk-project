from sqlalchemy.orm import Session
from app.repositories.ticket_repo import TicketRepository
from app.models.ticket import Ticket
from app.models.audit_log import AuditLog


def _audit(db: Session, ticket_id: int, user_name: str, action: str, field: str = None, old_value: str = None, new_value: str = None):
    db.add(AuditLog(
        ticket_id=ticket_id, user_name=user_name,
        action=action, field=field,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
    ))
    db.commit()


class TicketService:
    def __init__(self, db: Session):
        self.repo = TicketRepository(db)
        self.db = db

    def get_all_filtered(self, skip=0, limit=100, status=None, priority=None, search=None, category_id=None, assignee_id=None, author_id=None, date_from=None, date_to=None, sort="created_at", order="desc"):
        return self.repo.get_all_filtered(skip, limit, status, priority, search, category_id, assignee_id, author_id, date_from, date_to, sort, order)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip, limit)

    def get_by_id(self, ticket_id: int):
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Заявка не найдена")
        return ticket

    def create(self, data, user_name: str = None):
        ticket = Ticket(**data.model_dump())
        result = self.repo.create(ticket)
        _audit(self.db, result.id, user_name or "system", "created")
        return result

    def update(self, ticket_id: int, data, user_name: str = None):
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Заявка не найдена")
        old = {c.name: getattr(ticket, c.name) for c in ticket.__table__.columns}
        for key, val in data.model_dump(exclude_unset=True).items():
            setattr(ticket, key, val)
        result = self.repo.update(ticket)
        for key, val in data.model_dump(exclude_unset=True).items():
            old_val = old.get(key)
            if str(old_val) != str(val):
                _audit(self.db, ticket_id, user_name or "system", "changed", field=key, old_value=old_val, new_value=val)
        return result

    def delete(self, ticket_id: int):
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Заявка не найдена")
        self.repo.delete(ticket)

    def count(self):
        return self.repo.count()
