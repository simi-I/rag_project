import os
import groq
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq

class chat_bot():
    
    #set GROQ_API_KEY = "your api key" in the .env file"
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    client = groq.Groq(api_key=GROQ_API_KEY)
    
    sys_prompt = """You are a helpful virtual assistant. \
                Your goal is to provide useful and relevant \
                responses to my request"""
    
    llm = ChatGroq(
        model = "llama-3.1-70b-versatile",
        temperature = 0.0,
        max_retries = 2,
    )
    
    def get_response(self, message):
        try:
            llm = ChatGroq(
                        model = "llama-3.1-70b-versatile",
                        temperature = 0.0,
                        max_retries = 2,
                    )
            messages = [
                (
                    "system",
                    "You are a helpful virtual assistant. \
                Your goal is to provide useful and relevant \
                responses to my request",
                ),
                (f"{message}"),
                
            ]
            response = llm.invoke(messages)
            
            return response
        
        except Exception as e:
            return {"error": str(e)}