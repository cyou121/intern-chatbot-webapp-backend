import requests
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Message 
from app.core.config import settings
from app.messages.save_messages_media import save_llm_responses
from app.messages.call_api_media import call_gemini_api, call_openai_api, process_llm_calls
from app.messages.read_history import create_history_prompt
from app.messages.media_upload import generate_presigned_url

VALID_TIME=900
    
async def process_chat_request_image(room_id: int, user_message: str, image: str, llm_ids: list, db: AsyncSession):

    prompts = await create_history_prompt(db, room_id)
    results = await process_llm_calls(user_message, prompts, llm_ids, generate_presigned_url(image))
    response_messages = await save_llm_responses(results, user_message, room_id, db, llm_ids, image)

    
    return response_messages
