from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Response
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

@router.post("/turn-text-to-speech/")
async def turn_text_to_speech(request: Request):
    logger.info("Turning text to speech...")
    json_data = await request.json()
    
    try:
        message = json_data["message"]
        country = json_data["language"]
        mp3 = await openai_session._openai_audio_call(message,country)
        
        # Get the binary content from the OpenAI response
        audio_content = mp3.content
        
        # Return a Response object with the proper headers
        return Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )
    except Exception as e:
        logger.error(f"Error turning text to speech: {e}")
        raise HTTPException(status_code=500, detail="Error turning text to speech")

