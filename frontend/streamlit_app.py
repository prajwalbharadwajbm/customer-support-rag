import streamlit as st
import requests
import json
import time
import os
from typing import List, Dict

# Page configuration
st.set_page_config(
    page_title="Customer Support RAG",
    page_icon="🤖",
    layout="wide"
)

# App configuration - Use environment variable for backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
CHAT_ENDPOINT = f"{BACKEND_URL}/chat/stream"

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "followup_questions" not in st.session_state:
        st.session_state.followup_questions = []

def send_message_to_backend(messages: List[Dict]) -> str:
    """Send message to FastAPI backend and get streaming response"""
    try:
        # Prepare the payload according to your ChatInput model
        payload = {
            "messages": messages
        }
        
        # Make streaming request
        response = requests.post(
            CHAT_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True
        )
        
        if response.status_code == 200:
            full_response = ""
            followup_questions = []
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            if 'content' in data:
                                full_response += data['content']
                            if 'followup_questions' in data:
                                followup_questions.extend(data['followup_questions'])
                        except json.JSONDecodeError:
                            continue
            
            # Store followup questions in session state
            st.session_state.followup_questions = followup_questions
            return full_response
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ **Connection Error**: Could not connect to the backend. Please ensure your FastAPI server is running on http://localhost:8000"
    except Exception as e:
        return f"❌ **Error**: {str(e)}"

def display_chat_message(role: str, content: str):
    """Display a chat message with appropriate styling"""
    if role == "user":
        with st.chat_message("user"):
            st.write(content)
    else:
        with st.chat_message("assistant"):
            st.write(content)

def main():
    st.title("🤖 Customer Support RAG Assistant")
    st.markdown("Ask questions about your documents and get AI-powered responses!")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ Information")
        st.markdown("""
        **How to use:**
        1. Make sure your FastAPI backend is running
        2. Type your question in the chat input
        3. Get AI-powered responses from your documents
        
        **Backend Status:**
        """)
        
        # Check backend status
        try:
            response = requests.get(f"{BACKEND_URL}/docs", timeout=2)
            if response.status_code == 200:
                st.success("✅ Backend Connected")
            else:
                st.error("❌ Backend Error")
        except:
            st.error("❌ Backend Offline")
    
    # Display chat history
    for message in st.session_state.messages:
        display_chat_message(message["role"], message["content"])
    
    # Display followup questions if any
    if st.session_state.followup_questions:
        st.markdown("### 💡 Suggested Follow-up Questions:")
        cols = st.columns(min(len(st.session_state.followup_questions), 3))
        for i, question in enumerate(st.session_state.followup_questions):
            with cols[i % 3]:
                if st.button(question, key=f"followup_{i}"):
                    # Add the followup question as user message
                    user_message = {"role": "user", "content": question}
                    st.session_state.messages.append(user_message)
                    
                    # Get response from backend
                    with st.spinner("Getting response..."):
                        response = send_message_to_backend(st.session_state.messages)
                    
                    # Add assistant response
                    assistant_message = {"role": "assistant", "content": response}
                    st.session_state.messages.append(assistant_message)
                    
                    # Clear followup questions
                    st.session_state.followup_questions = []
                    st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        display_chat_message("user", prompt)
        
        # Get response from backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message_to_backend(st.session_state.messages)
            st.write(response)
        
        # Add assistant response to chat
        assistant_message = {"role": "assistant", "content": response}
        st.session_state.messages.append(assistant_message)
        
        # Rerun to update the interface
        st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", type="secondary"):
        st.session_state.messages = []
        st.session_state.followup_questions = []
        st.rerun()

if __name__ == "__main__":
    main() 