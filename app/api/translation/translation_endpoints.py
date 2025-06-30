from fastapi import APIRouter, HTTPException, Request, UploadFile, File
import json
import logging
from typing import Dict
from app.api.services.openai.openai_service import OpenAiSession
from app.api.services.image_parser.image_parser_service import ImageParserSession

router = APIRouter(tags=["Translation"])

logger = logging.getLogger(__name__)
country_to_languageid:  Dict[str, str] ={}
country_to_language: Dict[str, str] ={}
with open("app/api/translation/translation_system_message.txt") as f:
    origin_system_message = f.read()    
with open("app/resources/list of latin american countries.txt", "r") as f:
    languages = f.read().splitlines()
    for i in range(len(languages)):
        country = languages[i].strip().split(" ")[0]
        country = country.replace("_", " ")
        language_id = languages[i].strip().split(" ")[1]
        language = languages[i].strip().split(" ")[2]
        # Languages - used for the dropdown in the frontend
        languages[i] = country
        languages[i] = (country, language)
        # Mapping country to language id for the language_detect comparision
        country_to_languageid[country] = language_id
        # Mapping country to language for the system message
        country_to_language[country] = language
    
openai_session = OpenAiSession()
image_parser = ImageParserSession()

@router.get("/languages")
async def get_languages():
    logger.info("Getting languages...")
    try:
        return json.dumps({"languages": languages})
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error getting languages")

@router.post("/upload-picture/")
async def upload_picture(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    logger.info(f"Processing image '{file.filename}'...")
    try:
        # Read the image bytes
        image_bytes = await file.read()
        
        extracted_text=await image_parser.parse_image(file.filename,image_bytes)
        return json.dumps({"extracted_text": extracted_text})

    except Exception as e:
        logger.error(f"Error parsing image: {e}")
        raise HTTPException(status_code=500, detail="Error parsing image")

@router.post("/send-message/")
async def translate_sent_message(request: Request):
    logger.info("Translating message...")
    json_data = await request.json()
    
    try:
        message = json_data["message"]
        country = json_data["language"]
        retry = json_data["retry"]
        language_id=country_to_languageid[country]
        language = country_to_language[country]
        answer = await openai_session.get_translation(retry,message,country=country,language_id=language_id,language=language)

        return json.dumps({"answer": answer})
    except Exception as e:
        logger.error(f"Error sending the response: {e}")
        raise HTTPException(status_code=500, detail="Error translating message")
    
# @router.post("/stream-message/")
# async def stream_translation(request:Request):
#     json_data = await request.json()
#     logger.info(f"Streaming message: {json_data}")
#     message = json_data["message"]
    
#     try:
#         async def event_stream(message):
#             async for chunk in await openai_session.stream_message(message):
#                 if chunk:
#                     # logger.info(f"Chunk: {chunk}")
#                     yield chunk

#         return StreamingResponse(event_stream(message), media_type="text/event-stream",headers={"Cache-Control": "no-cache","Connection": "keep-alive"})
#     except Exception as e:
#         logger.error(f"Error Streaming the Response: {e}")
#         raise HTTPException(status_code=500, detail="Error translating message")