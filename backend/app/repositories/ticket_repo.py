from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.ticket import Ticket


SORTABLE_FIELDS = {"title", "status", "priority", "created_at", "updated_at", "deadline"}


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_filtered(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        assignee_id: Optional[int] = None,
        author_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort: str = "created_at",
        order: str = "desc",
    ):
        query = self.db.query(Ticket)

        if status:
            query = query.filter(Ticket.status == status)
        if priority:
            query = query.filter(Ticket.priority == priority)
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(Ticket.title.ilike(like), Ticket.description.ilike(like))
            )
        if category_id:
            query = query.filter(Ticket.category_id == category_id)
        if assignee_id:
            query = query.filter(Ticket.assignee_id == assignee_id)
        if author_id:
            query = query.filter(Ticket.author_id == author_id)
        if date_from:
            query = query.filter(Ticket.created_at >= date_from)
        if date_to:
            query = query.filter(Ticket.created_at <= date_to)

        total = query.count()

        sort_field = getattr(Ticket, sort, None) if sort in SORTABLE_FIELDS else Ticket.created_at
        order_func = sort_field.desc() if order == "desc" else sort_field.asc()
        query = query.order_by(order_func)

        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Ticket).offset(skip).limit(limit).all()

    def get_by_id(self, ticket_id: int):
        return self.db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def create(self, ticket: Ticket):
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def update(self, ticket: Ticket):
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def delete(self, ticket: Ticket):
        self.db.delete(ticket)
        self.db.commit()

    def count(self):
        return self.db.query(Ticket).count()
