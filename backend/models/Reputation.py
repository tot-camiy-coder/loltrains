from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.models.User import User
from datetime import datetime, UTC

class ReputationModel(Base):
    __tablename__ = "reputations"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    likes: Mapped[int] = mapped_column(default=0)
    dislikes: Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(back_populates="reputation")

class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True)
    voter_id: Mapped[int] = mapped_column(ForeignKey("users.id")) # кто голосовал
    target_id: Mapped[int] = mapped_column(ForeignKey("users.id")) # за кого
    value: Mapped[int] # +1 или -1

    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))