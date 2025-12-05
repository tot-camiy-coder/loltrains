from backend.models.database import (get_db, AsyncSession)
from backend.tools.user.user import (get_user, check_role, try_get_user, give_token)
from backend.tools.user.profile import (get_user_dict, save_file)
from fastapi import (APIRouter, Request, Response, Form, Depends, Query, UploadFile, File)
from fastapi.responses import JSONResponse
from datetime import datetime
from backend.models import (User, Linked, Favorites, Reputation, Comment)
from sqlalchemy import select

app = APIRouter()

@app.get("/info")
async def get_info(
    req: Request, resp: Response,
    who: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    viewer = await try_get_user(req, db)
    if not (target := await get_user(who, db) or viewer): return JSONResponse({"status": "NF"}, 404)

    if viewer and viewer.username == target.username:
        give_token(resp, target)
    
    is_owner = getattr(viewer, 'username', None) == target.username
    vote = await db.execute(select(Reputation.Vote)
                            .filter(Reputation.Vote.voter_id == viewer.id)
                            .filter(Reputation.Vote.target_id == target.id))
    vote = vote.scalar_one_or_none()
    return {
        "target_user": await get_user_dict(target, is_owner, db),
        "viewer_user": await get_user_dict(viewer, is_owner, db),
        "is_owner": is_owner
    }

@app.post("/profile/edit")
async def profile_edit(
    req: Request, target: str = Form(...), nickname: str = Form(...), description: str = Form(...),
    photo: UploadFile = File(None), banner: UploadFile = File(None), db: AsyncSession = Depends(get_db)
):
    if not (sender := await try_get_user(req, db)): return JSONResponse({"status": "NA"}, 401)
    
    user = sender if sender.username == target else get_user(target, db)
    if not user or (sender.username != target and not check_role(sender.role, "SMODER")):
        return {"status": "NP" if user else "NF"}

    if (url := save_file(photo, "photos", user.photo, user.username)): user.photo = url
    if (url := save_file(banner, "profileb", user.banner, user.username)): user.banner = url

    user.description, user.nickname = description, (nickname or user.username)
    await db.commit()
    return {"status": "OK"}

@app.post("/profile/add_comment")
async def add_comment(req: Request, to: str = Form(...), body: str = Form(...), db: AsyncSession = Depends(get_db)):
    if not (sender := await try_get_user(req, db)): return JSONResponse({"status": "NA"}, 401)
    if not (target := await get_user(to, db)): return JSONResponse({"status": "NF"}, 404)

    comment = Comment.CommentModel(
        sender_id = sender.id,
        target_id = target.id,
        body = body,
        date = datetime.now()
    )
    db.add(comment)
    await db.commit()
    return {"status": "OK"}

@app.post("/profile/reputation")
async def change_reputation_user(
    req: Request, to: str = Form(...), action: int = Form(...), db: AsyncSession = Depends(get_db)
):
    if not (sender := await try_get_user(req, db)): return JSONResponse({"status": "NA"}, 401)
    if action not in (1, -1): return JSONResponse({"status": "ERR"}, 400)

    if not (target := await get_user(to, db)):
        return JSONResponse({"status": "NF"}, 404)

    print(f"Sender: {sender.username} | Target: {target.username} | self vote? -> {sender.username == target.username}")
    if sender.username == target.username: return {"status": "ERR", "detail": "Self-vote"}

    vote = await db.execute(select(Reputation.Vote)
                            .filter(Reputation.Vote.voter_id == sender.id)
                            .filter(Reputation.Vote.target_id == target.id))
    vote = vote.scalar_one_or_none()
    if vote:
        return JSONResponse({"status": "AL"}, 400)

    rep = await db.execute(select(Reputation.ReputationModel).filter(Reputation.ReputationModel.user_id == target.id))
    rep = rep.scalar_one_or_none()

    if action == 1:
        rep.likes += 1
    else:
        rep.dislikes += 1
    
    db.add(Reputation.Vote(
        voter_id = sender.id,
        target_id = target.id,
        value = action,
        date = datetime.now()
    ))

    await db.commit()

    return {"status": "OK"}
    
