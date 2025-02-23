import requests
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Message 
from app.core.config import settings
from app.messages.save_messages import save_llm_responses, save_llm_responses_with_document
from app.messages.call_api import call_gemini_api, call_openai_api, process_llm_calls
from app.messages.read_history import create_history_prompt, get_history_document

async def process_chat_request(room_id: int, user_message: str, llm_ids: list, db: AsyncSession):
    prompts = await create_history_prompt(db, room_id)
    results = await process_llm_calls(user_message, prompts, llm_ids)
    response_messages = await save_llm_responses(results, user_message, room_id, db, llm_ids)
    
    return response_messages

async def process_chat_with_document_request(room_id: int, user_message: str, llm_ids: list, db: AsyncSession, file_content: str = ""):
    prompts = await create_history_prompt(db, room_id)
    documents_history = await get_history_document(db, room_id)
    
    file_prompt = ""
    if(documents_history != None):
        file_prompt = file_content + f"\n\n以下は、ユーザーが以前にアップロードしたファイルの内容です:\n{documents_history}"
    else:
        documents_history = ""
        file_prompt = file_content
    combined_input = f"以下は、ユーザーがアップロードしたドキュメントの内容です:\n{file_prompt}...\n\nユーザー問題: {user_message}"

    results = await process_llm_calls(combined_input, prompts, llm_ids)
    
    combined_history = file_content + "これは以前のファイルの内容：\n" + documents_history
    response_messages = await save_llm_responses_with_document(results, user_message, room_id, db, llm_ids, file_content, combined_history)

    return response_messages