from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.ticket import Ticket
from app.models.subscription import Subscription
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets/{ticket_id}/subscriptions", tags=["subscriptions"])
user_router = APIRouter(prefix="/subscriptions", tags=["user-subscriptions"])


@user_router.get("")
def list_my_subscriptions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subs = (
        db.query(Subscription, Ticket)
        .join(Ticket, Subscription.ticket_id == Ticket.id)
        .filter(Subscription.user_id == current_user.id)
        .order_by(Ticket.updated_at.desc())
        .all()
    )
    return [
        {
            "id": sub.id,
            "ticket_id": sub.ticket_id,
            "ticket_title": ticket.title,
            "ticket_status": ticket.status,
        }
        for sub, ticket in subs
    ]


@router.get("")
def get_subscription(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.ticket_id == ticket_id,
    ).first()
    return {"subscribed": sub is not None}


@router.post("")
def subscribe(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    TicketService(db).get_by_id(ticket_id)
    existing = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.ticket_id == ticket_id,
    ).first()
    if existing:
        return {"detail": "Уже подписаны"}
    db.add(Subscription(user_id=current_user.id, ticket_id=ticket_id))
    db.commit()
    return {"detail": "Подписка оформлена"}


@router.delete("")
def unsubscribe(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.ticket_id == ticket_id,
    ).first()
    if not sub:
        raise HTTPException(404, "Не подписаны")
    db.delete(sub)
    db.commit()
    return {"detail": "Подписка отменена"}
