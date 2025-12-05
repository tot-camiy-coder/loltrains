from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.database import Base
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.models.User import User

class LinkedTrainModel(Base):
    __tablename__ = "linked_trains"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    train_number: Mapped[str] = mapped_column()
    route0: Mapped[str] = mapped_column() # from
    route1: Mapped[str] = mapped_column() # to

    arrival_time: Mapped[datetime] = mapped_column(DateTime) # time to delete link

    user: Mapped["User"] = relationship(back_populates="linked")
