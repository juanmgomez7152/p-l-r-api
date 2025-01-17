import pytesseract
import logging
import platform
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from io import BytesIO
from typing import Optional

executor = ThreadPoolExecutor()
logger = logging.getLogger(__name__)
# Specify the Tesseract executable path based on the operating system
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def _process_image(img: Image) -> str:
    """Synchronous function to process image with pytesseract"""
    return pytesseract.image_to_string(img)

async def parse_words_from_image(image_bytes: bytes) -> Optional[str]:
    try:
        # Open the image file from bytes
        img = Image.open(BytesIO(image_bytes))
        
        # Run OCR in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(executor, _process_image, img)
        
        if not text:
            logger.warning("No text extracted from image")
            return None
            
        return text.strip()
    
    except Exception as e:
        logger.error(f"Error parsing image: {str(e)}")
        raise Exception(f"Failed to parse image: {str(e)}")