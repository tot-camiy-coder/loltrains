from fastapi import (Depends, Request, Response, APIRouter, Form)
from fastapi.responses import JSONResponse
from sqlalchemy import (select, func)
from backend.models.database import (get_db, AsyncSession)
from backend.models.User import User
from backend.models.Reputation import ReputationModel
from backend.tools.constant import COOKIE_NAME
from backend.tools.user.user import (get_user, give_token, try_get_user, hash_pw, verify_pw)
from backend.tools.random.imgs import (get_random_photos, get_random_banners)
from datetime import datetime

app = APIRouter()

@app.post("/register")
async def registration(
    req: Request, resp: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # проверка на существование
    already = await get_user(username, db)
    if already:
        return JSONResponse({"status": "AL"}, 400) # AlReady Has User
    
    # проверка IP
    client_ip = req.client.host
    forwarded = req.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(',')[0].strip()
        
    ext_count = await db.execute(select(func.count(User.id)).where(User.ip_address == client_ip))
    if ext_count.scalar() >= 3:
        return JSONResponse({"status": "TM"}, 403) # Too Much Accounts
    
    # создание нового пользователя
    user = User(
        username = username,
        nickname = username,
        description = "",
        password = hash_pw(password),

        photo = get_random_photos(),
        banner = get_random_banners(),

        role = "USER",
        ip_address = client_ip,
        last_login = datetime.now(),
        date_created = datetime.now()
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    db.add(ReputationModel(user_id=user.id))
    await db.commit()
 
    give_token(resp, user) # выдаём токен

    return {"status": "OK"}

@app.post('/login')
async def authentication_user(
    resp: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user(username, db)
    if not user or not verify_pw(password, user.password):
        return JSONResponse({"status": "WR"}, 403) # Wrong Password Or Login
    
    user.last_login = datetime.now()

    give_token(resp, user) # выдаём новый токен
    await db.commit()

    return {"status": "OK"} # всё окей

@app.post("/logout")
async def logout_user(
    resp: Response
):
    resp.delete_cookie(COOKIE_NAME)
    return {"status": "OK"} # всё окей

@app.get("/check")
async def checking(req: Request, resp: Response, db: AsyncSession = Depends(get_db)) -> bool:
    user = await try_get_user(req, db)
    if user:
        give_token(resp, user) # даём новый токен
        return True
    else:
        return False