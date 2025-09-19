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
with open("app/resources/countries_supported.json", "r") as f:
    countries = json.load(f)
    for language, data in countries.items():
        for lang_id, country_list in data.items():
            for country in country_list:
                country_to_languageid[country] = lang_id
                country_to_language[country] = language
    
openai_session = OpenAiSession()
image_parser = ImageParserSession()

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
        #verify is the country is supported:
        if country not in country_to_languageid:
            raise ValueError(f"Country '{country}' not supported")
        retry = json_data["retry"]
        language_id=country_to_languageid[country]
        language = country_to_language[country]
        answer = await openai_session.get_translation(retry,message,country=country,language_id=language_id,language=language)

        return json.dumps({"answer": answer})
    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
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
    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        raise HTTPException(status_code=400, detail="Language not supported")

