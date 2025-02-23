from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Message, Media
from app.core.llm_types import LLMType
from pydantic import BaseModel
import openai
from app.core.config import settings

MAX_INDEX_SIZE = 2704
client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

async def summarize_text(text: str) -> str:
    prompt = f"以下の内容を要約し、情報を完全に保ちつつ、より簡潔にしてください:\n\n{text}"
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "あなたはプロフェッショナルなテキスト要約アシスタントです"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return text 

async def save_llm_responses(results: dict, user_message: str, room_id: int, db: AsyncSession, llm_ids: list) -> tuple:
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
    

async def save_llm_responses_with_document(results: dict, user_message: str, room_id: int, db: AsyncSession, llm_ids: list, file_content: str, combined_history: str) -> tuple:
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

                if(file_content != ""):
                    text_bytes = combined_history.encode("utf-8")
                    if len(text_bytes) > MAX_INDEX_SIZE:
                        combined_history = await summarize_text(combined_history)

                    media_entry = Media(
                        message_id=message_response.id,  
                        path="",
                        type=2, 
                        text=combined_history
                    )
                    db.add(media_entry)
                    await db.commit()
                    await db.refresh(media_entry)

        return response_messages


    except Exception as e:
        raise e