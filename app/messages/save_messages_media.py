from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Message, Media
from app.core.llm_types import LLMType
from pydantic import BaseModel


async def save_llm_responses(results: dict, user_message: str, room_id: int, db: AsyncSession, llm_ids: list, image: str) -> tuple:
    responses = {}
    try:
        for llm_id in llm_ids:
            message_user = Message(
                room_id=room_id,
                role=True,
                llm_id=llm_id,
                content=user_message,
                created_at=datetime.now(),
                web_search_flag=False 
            )
            db.add(message_user)
            await db.commit()
            await db.refresh(message_user)

            media_user = Media(
                message_id=message_user.id,
                path=image,
                type=1
            )
            db.add(media_user)
            await db.commit()
            await db.refresh(media_user)

        response_messages = []

        for llm_id in llm_ids:
            reply = results.get(llm_id, "")
            if reply:
                
                message_response = Message(
                    room_id=room_id,
                    role=False,
                    llm_id=llm_id,
                    content=reply,
                    created_at=datetime.now(),
                    web_search_flag=False
                )
                db.add(message_response)
                await db.commit()
                await db.refresh(message_response)

                response_messages.append(message_response)
                responses[llm_id] = reply
        return response_messages


    except Exception as e:
        raise e
