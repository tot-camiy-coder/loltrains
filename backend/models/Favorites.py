from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.models.User import User

class FavoritesModel(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    code0: Mapped[str] = mapped_column() # from CODE
    code1: Mapped[str] = mapped_column() # to CODE
    name0: Mapped[str] = mapped_column() # from NAME
    name1: Mapped[str] = mapped_column() # to NAME

    user: Mapped["User"] = relationship(back_populates="favorites")
