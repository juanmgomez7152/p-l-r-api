from app.api.openai.open_ai_conn import openai_call
import logging

logger = logging.getLogger(__name__)
with open("app/api/translation/translation_system_message.txt") as f:
    system_message = f.read()
class OpenAiSession:
    def __init__(self):
        self.history = [{"role": "system", "content": system_message}]
        
    async def send_message(self, message):
        
        self.history.append({"role": "user", "content": message})
        
        answer = await openai_call(self.history)
        
        return answer
    
    def delete_history(self):
        self.history = []
        return "History deleted."
