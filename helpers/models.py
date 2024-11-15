import os, json
from dotenv import load_dotenv

from exceptions.operationshandler import system_logger, llmresponse_logger, userops_logger
from llama_index.llms.groq import Groq
from pydantic import BaseModel

from llama_index.llms.vertex import Vertex
from google.oauth2 import service_account
from google.auth.transport.requests import Request  # type: ignore[import-untyped]
from llama_index.llms.mistralai import MistralAI
from anthropic import AnthropicVertex
# from llama_index.llms.anthropic import Anthropic

#from mistralai_gcp import MistralGCP

from utils.anthropic_base import Anthropic

class LLMCLient(BaseModel):
    
    #set GROQ_API_KEY = "your api key" in the .env file"
    GROQ_API_KEY: str = ""
    secrets_path: str = ""
    temperature: float = 0.1
    max_output_tokens: int = 512
    
    def load_credentials(self):
        with open(self.secrets_path, "r") as file:
            secrets = json.load(file)
        
        credentials = service_account.Credentials.from_service_account_info(
            secrets,
            scopes = ['https://www.googleapis.com/auth/cloud-platform']
        )
        
        return credentials
    
    def refresh_auth(self, credentials) -> None:
        """This is part of a workaround to resolve issues with authentication scopes for AnthropicVertex"""
        credentials.refresh(Request())

        return credentials
    
    def generate_access_token(self, credentials) -> str:
        """This is part of a workaround to resolve issues with authentication scopes for AnthropicVertex"""
        
        _credentials = self.refresh_auth(credentials)
        access_token = _credentials.token
        if not access_token:
            raise RuntimeError("Could not resolve API token from the environment")

        assert isinstance(access_token, str)
        return access_token
    
    def get_groq(self, model):
        return Groq(
            model,
            temperature = self.temperature,
            max_tokens = self.max_output_tokens
        )
        
    
    def get_gemini(self, model):
        credentials = self.load_credentials()
        llm = Vertex(model, temperature=self.temperature, max_tokens=self.max_output_tokens, project= credentials.project_id, 
                     credentials=credentials)
        
        return llm
    
    
    # def get_mistral(self, model):
    #     vertexclient = MistralGCP()
        
    #     llm = MistralAI(model="mistral-large@2407")
        
        
    def get_anthropic(self, model):
        credentials = self.load_credentials()
        access_token = self.generate_access_token(credentials)
        
        region_mapping = {
            "claude-3-opus@20240229" : "us-east5",
            "claude-3-5-sonnet@20240620" : "us-east5"
        }
        
        vertex_client = AnthropicVertex(
            access_token=access_token,
            project_id=credentials.project_id,
            region=region_mapping.get(model)
            
        )
        
        return Anthropic(
            model = model,
            vertex_client = vertex_client,
            temperature=self.temperature, 
            max_tokens=self.max_output_tokens
        )
        
    def map_client_to_model(self, model):
        
        model_mapping = {
            "llama-3.1-70b-versatile": self.get_groq,
            "gemini-1.5-pro-001": self.get_gemini, 
            #"mistral-large@2407": self.get_mistral,
            "claude-3-opus@20240229": self.get_anthropic,
            "claude-3-5-sonnet@20240620": self.get_anthropic,
        }
        
        _client = model_mapping.get(model)
        
        return _client(model)