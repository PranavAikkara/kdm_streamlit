import streamlit as st
import uuid
from main import call_agent

# Page configuration
st.set_page_config(
    page_title="KDM Student Onboarding Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced professional styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main container styling */
    .main {
        padding-top: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Animated background */
    .main-header {
        background: linear-gradient(-45deg, #1e3a8a, #3b82f6, #0ea5e9, #06b6d4);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.95);
        margin: 1rem 0 0 0;
        font-size: 1.3rem;
        text-align: center;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* Enhanced sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    .sidebar-section {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .sidebar-section:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    
    .agent-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.75rem;
        margin-top: 1rem;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .agent-card:hover {
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
        transform: translateX(4px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }
    
    .agent-icon {
        font-size: 1.2rem;
        margin-right: 0.75rem;
    }
    
    .agent-name {
        color: #334155;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    /* Enhanced chat container */
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .chat-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #06b6d4, #8b5cf6, #3b82f6);
        background-size: 200% 100%;
        animation: gradientShift 8s ease infinite;
    }
    
    .session-header {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid #0284c7;
        position: relative;
    }
    
    .session-header h3 {
        margin: 0;
        color: #0369a1;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
    }
    
    /* Enhanced chat styling */
    .stChatMessage {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.8);
    }
    
    /* Typing indicator animation */
    .typing-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #3b82f6;
        animation: typing 1.4s infinite ease-in-out;
        margin: 0 2px;
    }
    
    .typing-indicator:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1.2); opacity: 1; }
    }
    
    /* Status indicator with pulse */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: linear-gradient(45deg, #10b981, #059669);
        border-radius: 50%;
        margin-right: 0.75rem;
        animation: pulse 2s infinite;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.7; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Enhanced welcome message */
    .welcome-message {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid #0284c7;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .welcome-message::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .welcome-content {
        position: relative;
        z-index: 1;
    }
    
    /* Feature highlights */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
        border: 1px solid #e2e8f0;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.2rem;
        }
        .main-header p {
            font-size: 1.1rem;
        }
        .feature-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# Enhanced main header with animation
st.markdown("""
<div class="main-header">
    <h1>🎓 KDM Student Onboarding</h1>
    <p>Your intelligent admission journey companion powered by AI</p>
</div>
""", unsafe_allow_html=True)

# --- Enhanced Professional Sidebar ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-section">
        <h3 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1.3rem; text-align: center;">
            <span class="status-indicator"></span>AI Agent Network
        </h3>
        <div class="agent-grid">
            <div class="agent-card">
                <span class="agent-icon">👤</span>
                <span class="agent-name">Student Profiler</span>
            </div>
            <div class="agent-card">
                <span class="agent-icon">📄</span>
                <span class="agent-name">Document Digitiser</span>
            </div>
            <div class="agent-card">
                <span class="agent-icon">✅</span>
                <span class="agent-name">Eligibility Checker</span>
            </div>
            <div class="agent-card">
                <span class="agent-icon">🎯</span>
                <span class="agent-name">Programme Recommender</span>
            </div>
            <div class="agent-card">
                <span class="agent-icon">💰</span>
                <span class="agent-name">Fee Calculator</span>
            </div>
            <div class="agent-card">
                <span class="agent-icon">🏛️</span>
                <span class="agent-name">Registration Concierge</span>
            </div>
            <div class="agent-card">
                <span class="agent-icon">💬</span>
                <span class="agent-name">Smart FAQ Assistant</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced New Chat Button
    st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
    if st.button("🔄 Start New Conversation", key="new_chat"):
        if 'session_id' in st.session_state:
            del st.session_state.session_id
        if 'history' in st.session_state:
            del st.session_state.history
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced session info
    if 'session_id' in st.session_state:
        st.markdown(f"""
        <div class="sidebar-section" style="margin-top: 1.5rem;">
            <h4 style="margin: 0 0 1rem 0; color: #64748b; font-size: 1rem; text-align: center;">
                🔗 Current Session
            </h4>
            <div style="background: #f1f5f9; padding: 1rem; border-radius: 8px; text-align: center;">
                <code style="font-size: 0.85rem; color: #475569; font-weight: 500;">
                    {st.session_state.session_id[:8]}...
                </code>
                <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #64748b;">
                    <span class="status-indicator" style="width: 6px; height: 6px; margin-right: 0.5rem;"></span>
                    Active & Ready
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Enhanced Main Chat Container ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Initialize session
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.history = []

# Enhanced session header
st.markdown(f"""
<div class="session-header">
    <h3>💬 AI Conversation Hub</h3>
    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; color: #0369a1; font-weight: 500;">
        Session: {st.session_state.session_id[:8]}... • 
        <span style="color: #059669;">
            <span class="typing-indicator"></span>
            <span class="typing-indicator"></span>
            <span class="typing-indicator"></span>
            Ready to assist
        </span>
    </p>
</div>
""", unsafe_allow_html=True)

# Enhanced welcome message with features
if not st.session_state.history:
    st.markdown("""
    <div class="welcome-message">
        <div class="welcome-content">
            <h4 style="margin: 0 0 1rem 0; color: #0369a1; font-size: 1.4rem; text-align: center;">
                👋 Welcome to KDM's AI-Powered Admission Hub!
            </h4>
            <p style="margin: 0 0 1.5rem 0; color: #075985; line-height: 1.6; text-align: center; font-size: 1.1rem;">
                I'm your intelligent admission assistant, ready to guide you through your entire educational journey. 
                Let's start by getting to know you better!
            </p>
            
           
            
           
    """, unsafe_allow_html=True)
    st.session_state.history.append({
        "role": "assistant", 
        "content": "Hello! I'm your KDM Student Onboarding Assistant. I'll help you navigate through your entire admission journey - from program selection to enrollment. Lets get started! How can I help you today?"
    })

# Display chat messages
for message in st.session_state.history:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# Enhanced chat input
if prompt := st.chat_input("💬 Ask me anything about admissions, programs, or requirements...", key="chat_input"):
    # Add user message
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Get AI response with enhanced loading
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🧠 AI is thinking... Processing your request"):
            response = call_agent(prompt, st.session_state.session_id)

        if response:
            st.session_state.history.append({"role": "assistant", "content": response})
            st.markdown(response)
        else:
            error_message = "I apologize, but I encountered an issue. Please try rephrasing your question or check your connection."
            st.session_state.history.append({"role": "assistant", "content": error_message})
            st.markdown(f"⚠️ {error_message}")

    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Enhanced footer with additional info
st.markdown("""
<div style="text-align: center; padding: 3rem 0; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 16px; margin-top: 2rem;">
    <div style="max-width: 600px; margin: 0 auto; padding: 0 2rem;">
        <p style="margin: 0 0 1rem 0; color: #475569; font-size: 1rem; font-weight: 500;">
            🚀 Powered by Advanced AI Technology
        </p>
        <p style="margin: 0; color: #94a3b8; font-size: 0.9rem; line-height: 1.5;">
            Built with Google ADK & Streamlit • KDM Global Education<br/>
            <span style="color: #64748b;">Transforming education through intelligent automation</span>
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
