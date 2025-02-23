from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Llm
from sqlalchemy import select

async def get_llm_by_name(db: AsyncSession, name: str):
    stmt = select(Llm).where(Llm.name == name)
    result = await db.execute(stmt)
    return result.scalars().first()

