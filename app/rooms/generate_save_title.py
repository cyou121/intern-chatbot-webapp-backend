from app.messages.call_api import call_gemini_api, call_openai_api, process_llm_calls

async def generate_save_room_title(conversation: str, new_room, db) -> str:

    prompt = [
        {
            "role": "system",
            "content": (
                "Read the following conversation and generate a short, simple title that best represents the chat. "
                "The title should be in the same language as the conversation and must be strictly limited to 30 characters or fewer."
            )
        },
        {
            "role": "user",
            "content": f"Conversation:\n{conversation}"
        }
    ]

    
    title = await call_openai_api(prompt=prompt)

    new_room.title = title

    db.add(new_room)         
    await db.commit()      
    await db.refresh(new_room)
    print(title)

    return title

