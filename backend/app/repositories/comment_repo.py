from sqlalchemy.orm import Session
from app.models.comment import Comment


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_ticket(self, ticket_id: int):
        return self.db.query(Comment).filter(Comment.ticket_id == ticket_id).all()

    def get_by_id(self, comment_id: int):
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def create(self, comment: Comment):
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete(self, comment: Comment):
        self.db.delete(comment)
        self.db.commit()
