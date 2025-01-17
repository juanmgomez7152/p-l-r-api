from langdetect import detect
from cachetools import TTLCache
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv()
model_name = "gpt-4o"
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")
    
class OpenAiSession:
    cache = TTLCache(maxsize=100, ttl=300)
    def __init__(self,system_message):
        self.system_message = system_message
        # self.history = [{"role": "system", "content": system_message}]
    
    def set_system_message(self, system_message):
        self.system_message = system_message
        self.cache.clear()
        # self.history = [{"role": "system", "content": system_message}]
        return "System message set."
    
    async def _openai_call(self, messages, model_name=model_name):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0
            )
    
            answer = response.choices[0].message.content
            return answer
        except Exception as e:
            logger.error("Error making connection to OpenAI: ", e)
    async def _stream_openai_call(self, messages, model_name=model_name):
        try:
            response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0,
            stream=True
            )
        
            for chunk in response:
                yield chunk.choices[0].delta.content
    
        except Exception as e:
            logger.error("Error making connection to OpenAI: ", e)
    
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
                answer = await self._openai_call(payload)
                
            self.cache[message] = answer
            return answer
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "Lenguaje no detectado."
        
    async def stream_message(self,message):
            payload = [{"role": "system", "content": self.system_message},
                        {"role": "user", "content": message}]
            try:
                return self.stream_openai_call(payload)
            except Exception as e:
                logger.error(f"STREAM: Error detecting language: {e}")
                return "Lenguaje no detectado."
            
            
    # def delete_history(self):
    #     self.history = []
    #     self.history = [{"role": "system", "content": self.system_message}]
    #     return "History deleted."
