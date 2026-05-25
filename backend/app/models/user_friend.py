from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from app.database import Base
from datetime import datetime, timezone


class UserFriend(Base):
    __tablename__ = "user_friends"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    friend_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    __table_args__ = (
        UniqueConstraint("user_id", "friend_id", name="uq_user_friend"),
    )
