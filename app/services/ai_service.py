import httpx
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Message  
from app.database.curd import get_llm_by_name 
from app.core.config import settings

OPENAI_CHAT_API = "https://api.openai.com/v1/chat/completions"
GEMINI_CHAT_API = "https://api.gemini.com/v1/generate"

async def call_openai_api(user_message: str) -> str:
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 50,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            OPENAI_CHAT_API,
            json=data,
            headers=headers
        )

    if response.status_code == 200:
        result = response.json()
        reply = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return reply
    else:
        return f"Error: OpenAI API returned status code {response.status_code}"

async def call_gemini_api(user_message: str) -> str:
    headers = {
        "Authorization": f"Bearer {settings.gemini_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "prompt": user_message,
        "max_tokens": 50,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GEMINI_CHAT_API,
            json=data,
            headers=headers
        )

    if response.status_code == 200:
        result = response.json()
        reply = result.get("reply", "").strip()
        return reply
    else:
        return f"Error: Gemini API returned status code {response.status_code}"

async def process_chat_request(room_id: int, user_message: str, db: AsyncSession):
    try:
        async with db.begin():
            openai_reply = await call_openai_api(user_message)

            openai_llm = await get_llm_by_name(db, "Open_AI")

            message_openai = Message(
                room_id=room_id,
                role=False,
                llm_id=openai_llm.id if openai_llm else None,
                content=openai_reply,
                created_at=datetime.now(),
                web_search_flag=False
            )

            db.add(message_openai)

        await db.refresh(message_openai)

        return openai_reply, "gemini_reply"
    
    except Exception as e:
        await db.rollback()
        raise e

async def add_search_results_to_message(user_message: str, search_results: list[dict]) -> str:
    formatted_results = [
        f"■ {result['title']}\n{result['snippet']}"
        for result in search_results
    ]
    search_results_texts = "\n\n".join(formatted_results)
    return user_message +"\n\n 以下はweb検索の結果です。\n\n" + search_results_texts
