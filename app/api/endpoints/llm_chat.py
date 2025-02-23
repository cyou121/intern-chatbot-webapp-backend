from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from app.schemas.chat import ChatRequest
from app.services.llm_chat_processor import process_chat_request, process_chat_with_document_request
from app.services.llm_chat_processor_media import process_chat_request_image
from sqlalchemy.orm import Session
from app.models.models import Room
from datetime import datetime
from app.rooms.generate_save_title import generate_save_room_title
from app.rooms.create_room import create_room
from app.database.session import get_async_db
from app.core.llm_types import LLMType
from app.messages.media_upload import upload_to_s3
from fastapi.responses import HTMLResponse
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import oauth2_scheme, verify_access_token
from app.services.web_search_service import get_search_results
from app.services.ai_service import add_search_results_to_message
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.documents.extract_text import extract_text_from_file
from pydantic import Field

router = APIRouter()

async def is_image(image: UploadFile) -> bool:
    if image.content_type.startswith('image/'):
        return True
    return False

@router.post("/chat/response")
async def chat_endpoint(
    user_id: Optional[int] = Form(None, gt=0, lt=10**10),
    room_id: Optional[int] = Form(None, gt=0, lt=10**10),
    user_message: str = Form(...),
    llm_ids: str = Form("1,2"), 
    image: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_async_db),
    web_search_flag: bool = Form(False),
    document_history_flag: Optional[int] = Form(0),
    # access_token: str = Depends(oauth2_scheme)
    ):
    try:
        # payload = verify_access_token(access_token)
        llm_ids_list = [int(id_str) for id_str in llm_ids.split(",")]
        if room_id is None:
            if user_id is None:
                raise HTTPException(status_code=400, detail="room_idまたはuser_idのどちらかを指定してください。")

            new_room = await create_room(user_id, db)
            new_room_id = new_room.id
        else:
            new_room_id = room_id
        
        if web_search_flag:
            search_results = await get_search_results(user_message)
            user_message = await add_search_results_to_message(user_message, search_results)

        if image is not None:
            if await is_image(image):
                image_path = await upload_to_s3(image)
            else:
                raise ValueError("Uploaded file is not an image")
            if image_path is None:
                return {"error": "画像のアップロードに失敗しました"}
            response_messages= await process_chat_request_image(
                room_id=new_room_id,
                user_message=user_message,
                image=image_path,
                llm_ids=llm_ids_list,
                db=db
            )

        file_contents = []
        if file:
            extracted_text = await extract_text_from_file(1, file)
            file_contents.append(extracted_text)

        if file_contents:
            response_messages = await process_chat_with_document_request(
                room_id=new_room_id,
                user_message=user_message,
                llm_ids=llm_ids_list,
                file_content="\n".join(file_contents), 
                db=db
            )
        elif(document_history_flag == 1):
                response_messages = await process_chat_with_document_request(
                room_id=new_room_id,
                user_message=user_message,
                llm_ids=llm_ids_list,
                file_content="",
                db=db
            )
        elif(image is None):
            response_messages= await process_chat_request(
                room_id=new_room_id,
                user_message=user_message,
                llm_ids=llm_ids_list,
                db=db
            )

        if room_id is None:
            conversation = f"User: {user_message}\n"
            for msg in response_messages:
                if msg.llm_id == LLMType.OPENAI:
                    conversation += f"LLM(OpenAI): {msg.content}\n"
                elif msg.llm_id == LLMType.GEMINI:
                    conversation += f"LLM(Gemini): {msg.content}\n"
        
            await generate_save_room_title(conversation, new_room, db)

        await db.commit()

        return response_messages

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
