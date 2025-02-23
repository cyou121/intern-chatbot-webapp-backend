import os
import requests
import concurrent.futures
from app.core.config import settings
from app.core.llm_types import LLMType
import asyncio
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
import mimetypes

OPENAI_API_ENDPOINT = "https://api.openai.com/v1/chat/completions"

async def call_openai_api(user_message: str = None, image: str = None, prompt: list = None) -> str:
    if prompt is None:
        prompt = []

    if user_message is not None:
        prompt.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_message},
                {"type": "image_url", "image_url": {"url": image}},
            ]
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
        OPENAI_API_ENDPOINT,
        json=payload,
        headers=headers
    )
    if response.status_code == 200:
        result = response.json()
        reply = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return reply
    else:
        return f"Error: OpenAI API returned status code {response.status_code}"


async def call_gemini_api(user_message: str = None, image: str = None, prompt: list = None) -> str:
    if prompt is None:
        prompt = []

    prompt.append(Content(role="user", parts=[Part.from_text(user_message)]))
    mime_type, _ = mimetypes.guess_type(image)
    prompt.append(Content(role="user", parts=[Part.from_uri(image, mime_type)]))
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.gemini_api_key_path
    PROJECT_ID = settings.PROJECT_ID
    LOCATION = settings.LOCATION
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    MODEL_NAME = settings.GEMINI_MODEL
    model = GenerativeModel(MODEL_NAME)

    chat = model.start_chat(history=prompt)
    response = chat.send_message(user_message)
    return str(response.text)

async def process_llm_calls(user_message: str, prompts: dict, llm_ids: list, image: str) -> dict:
    results = {}

    llm_functions = {
        LLMType.OPENAI: call_openai_api,
        LLMType.GEMINI: call_gemini_api
    }

    tasks = {}
    for llm_id in llm_ids:
        if llm_id in llm_functions:

            tasks[llm_id] = asyncio.create_task(
                llm_functions[llm_id](user_message, image, prompts.get(llm_id, []))
            )
    

    for llm_id, task in tasks.items():
        try:
            results[llm_id] = await task
        except Exception as exc:
            results[llm_id] = f"Error: {exc}"
    
    return results