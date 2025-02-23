from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from app.core.config import settings 
from app.database.session import get_async_db
from app.core.security import oauth2_scheme, authenticate_user, get_user_by_id, create_access_token, create_refresh_token, verify_refresh_token
from pydantic import BaseModel
import logging

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES 
ALGORITHM = settings.ALGORITHM
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter()

class TokenRefreshRequest(BaseModel):
    refresh_token: str

@router.post("/token")
async def login_for_access_token(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_async_db)
) -> dict:
    if not email or not password:
        raise HTTPException(status_code=400, detail="メールアドレスとパスワードは必須です。")
    
    user = await authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    access_token = await create_access_token({"sub": str(user.id)})
    refresh_token = await create_refresh_token({"sub": str(user.id)})

    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh")
async def refresh_access_token(request: TokenRefreshRequest) -> dict:
    try:
        payload = verify_refresh_token(request.refresh_token)
        id: str = payload.get("sub")
        if not id:
            raise HTTPException(status_code=401, detail="id isn't in token")
        if not isinstance(id, str):
            raise HTTPException(status_code=401, detail="id should be a string")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    new_access_token = await create_access_token({"sub": id})

    return {"access_token": new_access_token, "token_type": "bearer"}


# @router.get("/me")
# async def read_users_me(
#     token: str = Depends(oauth2_scheme),
#     db: AsyncSession = Depends(get_async_db)
# ) -> dict:
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         id: str = payload.get("sub")
#         if not id:
#             raise HTTPException(status_code=401, detail="id isn't in token")
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token has expired")
#     except JWTError as e:
#         logger.error(f"JWT error: {e}")
#         raise HTTPException(status_code=401, detail="Invalid token")

#     user = get_user_by_id(db, id)
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")

#     return {"email": user.email}
