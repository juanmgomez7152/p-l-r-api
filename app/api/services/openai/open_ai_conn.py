from openai import OpenAI
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()
model_name = "gpt-4o"
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

async def openai_call(list_of_messages, model_name=model_name):
  try:
    response = client.chat.completions.create(
      model=model_name,
      messages=list_of_messages,
      temperature=0
    )
    
    answer = response.choices[0].message.content
    
    list_of_messages.append({"role": response.choices[0].message.role, "content": answer})
    
    return answer
    
  except Exception as e:
    logger.error("Error making connection to OpenAI: ", e)
