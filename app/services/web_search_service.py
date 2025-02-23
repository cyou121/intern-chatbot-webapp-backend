from time import sleep
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from app.database.session import get_async_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

GOOGLE_API_KEY = "AIzaSyDZAsidFyPsUZ5V1qxhrzabhsMoWbVRWek"
CUSTOM_SEARCH_ENGINE_ID = "a7a29b973e5a24174"

async def get_search_results(keyword:str):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    search_results = []
    try:
        await asyncio.sleep(1)
        result = service.cse().list(
            q=keyword,
            cx=CUSTOM_SEARCH_ENGINE_ID,
            lr='lang_ja',
            num=10
        ).execute()
        
        if "items" in result:
            for item in result["items"]:
                search_results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
    except Exception as e:
        print(f"Error: {e}")
    
    return search_results

