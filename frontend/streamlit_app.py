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
    initial_sidebar_state="collapsed"
)

# Custom CSS with beautiful colors
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.3rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stChatMessage {
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }
    
    .success-box {
        padding: 1.2rem;
        background: linear-gradient(135deg, #51CF66 0%, #3BC55B 100%);
        color: white;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(81, 207, 102, 0.3);
    }
    
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
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

if "db" not in st.session_state:
    st.session_state.db = DatabaseManager()

# Authentication state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.show_signup = False

def login_page():
    """Display login page"""
    st.markdown('<div class="main-header">🍽️ GoodFoods</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI Reservation Assistant</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.show_signup:
            # Login Form
            st.markdown("### 🔐 Login")
            
            with st.form("login_form"):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if username and password:
                        result = st.session_state.db.authenticate_user(username, password)
                        if result["success"]:
                            st.session_state.authenticated = True
                            st.session_state.user = result["user"]
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")
                    else:
                        st.warning("⚠️ Please enter both username and password")
            
            st.markdown("---")
            if st.button("📝 Create New Account", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
            
            st.markdown("---")
            st.info("💡 **Demo Account:**\n\nUsername: `demo`\n\nPassword: `demo123`")
        
        else:
            # Signup Form
            st.markdown("### 📝 Create Account")
            
            with st.form("signup_form"):
                new_username = st.text_input("Username", key="signup_username")
                new_email = st.text_input("Email", key="signup_email")
                new_password = st.text_input("Password", type="password", key="signup_password")
                confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
                full_name = st.text_input("Full Name (optional)", key="signup_fullname")
                phone = st.text_input("Phone (optional)", key="signup_phone")
                
                submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit:
                    if not new_username or not new_email or not new_password:
                        st.warning("⚠️ Please fill in all required fields")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords don't match")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        result = st.session_state.db.create_user(
                            username=new_username,
                            email=new_email,
                            password=new_password,
                            full_name=full_name,
                            phone=phone
                        )
                        if result["success"]:
                            st.success("✅ Account created! Please login.")
                            st.session_state.show_signup = False
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")
            
            st.markdown("---")
            if st.button("🔙 Back to Login", use_container_width=True):
                st.session_state.show_signup = False
                st.rerun()

# Check authentication
if not st.session_state.authenticated:
    login_page()
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("### 🍽️ GoodFoods")
    st.markdown("**AI Reservation Assistant**")
    st.markdown("---")
    
    # User info
    user = st.session_state.user
    print("user:",user)
    st.markdown(f"👤 **{user['full_name'] or user['username']}**")
    st.markdown(f"📧 {user['email']}")
    st.markdown("---")
    
    # Quick actions
    st.markdown("### 🎯 Quick Actions")
    
    if st.button("📋 View Reservations", use_container_width=True):
        prompt = "Show me my reservations"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Checking reservations..."):
            response = st.session_state.orchestrator.process_message(prompt, user['username'], user['id'])
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    if st.button("🔍 Find Restaurants", use_container_width=True):
        prompt = "I'm looking for restaurant recommendations"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Finding restaurants..."):
            response = st.session_state.orchestrator.process_message(prompt, user['username'], user['id'])
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
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.messages = []
        st.session_state.orchestrator.reset_conversation()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 💡 Try asking:")
    st.markdown("""
    - "Find me Italian restaurants"
    - "Book a table for 4 tomorrow at 7pm"
    - "Show me my reservations"
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
            # Pass both username and user_id for proper database linking
            response = st.session_state.orchestrator.process_message(
                prompt, 
                st.session_state.user['username'],
                st.session_state.user['id']
            )
            st.markdown(response)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

# Welcome message if no conversation yet
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        user_display_name = st.session_state.user['full_name'] or st.session_state.user['username']
        welcome_message = f"""
👋 Hi {user_display_name}! Welcome to GoodFoods!

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
