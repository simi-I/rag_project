import streamlit as st
import requests, time, os, shutil, yaml
from chat_bot import *
from exceptions.operationshandler import userops_logger, llmresponse_logger, system_logger

# Load configuration from YAML file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Define backend API URLs
CHROMADB_URL = "http://127.0.0.1:5000/init_chromadb"
MODEL_URL = "http://127.0.0.1:5000/init_model"
QUERY_URL = "http://127.0.0.1:5000/process_query"

def save_uploaded_file(file_upload):
    """Saves the uploaded file to the specified directory."""
    if file_upload is not None:
        file_path = os.path.join(config["Data_upload_folder"], file_upload.name)
        with open(file_path, "wb") as f:
            f.write(file_upload.getbuffer())
        return True
    return False

# Main app title
st.title("Chat with your PDFs")

# Session state initialization for model selection and temperature
if 'model_select' not in st.session_state:
    st.session_state.model_select = ""

if 'model_temperature' not in st.session_state:
    st.session_state.model_temperature = 0.0

if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False
    
if "intialize_llm" not in st.session_state:
    st.session_state.intialize_llm = False

# Sidebar for file upload
with st.sidebar:
    saved = False
    
    # File uploader widget
    file_upload = st.file_uploader("Upload a PDF file to begin", type=['pdf'])
    
    # Button to save the file
    save_file = st.sidebar.button("Save file")
    
    if save_file and file_upload is not None:
        save = save_uploaded_file(file_upload)
        if save:
            success = st.sidebar.success("File saved successfully.")
            response = requests.post(CHROMADB_URL)
            if response.status_code ==200:
                st.session_state.file_uploaded = True
                time.sleep(2)
                success.empty()
        else:
            st.sidebar.error("Failed to save uploaded file.")
    elif save_file and file_upload is None:
        st.sidebar.error("Please upload a file first.")

# If file is uploaded, allow model and temperature selection
if st.session_state.file_uploaded:
    st.sidebar.subheader("Model and Settings")
    
    # Model selection widget
    model_select = st.sidebar.selectbox(
        "Select a Model",
        ("llama-3.1-70b-versatile", "gemini-1.5-pro-001", "mistral-large@2407", "claude-3-opus@20240229", "claude-3-5-sonnet@20240620")
    )
    if model_select:
        st.session_state.model_select = model_select
    
    # Temperature slider widget
    model_temperature = st.sidebar.slider(
        "Select Model's Temperature", 
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.1
    )
    if model_temperature:
        st.session_state.model_temperature = model_temperature

    # Initialize the model
    if st.sidebar.button("Initialize Model"):
        model_data = {
            "model": st.session_state.model_select,
            "temperature": st.session_state.model_temperature
        }
        response = requests.post(MODEL_URL, json=model_data)
        if response.status_code == 200:
            st.sidebar.success("Model initialized successfully")
            st.session_state.intialize_llm = True
        else:
            st.sidebar.error(f"Failed to initialize model: {response.text}")
             

# Chat section after file upload, model selection, and temperature setup
if st.session_state.file_uploaded and st.session_state.intialize_llm:
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you?"}]

    # Display previous chat messages
    for message in st.session_state.messages:
        st.chat_message(message['role']).write(message["content"])

    # Accept user input and display chat
    if prompt := st.chat_input("Ask a question about your document"):
        # Display user message in chat
        st.chat_message("user").write(prompt)
        # Add user message to session state (chat history)
        st.session_state.messages.append({"role": "user", "content": prompt})
        userops_logger.info(f'User query: {prompt}\n\n')

        # Get response from backend API
        bot_response = ""
        with st.spinner("Thinking..."):
            response = requests.post(QUERY_URL, json={"query": prompt})
            
            if response.status_code == 200:
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    bot_response += chunk
                st.chat_message("assistant").write(bot_response)
            else:
                st.error(f"Failed to get a response. Status Code: {response.status_code}")
                
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
else:
    st.write("Please complete the file upload and model configuration to start the chat.")
