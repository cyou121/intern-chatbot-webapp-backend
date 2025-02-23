from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth
from app.api.endpoints import register
from app.api.endpoints import llm_chat
from app.api.endpoints import chatroom
from app.core.config import settings
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models.models import User, Room, Message, Llm, Media

from app.database.session import get_async_db

from app.api.endpoints.chatroom import router as chatroom_router
from app.api.endpoints.message import router as message_router
from app.api.endpoints.llm_chat import router as ai_router
import requests

app = FastAPI()


app.include_router(message_router, prefix="/chat/chatrooms", tags=["latest message"])
app.include_router(ai_router, prefix="", tags=["ai"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: 本番環境では適切に設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(register.router, prefix="/register", tags=["User Register"])

@app.get("/users/")
async def get_users(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    if not users:
        raise HTTPException(status_code=404, detail="Users not found")
    return users

@app.get("/rooms/")
async def get_rooms(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Room))
    rooms = result.scalars().all()
    if not rooms:
        raise HTTPException(status_code=404, detail="Rooms not found")
    return rooms

@app.get("/messages/")
async def get_messages(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Message))
    messages = result.scalars().all()
    if not messages:
        raise HTTPException(status_code=404, detail="Messages not found")
    return messages

@app.get("/llms/")
async def get_messages(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Llm))
    llms = result.scalars().all()
    if not llms:
        raise HTTPException(status_code=404, detail="Messages not found")
    return llms

@app.get("/medias/")
async def get_messages(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Media))
    medias = result.scalars().all()
    if not medias:
        raise HTTPException(status_code=404, detail="Messages not found")
    return medias


app.include_router(llm_chat.router)
app.include_router(chatroom.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)