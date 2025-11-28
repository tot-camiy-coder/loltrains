"""
Made with ❤️ by @snowlover4ever
"""
from fastapi import FastAPI
from backend.api.rzd_api import rzd_api
import uvicorn

app = FastAPI(openapi_url="/debug")
app.include_router(rzd_api)

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)