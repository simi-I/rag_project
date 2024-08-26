from model import chat_bot
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse
import groq
from dotenv import load_dotenv
import traceback

load_dotenv()

#intialize your Applications
app = FastAPI()
chat_bot = chat_bot()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route("/chat_batch", methods=["POST"])
async def chat_batch(request: Request):
    user_input = await request.json()
    user_message = user_input.get("message")
    
    try:
        # Generate a response
        response = chat_bot.get_response(message = user_message)
        output = response.content
        return PlainTextResponse(content=output, status_code=200)
    
    except Exception as e:
        print(traceback.format_exc())
        return {
            "error": str(e),
            "status_code": 400
        }