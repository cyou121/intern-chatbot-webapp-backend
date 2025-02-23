from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database.session import get_async_db
from app.models.models import Room, Message
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.core.security import oauth2_scheme, verify_access_token
from app.messages.media_upload import generate_presigned_url
from sqlalchemy import case

router = APIRouter()
VALID_TIME=900

@router.get("/{room_id}")
async def get_messages(
    room_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    # access_token: str = Depends(oauth2_scheme)
    ):
    # payload = verify_access_token(access_token)
    result = await db.execute(select(Message).options(joinedload(Message.medias)).where(Message.room_id == room_id).order_by(Message.created_at,case((Message.role == True, 0),else_=1)))
    messages = result.unique().scalars().all()
    if not messages:
        raise HTTPException(status_code=404, detail="Messages not found")
    for message in messages:
        presigned_urls = []
        for media in message.medias:
            if media.path:
                presigned_url = generate_presigned_url(media.path, VALID_TIME)
                presigned_urls.append(presigned_url)
        message.image = presigned_urls
    return messages


