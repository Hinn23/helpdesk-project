import os, uuid, shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, get_optional_user
from app.models.user import User
from app.models.attachment import Attachment
from app.services.ticket_service import TicketService
from app.config import DATABASE_URL

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/tickets/{ticket_id}/attachments", tags=["attachments"])

MAX_SIZE = 10 * 1024 * 1024


@router.get("")
def list_attachments(ticket_id: int, db: Session = Depends(get_db), _=Depends(get_optional_user)):
    files = db.query(Attachment).filter(Attachment.ticket_id == ticket_id).all()
    return [
        {
            "id": f.id,
            "original_name": f.original_name,
            "file_size": f.file_size,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in files
    ]


@router.post("", status_code=201)
async def upload_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    TicketService(db).get_by_id(ticket_id)
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(413, "Файл больше 10 МБ, не дозволено")
    ext = os.path.splitext(file.filename)[1] or ""
    stored_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, stored_name)
    with open(filepath, "wb") as f:
        f.write(contents)
    att = Attachment(
        ticket_id=ticket_id,
        user_id=current_user.id,
        filename=stored_name,
        original_name=file.filename,
        file_size=len(contents),
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return {"id": att.id, "original_name": att.original_name, "file_size": att.file_size}


@router.get("/{attachment_id}")
def download_attachment(ticket_id: int, attachment_id: int, db: Session = Depends(get_db), _=Depends(get_optional_user)):
    att = db.query(Attachment).filter(Attachment.id == attachment_id, Attachment.ticket_id == ticket_id).first()
    if not att:
        raise HTTPException(404, "Файл не найден")
    filepath = os.path.join(UPLOAD_DIR, att.filename)
    if not os.path.exists(filepath):
        raise HTTPException(404, "Файл удалён с сервера")
    return FileResponse(filepath, filename=att.original_name)
