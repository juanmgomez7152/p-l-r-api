from app.api.services.openai.open_ai_conn import openai_call
from langdetect import detect
from cachetools import TTLCache
import logging

logger = logging.getLogger(__name__)

# with open("app/api/translation/translation_system_message.txt") as f:
#     system_message = f.read()
    
class OpenAiSession:
    cache = TTLCache(maxsize=100, ttl=300)
    def __init__(self,system_message):
        self.system_message = system_message
        # self.history = [{"role": "system", "content": system_message}]
    
    def set_system_message(self, system_message):
        self.system_message = system_message
        # self.history = [{"role": "system", "content": system_message}]
        return "System message set."
    
    async def send_message(self, message):
        if message in self.cache:
            return self.cache[message]
        payload = [{"role": "system", "content": self.system_message},
                    {"role": "user", "content": message}]
        
        try:
            language_detected = detect(message)
            if language_detected == "es":
                answer =  "El mensaje ya está en español, no es necesario traducirlo."
            else:
                answer = await openai_call(payload)
                
            self.cache[message] = answer
            return answer
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "Lenguaje no detectado."
    
    # def delete_history(self):
    #     self.history = []
    #     self.history = [{"role": "system", "content": self.system_message}]
    #     return "History deleted."
