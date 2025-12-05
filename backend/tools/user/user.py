from fastapi import (Depends, Request, Response)
from backend.models.database import (get_db, AsyncSession)
from backend.models.User import User
from backend.tools.constant import *
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy import select
from typing import Literal
from dotenv import load_dotenv
import os
load_dotenv()

roles = Literal["USER", "JMODER", "SMODER", "ADMIN", "SADMIN", "OWNER"]

crypt = CryptContext(schemes=["bcrypt"])
def hash_pw(password: str) -> str:
    return crypt.hash(password)
def verify_pw(password: str, hash: str) -> bool:
    return crypt.verify(password, hash=hash) 

async def get_user(username: str, db: AsyncSession = Depends(get_db)) -> User:
    """
    🔎 Поиск пользователя по нику \n
    return User | None
    """
    result = await db.execute(
        select(User).filter_by(username=username)
    )
    user = result.scalar_one_or_none()
    return user

async def get_user_by_ID(id: int, db: AsyncSession = Depends(get_db)) -> User:
    """
    🔎 Поиск пользователя по нику \n
    return User | None
    """
    result = await db.execute(
        select(User).filter_by(id=id)
    )
    user = result.scalar_one_or_none()
    return user

async def try_get_user(req: Request, db: AsyncSession = Depends(get_db)):
    """
    ⚙️ Пытается получить пользователя из `Request` \n
    return User | None
    """
    token = req.cookies.get(COOKIE_NAME)
    if not token:
        return None # нету токена = err 401
    
    try:
        payload = jwt.decode(token, os.environ.get("key"))
        username = payload.get('sub')

        user = await get_user(username, db)
        return user # User | None - есть ли пользователь за токеном? (всё окей, в основном)
    except JWTError:
        return None # неверный токен
    
def give_token(resp: Response, user: User):
    """
    ✏️ вписывает в `Response` новый токен
    """
    data = {
        'sub': user.username, # пользователь, чтобы можно было из токена узнать кто это.
        'exp': datetime.utcnow() + timedelta(minutes=TOKEN_LIFE) # текущее время + время жизни токена
    }
    token = jwt.encode(data, SECRET_KEY)
    resp.set_cookie(COOKIE_NAME, token, TOKEN_LIFE, httponly=True)

def check_role(role_a: str, role_b: str) -> bool:
    """
    💎 Проверят роль выше или ровно \n
    return bool
    """
    ROLES_ORDER = list(roles.__args__)
    if not all(r in ROLES_ORDER for r in [role_a, role_b]):
        raise ValueError("Одна или обе роли не существуют.")

    index_a = ROLES_ORDER.index(role_a)
    index_b = ROLES_ORDER.index(role_b)

    return index_a >= index_b