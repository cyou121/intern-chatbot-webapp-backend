from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings 
from app.database.session import get_async_db
from app.core.security import hash_password
from pydantic import BaseModel
from app.models.models import User


router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str

@router.post("/")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    try:
        hashed_password = hash_password(user.password)
        db_user = User(email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return {"id": db_user.id, "created_at": db_user.created_at}
    
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred during database operation"
        )   
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An unexpected error occurred during user registration: {str(e)}"
        )