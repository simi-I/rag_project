from chat_bot import ChatBot
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse
from dotenv import load_dotenv
import traceback
from exceptions.operationshandler import system_logger
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from exceptions.operationshandler import userops_logger

load_dotenv()

#intialize your Applications
app = FastAPI()

# Intialize a global chatbot instance
chat_bot = ChatBot()

class ModelInitRequest(BaseModel):
    model:str
    temperature:float
    
class QueryRequest(BaseModel):
    query: str

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["https://*.streamlit.app", "http://localhost:8502"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers=['*'],
)

@app.post("/init_chromadb/")
async def init_chromadb_endpoint():
    try:
        chat_bot.init_chromadb()
        return{"message": "ChromaDb initialized successfully."}
        
    except Exception as e:
        system_logger.error(e)
        print(traceback.format_exc())
        return{
            "error": str(e),
            "status_code": 400
        }

@app.post("/init_model/")
async def init_model(model_init_request: ModelInitRequest):
    """Endpoint to initialzie the LLM with a selected Model and temperature."""
    try:
        chat_bot.init_llm(model_init_request.model, model_init_request.temperature)
        return{"message":f"Model {model_init_request.model} initialized successfully with temperature {model_init_request.temperature}"}
    except Exception as e:
        system_logger.error("An error occured when initializing the LLM %s", str(e), exc_info=1)
        print(traceback.format_exc())
        return {
            "error": str(e),
            "status_code": 400
        }

            

@app.post("/process_query/")
async def process_query(query_request: QueryRequest):
    """Endpoint to process a query using the initialized ChromaDB and LLM."""
    
    userops_logger.info(
        f"""
        User Request: 
        -----log prompt-----
        User data: {query_request.query}
        """
    )
    
    try:
        # Generate a response
        response = chat_bot.process_query(query_request.query)
        output = response
        return PlainTextResponse(content=output, status_code=200)
    
    except Exception as e:
        system_logger.error(e)
        print(traceback.format_exc())
        return {
            "error": str(e),
            "status_code": 400
        }
        

if __name__ == "__main__":
    import uvicorn
    
    print("Starting LLM API")
    uvicorn.run("app:app", host="0.0.0.0", port=8505, reload=True)