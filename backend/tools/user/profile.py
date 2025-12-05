from backend.models.database import (get_db, AsyncSession)
from backend.models import (User, Linked, Favorites, Reputation, Comment)
from backend.tools.user.user import (get_user, check_role, try_get_user, give_token, get_user_by_ID)
from fastapi import (APIRouter, Request, Response, Form, Depends, Query, UploadFile, File)
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import (select, func)
from datetime import datetime
from pathlib import Path
import shutil

async def get_user_dict(user: User.User, is_owner: bool, db: AsyncSession = None, full: bool = True):
    if not user: 
        return None

    base = {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "photo": user.photo,
    }
    
    if not full:
        return base

    
    linked = await db.execute(
        select(Linked.LinkedTrainModel).filter(Linked.LinkedTrainModel.user_id == user.id)
    )
    linked = linked.scalar_one_or_none()

    favorites = await db.execute(
        select(Favorites.FavoritesModel).filter(Favorites.FavoritesModel.user_id == user.id)
    )
    favorites = favorites.scalar_one_or_none()

    reputation = await db.execute(
        select(Reputation.ReputationModel).filter(Reputation.ReputationModel.user_id == user.id)
    )
    reputation = reputation.scalar_one_or_none()

    comments = await db.execute(
        select(Comment.CommentModel).filter(Comment.CommentModel.target_id == user.id)
    )
    comments = comments.scalars().all()

    formatted_comments = []
    for com in comments:
        sender_user = await get_user_by_ID(com.sender_id, db)
        sender_dict = await get_user_dict(sender_user, False, db, False)
        
        formatted_comments.append({
            "id": com.id,
            "body": com.body,
            "timestamp": com.date.isoformat(),
            "sender": sender_dict
        })
    formatted_comments.reverse()

    return {
        **base,
        "description": user.description,
        "banner": user.banner,
        "rank": user.rank,
        "role": user.role,
        "achievements": user.achievements,
        
        "date_created": user.date_created.strftime("%d-%m-%Y") if user.date_created else None,

        "linked": linked if is_owner and linked else None,
        "favorites": favorites if is_owner and favorites else None,
        "reputation": reputation,
        
        "comments": formatted_comments
    }

def save_file(file: UploadFile, folder: str, current_url: str | None, username: str) -> str | None:
    if not file or not file.filename:
        return None
    
    if current_url:
        clean_path = current_url.replace("/api/", "").lstrip("/")
        old_path = Path(clean_path)
        
        if old_path.exists() and old_path.is_file():
            try:
                if not "defaults" in str(old_path):
                    old_path.unlink()
            except OSError as e:
                print(f"Error deleting file {old_path}: {e}")

    save_dir = Path(f"media/{folder}")
    save_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().timestamp()
    extension = Path(file.filename).suffix
    fname = f"{username}_{folder}_{timestamp}{extension}"
    dest = save_dir / fname
    
    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    dest_str = str(dest).replace('\\', '/')
    return f"/api/{dest_str}"