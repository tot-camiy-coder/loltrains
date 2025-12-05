"""
Made with ❤️ by @snowlover4ever
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api.rzd_api import rzd_api
import uvicorn
from backend.models.database import init_db, engine
from backend.models import (User, Comment, Favorites, Linked, Report, Reputation)
from backend.routes import (auth, profile)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()

app = FastAPI(openapi_url="/debug", lifespan=lifespan)
app.include_router(rzd_api)
app.include_router(auth.app)
app.include_router(profile.app)
app.mount("/media", StaticFiles(directory="media"), name="media") 

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)