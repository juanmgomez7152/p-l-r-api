import logging
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from io import BytesIO
from typing import Optional
import easyocr
from cachetools import TTLCache

reader = easyocr.Reader(['en'])
executor = ThreadPoolExecutor()
logger = logging.getLogger(__name__)

class ImageParserSession:   
    cache = TTLCache(maxsize=100, ttl=300)
    def __init__(self):
        pass 
    async def parse_image_using_easyocr(self,filename:str,image_bytes: bytes) -> Optional[str]:
        if filename in self.cache:
            return self.cache[filename]
        try:
            img = Image.open(BytesIO(image_bytes))
            result = reader.readtext(image=img)
            extracted_text = ""
            for (bbox, text, prob) in result:
                # logger.info(f"Detected text: {text}, with probability: {prob}")
                extracted_text += text + " "
            self.cache[filename] = extracted_text
            
            return extracted_text
        except Exception as e:
            logger.error(f"Error parsing image using EasyOCR: {str(e)}")
            return "Problema al leer la imagen"
            # raise Exception(f"Failed to parse image using EasyOCR: {str(e)}")