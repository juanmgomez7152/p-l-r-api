from PIL import Image
import pytesseract
from io import BytesIO
import logging

logger = logging.getLogger(__name__)
# Specify the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def parse_words_from_image(image_bytes: bytes) -> str:
    """
    Parses words from a .jpg image file.

    Args:
        image_bytes (bytes): The bytes of the .jpg image file.

    Returns:
        str: The extracted text from the image.
    """
    try:
        # Open the image file from bytes
        img = Image.open(BytesIO(image_bytes))
        
        # Use pytesseract to do OCR on the image
        text = pytesseract.image_to_string(img)
        
        return text
    except Exception as e:
        raise logger.error(f"Error parsing image: {e}")