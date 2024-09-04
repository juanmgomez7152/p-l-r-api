from openai import OpenAI
import os
import tiktoken
import asyncio
from dotenv import load_dotenv


load_dotenv()
model_name = "gpt-4-turbo"
# system_message = "You are a helpful assistant"
# client.api_key = os.getenv("OPENAI_API_KEY")
# openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

async def openai_call(list_of_messages):
  try:
    response = client.chat.completions.create(
      model=model_name,
      messages=list_of_messages,
      temperature=0.5
    )
    
    answer = response.choices[0].message.content
    
    list_of_messages.append({"role": response.choices[0].message.role, "content": answer})
    
    return answer
    
  except Exception as e:
    print("Error making connection to OpenAI: ", e)
