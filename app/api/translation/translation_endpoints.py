from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Response
import asyncio
import json
import logging
from app.api.services.openai.openai_service import OpenAiSession
from app.api.services.image_parser_service import parse_words_from_image

router = APIRouter(tags=["Translation"])

logger = logging.getLogger(__name__)
    
openai_session = OpenAiSession()

@router.get("/hello")
async def hello():
    return {"message": "Hello, World!"}

@router.post("/upload-picture/")
async def upload_picture(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if file.content_type != "image/jpeg":
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG images are allowed.")
    
    print(f"Received image: {file.filename}")
    try:
        # Read the image bytes
        image_bytes = await file.read()
        
        # Parse words from the image
        extracted_text = parse_words_from_image(image_bytes)
        return json.dumps({"extracted_text": extracted_text})
    except Exception as e:
        logger.error(f"Error parsing image: {e}")
        raise HTTPException(status_code=500, detail="Error parsing image")

@router.post("/send-message/")
async def translate_sent_message(request: Request):
    json_data = await request.json()

    message = json_data["message"]
    try:
        answer = await openai_session.send_message(message)

        return json.dumps({"answer": answer})
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error translating message")
    
@router.delete("/delete-history")
def delete_history():
    try:
        print("History Deleted.")
        answer = openai_session.delete_history()
        return Response(content=json.dumps({"details": "History Deleted."}), status_code=200)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error deleting history")