from app.api.services.openai.open_ai_conn import openai_call
import asyncio

def test_session():
    system_message = "You are to help me with any task I ask you to do. You are to be factual and provide information and recommendations I also did not account for."
    
    history = [{"role": "system", "content": system_message}]
    
    bool = True
    
    while bool:
        user_message = input("User Message: ")
        if user_message == "n":
            bool = False
            break
        elif user_message == "trash":
            history = [{"role": "system", "content": system_message}]
            continue
        history.append({"role": "user", "content": user_message})
        answer = asyncio.run(openai_call(history,"gpt-4o"))
        print(f"AI Answer: {answer}\n")
        
test_session()