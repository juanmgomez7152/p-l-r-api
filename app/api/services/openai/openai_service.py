from app.api.services.openai.open_ai_conn import openai_call
from langdetect import detect
import logging

logger = logging.getLogger(__name__)
with open("app/api/translation/translation_system_message.txt") as f:
    system_message = f.read()
    
class OpenAiSession:
    def __init__(self):
        self.history = [{"role": "system", "content": system_message}]
        
    async def send_message(self, message):
        self.history.append({"role": "user", "content": message})
        try:
            language_detected = detect(message)
            if language_detected == "es":
                answer =  "El mensaje ya está en español, no es necesario traducirlo."
            else:
                answer = await openai_call(self.history)
            return answer
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "Lenguaje no detectado."
    
    def delete_history(self):
        self.history = []
        self.history = [{"role": "system", "content": system_message}]
        return "History deleted."
