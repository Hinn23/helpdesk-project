from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.comment import CommentCreate, CommentRead
from app.services.comment_service import CommentService
from app.services.ticket_service import TicketService
from app.auth import get_optional_user, get_current_user
from app.models.comment_thanks import CommentThanks
from app.sse import events as sse_events


router = APIRouter(prefix="/tickets/{ticket_id}/comments", tags=["comments"])


@router.get("/", response_model=list[CommentRead])
def list_comments(ticket_id: int, db: Session = Depends(get_db), current_user=Depends(get_optional_user)):
    try:
        TicketService(db).get_by_id(ticket_id)
    except ValueError:
        raise HTTPException(404, f"Заявка #{ticket_id} не найдена. Комментировать призрак?")
    comments = CommentService(db).get_by_ticket(ticket_id)
    user_id = current_user.id if current_user else -1
    result = []
    for c in comments:
        thanks_count = db.query(CommentThanks).filter(CommentThanks.comment_id == c.id).count()
        is_thanked = db.query(CommentThanks).filter(CommentThanks.comment_id == c.id, CommentThanks.user_id == user_id).first() is not None
        result.append(CommentRead(
            id=c.id, ticket_id=c.ticket_id, author_id=c.author_id,
            author_name=c.author_name, text=c.text, created_at=c.created_at,
            thanks_count=thanks_count, is_thanked=is_thanked, is_response=c.is_response or 0,
        ))
    return result


@router.post("/", response_model=CommentRead, status_code=201)
def create_comment(ticket_id: int, data: CommentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        ticket = TicketService(db).get_by_id(ticket_id)
    except ValueError:
        raise HTTPException(404, f"Какой тикет #{ticket_id}? Его нет в природе")
    if ticket.status == "closed" and current_user.role not in ("admin", "junior_admin", "moderator"):
        raise HTTPException(403, "Заявка закрыта. Только персонал может оставлять ответы.")
    is_response = 1 if current_user.role in ("admin", "junior_admin", "moderator") else 0
    comment = CommentService(db).create_response(ticket_id, data.text, current_user.id, current_user.name, is_response)
    return CommentRead(
        id=comment.id, ticket_id=comment.ticket_id, author_id=comment.author_id,
        author_name=comment.author_name, text=comment.text, created_at=comment.created_at,
        thanks_count=0, is_thanked=False, is_response=comment.is_response or 0,
    )


@router.delete("/{comment_id}", status_code=204)
def delete_comment(ticket_id: int, comment_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    svc = CommentService(db)
    comment = svc.get_by_id(comment_id)
    if current_user.role != "admin" and comment.author_id != current_user.id:
        raise HTTPException(403, "Не трожь чужой комментарий. Свои удаляй")
    try:
        svc.delete(comment_id)
        if current_user.id != comment.author_id:
            sse_events.broadcast_sync("comment_deleted", {
                "user_id": comment.author_id, "user_name": comment.author_name,
                "by_user_name": current_user.name, "ticket_id": ticket_id,
            })
    except ValueError:
        raise HTTPException(404, f"Комментарий #{comment_id} испарился. Наверное, стеснительный")


@router.post("/{comment_id}/thanks")
def toggle_thanks(ticket_id: int, comment_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    existing = db.query(CommentThanks).filter(
        CommentThanks.comment_id == comment_id,
        CommentThanks.user_id == current_user.id,
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"thanked": False, "thanks_count": db.query(CommentThanks).filter(CommentThanks.comment_id == comment_id).count()}
    db.add(CommentThanks(comment_id=comment_id, user_id=current_user.id))
    db.commit()
    return {"thanked": True, "thanks_count": db.query(CommentThanks).filter(CommentThanks.comment_id == comment_id).count()}
