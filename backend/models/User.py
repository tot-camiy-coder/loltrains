from sqlalchemy import String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.mutable import MutableDict
from backend.models.database import Base
from datetime import datetime, UTC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.models.Linked import LinkedTrainModel
    from backend.models.Favorites import FavoritesModel
    from backend.models.Reputation import ReputationModel
    from backend.models.Comment import CommentModel


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(String(512))
    password: Mapped[str] = mapped_column()

    photo: Mapped[str] = mapped_column()
    banner: Mapped[str] = mapped_column()
    status: Mapped[str | None] = mapped_column(String(64), default=None)
    rank: Mapped[str | None] = mapped_column(String(64), default=None)

    linked: Mapped["LinkedTrainModel"] = relationship(back_populates="user")
    favorites: Mapped[list["FavoritesModel"]] = relationship(back_populates="user")
    role: Mapped[str] = mapped_column(String(64))
    achievements: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON), default=dict)

    ip_address: Mapped[str] = mapped_column()
    last_login: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    date_created: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    reputation: Mapped["ReputationModel"] = relationship(back_populates="user")
"""
    🎲 Роли:
        USER - обычный пользователь
        PREMIUM - улучшенный пользователь

        JMODER - Junior Moderator | Младший Модератор
            Возможность отправлять запросы на: 
                - удаление комментариев
                - удаление сообщений 
                - изменение профиля
            Имеет возможность:
                - просматривать жалобы (и отправлять запросы)
                - мут пользователя (до 15 минут)

        SMODER - Senior Moderator | Старший Модератор
            Возможность:
                - удалять комментарии
                - удалять сообщения
                - изменять профиль
                - мут пользователя (до 7 часа)
                - просматривать жалобы
                - просматривать логи
                - просматривать список пользователей
            Имеет возможность:
                - отправить запрос на бан пользователя

        ADMIN - Админ
            Возможность:
                - всё что умеет SMODER
                - мут пользователей (без ограничений)
                - банить пользователей (кроме ADMIN, SADMIN, OWNER)
                - изменять пользователей полностью 
        
        SADMIN - Senior Admin | Старший админ
            Возможность:
                - всё что умеет ADMIN
                - просматривать логи консоли
        
        OWNER - Основатель
            Возможность:
                - всё что умеет SADMIN
                - банить пользователей (без ограничений)
                - нет никаких ограничений                
"""