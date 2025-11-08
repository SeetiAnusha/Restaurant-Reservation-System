"""
Streamlit Frontend
Main chat interface for the restaurant reservation agent
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from agent.orchestrator import AgentOrchestrator
from data.db_manager import DatabaseManager

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="GoodFoods Reservation Assistant",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "orchestrator" not in st.session_state:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found in environment variables. Please set it in .env file.")
        st.stop()
    
    model_name = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
    st.session_state.orchestrator = AgentOrchestrator(api_key, model_name)

if "user_name" not in st.session_state:
    st.session_state.user_name = "Guest"

if "db" not in st.session_state:
    st.session_state.db = DatabaseManager()

# Sidebar
with st.sidebar:
    st.markdown("### 🍽️ GoodFoods")
    st.markdown("**AI Reservation Assistant**")
    st.markdown("---")
    
    # User name input
    user_name = st.text_input("Your Name", value=st.session_state.user_name, key="user_name_input")
    if user_name != st.session_state.user_name:
        st.session_state.user_name = user_name
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### 🎯 Quick Actions")
    
    if st.button("📋 View My Reservations", use_container_width=True):
        prompt = "Show me my reservations"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Checking reservations..."):
            response = st.session_state.orchestrator.process_message(prompt, st.session_state.user_name)
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    if st.button("🔍 Find Restaurants", use_container_width=True):
        prompt = "I'm looking for restaurant recommendations"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Finding restaurants..."):
            response = st.session_state.orchestrator.process_message(prompt, st.session_state.user_name)
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    if st.button("📊 View Analytics", use_container_width=True):
        analytics = st.session_state.db.get_analytics()
        st.markdown("### 📈 Booking Analytics")
        st.metric("Total Reservations", analytics["total_reservations"])
        
        if analytics["popular_cuisines"]:
            st.markdown("**Popular Cuisines:**")
            for cuisine in analytics["popular_cuisines"][:3]:
                st.write(f"• {cuisine['cuisine']}: {cuisine['count']} bookings")
    
    st.markdown("---")
    
    # Reset conversation
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.orchestrator.reset_conversation()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 💡 Try asking:")
    st.markdown("""
    - "Find me Italian restaurants"
    - "Book a table for 4 tomorrow at 7pm"
    - "Show me my reservations"
    - "Cancel my booking"
    - "Recommend romantic restaurants"
    """)

# Main content
st.markdown('<div class="main-header">🍽️ GoodFoods Reservation Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your AI-powered dining concierge</div>', unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about reservations..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.orchestrator.process_message(prompt, st.session_state.user_name)
            st.markdown(response)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

# Welcome message if no conversation yet
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        welcome_message = f"""
👋 Hi {st.session_state.user_name}! Welcome to GoodFoods!

I'm your AI reservation assistant. I can help you:
- 🔍 Find the perfect restaurant
- 📅 Book reservations
- 📋 Manage your bookings
- 💡 Get personalized recommendations

What would you like to do today?
        """
        st.markdown(welcome_message)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
    'Powered by Llama 3.3 via Groq | Built for GoodFoods Restaurant Chain'
    '</div>',
    unsafe_allow_html=True
)
