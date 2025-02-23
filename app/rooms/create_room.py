from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Room




async def create_room(user_id: int, db: AsyncSession) -> Room:

    async with db.begin(): 
        new_room = Room(
            user_id=user_id,
            title="New Chat",
            created_at=datetime.now()
        )
        db.add(new_room)

    return new_room
