from typing import List, Optional
from typing_extensions import Annotated  
from pydantic import BaseModel, Field
from fastapi import File, UploadFile

class ChatRequest(BaseModel):
    user_id: Optional[Annotated[int, Field(gt=0,lt=10**10)]]= None
    room_id: Optional[Annotated[int, Field(gt=0,lt=10**10)]]= None
    image: Optional[UploadFile] = None
    # image: Optional[str] = None
    user_message: str
    llm_ids: list