from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_async_db
from app.models.models import Room, Message
from pydantic import BaseModel
from datetime import datetime
from app.core.security import oauth2_scheme, verify_access_token

router = APIRouter()

@router.get("/chat/history")
async def get_rooms(
    user_id: int,
    db: AsyncSession = Depends(get_async_db), 
    # access_token: str = Depends(oauth2_scheme)
    ):
    # payload = verify_access_token(access_token)
    result = await db.execute(select(Room).where(Room.user_id == user_id))
    rooms = result.scalars().all()
    if not rooms:
        raise HTTPException(status_code=404, detail="Rooms not found")
    return rooms