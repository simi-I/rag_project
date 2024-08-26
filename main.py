import streamlit as st
import requests
from model import *

chat_bot = chat_bot()

# Initialize session state for tracking user input and responses
if 'responses' not in st.session_state:
    st.session_state.responses = []
    
#Define backend API Url   
backend_url = "http://127.0.0.1:5000/chat_batch"

def handle_message(user_input):
    if user_input:
        #Add the user input to the session state
        st.session_state.responses.append({'user': user_input, 'bot': None})
        
        # Empty container to update the bot's response in real-time 
        response_container = st.empty()
        
        # Send the user input to the backend API
        response = requests.post(backend_url, json= {"message": user_input}, stream=True)
        
        if response.status_code == 200:
            
            bot_response = ""
            
            # collect the batch response
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                bot_response += chunk
                
            #Display the bot's response with adaptable height
            st.markdown(f"""
            <div style="background-color:#f0f0f0; color:#000000; padding: 10px; border-radius:5px;">
                <p style="font-family:Arial,sans-serif;"> {bot_response.strip()}</p>
            </div>
            """, unsafe_allow_html=True) 
            
        else: 
            response_container.markdown("<p style='color:red;'>Error: Unable to get a response from the server.</p>", unsafe_allow_html=True)
            
        #clear the input box for the next question
        st.session_state.current_input = ""
        
# Input text box for user input
if 'current_input' not in st.session_state:
    st.session_state.current_input = ""

user_input = st.text_input("Human:", st.session_state.current_input)

if st.button("Send"):
    handle_message(user_input)
