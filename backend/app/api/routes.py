from fastapi import APIRouter

from app.api import chat, db, llm, result, sql


api_router = APIRouter()
api_router.include_router(llm.router)
api_router.include_router(db.router)
api_router.include_router(sql.router)
api_router.include_router(chat.router)
api_router.include_router(result.router)
