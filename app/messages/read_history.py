from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Message, Media
from vertexai.generative_models import Content, Part
from app.core.llm_types import LLMType
from sqlalchemy.orm import joinedload
from app.messages.media_upload import generate_presigned_url
import mimetypes

VALID_TIME=900

async def create_history_prompt(db: AsyncSession, room_id: int) -> dict:

    stmt = (
        select(Message)
        .options(joinedload(Message.medias))
        .where(Message.room_id == room_id)
        .order_by(Message.created_at)
    )
    result = await db.execute(stmt)
    messages = result.unique().scalars().all()
    prompts = {
        LLMType.OPENAI: [],
        LLMType.GEMINI: []
    }
    for msg in messages:
        if msg.role:

            if msg.llm_id in prompts:
                if msg.medias:
                    image_path = generate_presigned_url(msg.medias[0].path, VALID_TIME)
                    if msg.llm_id == LLMType.OPENAI:
                        prompts[LLMType.OPENAI].append({
                            "role": "user",
                            "content": [
                                {"type": "text", "text": msg.content},
                                {"type": "image_url", "image_url": {"url": image_path}},
                            ]
                        })
                    elif msg.llm_id == LLMType.GEMINI:
                        prompts[LLMType.GEMINI].append(
                            Content(role="user", parts=[Part.from_text(msg.content)])
                        )
                        mime_type, _ = mimetypes.guess_type(image_path)
                        prompts[LLMType.GEMINI].append(Content(role="user", parts=[Part.from_uri(image_path, mime_type)]))
                else:
                    if msg.llm_id == LLMType.OPENAI:
                        prompts[LLMType.OPENAI].append({
                                "role": "user",
                                "content": msg.content
                            })
                    elif msg.llm_id == LLMType.GEMINI:
                        prompts[LLMType.GEMINI].append(
                            Content(role="user", parts=[Part.from_text(msg.content)])
                        )

        else:
            if msg.llm_id == LLMType.OPENAI:
                prompts[LLMType.OPENAI].append({
                    "role": "assistant",
                    "content": msg.content
                })
            elif msg.llm_id == LLMType.GEMINI:
                prompts[LLMType.GEMINI].append(
                    Content(role="model", parts=[Part.from_text(msg.content)])
                )
    return prompts

async def get_history_document(db: AsyncSession, room_id: int):
    stmt = (
        select(Media.text)
        .join(Message, Media.message_id == Message.id)
        .where(Message.room_id == room_id, Media.type == 2)
        .order_by(Media.id.desc())
        .limit(1)
    )

    result = await db.execute(stmt)
    latest_text = result.scalar()

    return latest_text