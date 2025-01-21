from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Response
from fastapi.responses import StreamingResponse
import asyncio
import json
import logging
from app.api.services.openai.openai_service import OpenAiSession
from app.api.services.image_parser.image_parser_service import ImageParserSession

router = APIRouter(tags=["Translation"])

logger = logging.getLogger(__name__)
    
with open("app/api/translation/translation_system_message.txt") as f:
    origin_system_message = f.read()    
with open("app/resources/list of latin american countries.txt", "r") as f:
    languages = f.read().splitlines()
openai_session = OpenAiSession(origin_system_message.replace("{Hispanic_Country}", "Mexico"))
image_parser = ImageParserSession()
@router.get("/hello")
async def hello():
    return {"message": "Hello, World!"}

@router.get("/languages")
async def get_languages():
    try:
        system_message = origin_system_message.replace("{Hispanic_Country}", "Mexico")
        openai_session.set_system_message(system_message)
        return json.dumps({"languages": languages})
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error getting languages")

@router.post("/set-language/")
async def set_language(request: Request):
    json_data = await request.json()
    language = json_data["language"]
    try:
        if language not in languages:
            raise HTTPException(status_code=400, detail="Language not supported")
        
        system_message = origin_system_message.replace("{Hispanic_Country}", language)
        logger.info(f"Language set to {language}")
        openai_session.set_system_message(system_message)
        return json.dumps({"details": f"Language set to {language}"})
    except Exception as e:
        logger.error(f"Error setting the language, language will be set to MX Sp: {e}")
        system_message = origin_system_message.replace("{Hispanic_Country}", "Mexico")
        openai_session.set_system_message(system_message)
        raise HTTPException(status_code=500, detail="Error setting language")

@router.post("/upload-picture/")
async def upload_picture(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    logger.info(f"Processing image '{file.filename}'...")
    try:
        # Read the image bytes
        image_bytes = await file.read()
        
        extracted_text=await image_parser.parse_image_using_easyocr(file.filename,image_bytes)
        return json.dumps({"extracted_text": extracted_text})
    except Exception as e:
        logger.error(f"Error parsing image: {e}")
        raise HTTPException(status_code=500, detail="Error parsing image")

@router.post("/send-message/")
async def translate_sent_message(request: Request):
    json_data = await request.json()

    message = json_data["message"]
    try:
        # answer,audio_response = await openai_session.send_message(message)
        answer = await openai_session.send_message(message)

        # return json.dumps({"answer": answer,
        #                    "audio_response": audio_response})
        return json.dumps({"answer": answer})
    except Exception as e:
        logger.error(f"Error sending the response: {e}")
        raise HTTPException(status_code=500, detail="Error translating message")
    
@router.post("/stream-message/")
async def stream_translation(request:Request):
    json_data = await request.json()
    logger.info(f"Streaming message: {json_data}")
    message = json_data["message"]
    
    try:
        async def event_stream(message):
            async for chunk in await openai_session.stream_message(message):
                if chunk:
                    # logger.info(f"Chunk: {chunk}")
                    yield chunk

        return StreamingResponse(event_stream(message), media_type="text/event-stream",headers={"Cache-Control": "no-cache","Connection": "keep-alive"})
    except Exception as e:
        logger.error(f"Error Streaming the Response: {e}")
        raise HTTPException(status_code=500, detail="Error translating message")
    
    
# @router.delete("/delete-history")
# async def delete_history():
#     try:
#         logger.info("History Deleted.")
#         openai_session.delete_history()
#         return Response(content=json.dumps({"details": "History Deleted."}), status_code=200)
#     except Exception as e:
#         logger.error(f"Error: {e}")
#         raise HTTPException(status_code=500, detail="Error deleting history")