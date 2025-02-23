import os
import requests
import concurrent.futures
from app.core.config import settings
from app.core.llm_types import LLMType
import asyncio
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
from app.messages.save_messages import MAX_INDEX_SIZE, summarize_text

async def call_openai_api(user_message: str = None, prompt: list = None) -> str:
    if prompt is None:
        prompt = []

    if user_message is not None:
        prompt.append({
            "role": "user",
            "content": user_message
        })

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.openai_model,
        "messages": prompt, 
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        json=payload,
        headers=headers
    )
    if response.status_code == 200:
        result = response.json()
        reply = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return reply
    else:
        return f"Error: OpenAI API returned status code {response.status_code}"


async def call_gemini_api(user_message: str = None, prompt: list = None) -> str:
    if prompt is None:
        prompt = []

    prompt.append(Content(role="user", parts=[Part.from_text(user_message)]))
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.gemini_api_key_path
    PROJECT_ID = settings.PROJECT_ID
    LOCATION = settings.LOCATION
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    MODEL_NAME = settings.GEMINI_MODEL
    model = GenerativeModel(MODEL_NAME)

    chat = model.start_chat(history=prompt)
    response = chat.send_message(user_message)
    return str(response.text)

async def process_llm_calls(user_message: str, prompts: dict, llm_ids: list) -> dict:
    results = {}

    llm_functions = {
        LLMType.OPENAI: call_openai_api,
        LLMType.GEMINI: call_gemini_api
    }

    text_bytes = user_message.encode("utf-8")
    if len(text_bytes) > MAX_INDEX_SIZE:
        user_message = await summarize_text(user_message)

    tasks = {}
    for llm_id in llm_ids:
        if llm_id in llm_functions:

            tasks[llm_id] = asyncio.create_task(
                llm_functions[llm_id](user_message, prompts.get(llm_id, []))
            )
    

    for llm_id, task in tasks.items():
        try:
            results[llm_id] = await task
        except Exception as exc:
            results[llm_id] = f"Error: {exc}"
    
    return results