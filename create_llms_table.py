import asyncio
from app.database.session import AsyncSessionLocal
from app.models.models import Llm

async def insert_object_to_llm_table(name: str):
    async with AsyncSessionLocal() as db:
        room = Llm(name=name)
        db.add(room)
        await db.commit()
        await db.refresh(room)
        print(f"Created room with id: {room.id}")

async def add_gpt_and_gemini_to_llm_table():
    tasks = [
        insert_object_to_llm_table("ChatGPT"),
        insert_object_to_llm_table("Gemini"),
    ]
    await asyncio.gather(*tasks)

asyncio.run(add_gpt_and_gemini_to_llm_table())
