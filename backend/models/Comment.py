from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.models.User import User
from datetime import datetime, UTC

class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    target_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(String(512))
    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))