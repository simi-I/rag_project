import os
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.node_parser import TokenTextSplitter
from exceptions.operationshandler import system_logger, llmresponse_logger, userops_logger
from helpers.models import LLMCLient

# Load environment variables
load_dotenv()

class ChatBot(BaseModel):
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY")
    secrets_path: str = os.environ.get("secrets_path")
    
    SYSTEM_PROMPT: str = """
    You are an AI assistant designed to support users by providing answers based on the content of a provided PDF document.
    
    The PDF contains various details relevant to the user's needs. Use this information to answer questions clearly and concisely.
    If a question extends beyond the PDF’s content or requires subjective judgment, inform the user accordingly.
    
    Ensure all responses are directly relevant to the PDF’s content and maintain a conversational tone to foster an engaging and helpful experience.
    Below is the context from the pdf:
    {context}
    Based on the provided details, please respond to the following query:
    
    Question: {query_str}
    """
    
    chroma_index : None = None   # Variable to store the initialized ChromaDB index
    llm: None = None  # Variable to store the initialized LLM
    chat_engine: None = None
    memory: None = None
    

    def init_llm(self, model: str, temperature: float):
        """Initialize the LLM with the given model and temperature."""
        llm_client = LLMCLient(GROQ_API_KEY=self.GROQ_API_KEY, secrets_path=self.secrets_path, temperature=temperature)
        Settings.llm = llm_client.map_client_to_model(model)
        self.llm = Settings.llm
         
        self.memory = ChatMemoryBuffer.from_defaults(token_limit=3900)
        self.chat_engine = self.chroma_index.as_chat_engine(
            chat_mode="context",
            system_prompt=self.SYSTEM_PROMPT,
            similarity_top_k=3,
            verbose=False,
            memory=self.memory
        )
        
        system_logger.info(f"Initialized model: {model} with temperature {temperature}")
        
        
    
    def init_chromadb(self):
        """Initialize the ChromaDB and load documents."""
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
        documents = SimpleDirectoryReader("data").load_data()
        
        db = chromadb.PersistentClient(path="chroma_db")
        chroma_collection = db.get_or_create_collection("quickstart")
        chroma_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        storage_context = StorageContext.from_defaults(vector_store=chroma_store)
        Settings.text_splitter = TokenTextSplitter(chunk_size=1024, chunk_overlap=20)
        
        self.chroma_index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context, embed_model=embed_model
        )
        
        system_logger.info("ChromaDB and index created.")
    
    
    def process_query(self, query: str):
        """Process a query using the initialized ChromaDB and LLM."""
        if not self.llm:
            raise HTTPException(status_code=400, detail="Model not initialized.")
        
        if not self.chroma_index:
            raise HTTPException(status_code=400, detail="ChromaDB not initialized.")
        
    
        llm_response = self.chat_engine.chat(query)
        response = llm_response.response
        
        llmresponse_logger.info(f"Query: {query} \n Response: {str(response)}\n")
        return response