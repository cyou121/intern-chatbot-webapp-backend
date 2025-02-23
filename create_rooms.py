import asyncio
from app.database.session import AsyncSessionLocal
from app.models.models import Llm

async def create_room(name: str):
    async with AsyncSessionLocal() as db:
        room = Llm(name=name)
        db.add(room)
        await db.commit()
        await db.refresh(room)
        print(f"Created room with id: {room.id}")

async def main():
    tasks = [
        create_room("ChatGPT"),
        create_room("Gemini"),
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())