from fastapi import APIRouter, HTTPException, Request, Response
import asyncio
import json
import logging
from app.api.openai.openai_session import OpenAiSession

router = APIRouter(tags=["Translation"])

logger = logging.getLogger(__name__)
    
openai_session = OpenAiSession()

@router.get("/hello")
async def hello():
    return {"message": "Hello, World!"}

@router.post("/send-message/")
async def translate_sent_message(request: Request):
    
    json_data = await request.json()
    message = json_data["message"]
    print(f"User message: {message}")
    try:
        answer = await openai_session.send_message(message)
        print(f"OpenAI response: {answer}")
        Response(content=json.dumps({"details": "User Message received and translated."}), status_code=200)
        
        # return json.dumps({"answer": answer})
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error translating message")

@router.delete("/delete-history")
def delete_history():
    answer = openai_session.delete_history()
    return {"message": answer}