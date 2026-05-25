from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from app.database import Base
from datetime import datetime, timezone


class CommentThanks(Base):
    __tablename__ = "comment_thanks"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", name="uq_comment_user_thanks"),
    )
