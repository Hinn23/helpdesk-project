from sqlalchemy.orm import Session
from app.repositories.comment_repo import CommentRepository
from app.models.comment import Comment


class CommentService:
    def __init__(self, db: Session):
        self.repo = CommentRepository(db)

    def get_by_ticket(self, ticket_id: int):
        return self.repo.get_by_ticket(ticket_id)

    def get_by_id(self, comment_id: int):
        comment = self.repo.get_by_id(comment_id)
        if not comment:
            raise ValueError("Комментарий не найден")
        return comment

    def create(self, ticket_id: int, text: str, author_id: int, author_name: str):
        comment = Comment(ticket_id=ticket_id, text=text, author_id=author_id, author_name=author_name, is_response=0)
        return self.repo.create(comment)

    def create_response(self, ticket_id: int, text: str, author_id: int, author_name: str, is_response: int = 1):
        comment = Comment(ticket_id=ticket_id, text=text, author_id=author_id, author_name=author_name, is_response=is_response)
        return self.repo.create(comment)

    def delete(self, comment_id: int):
        comment = self.repo.get_by_id(comment_id)
        if not comment:
            raise ValueError("Комментарий не найден")
        self.repo.delete(comment)
