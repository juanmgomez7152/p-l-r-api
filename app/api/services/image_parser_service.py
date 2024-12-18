import pytesseract
import logging
import platform
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from io import BytesIO

executor = ThreadPoolExecutor()
logger = logging.getLogger(__name__)
# Specify the Tesseract executable path based on the operating system
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

async def parse_words_from_image(image_bytes: bytes) -> str:
    try:
        # Open the image file from bytes
        img = Image.open(BytesIO(image_bytes))
        # Use pytesseract to do OCR on the image
        text = pytesseract.image_to_string(img)
        
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(executor, parse_words_from_image, image_bytes)
        return text
    
    except Exception as e:
        raise logger.error(f"Error parsing image: {e}")