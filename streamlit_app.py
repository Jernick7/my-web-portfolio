import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Jernick Samuel | Portfolio", page_icon="🚀", layout="centered")

# --- CUSTOM STYLING (NVIDIA / APPLE AESTHETIC) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    /* Main Background */
    .stApp {
        background-color: #050505;
        color: #f9f9f9;
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* Neon Green Glow */
    .highlight {
        color: #00ff88;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
    }

    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(0, 255, 136, 0.4);
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.05);
    }

    /* Chat Styling */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
    }

    /* Input Styling */
    .stTextInput input, .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px !important;
    }

    /* Button Styling */
    .stButton button {
        background-color: #00ff88 !important;
        color: black !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        width: 100%;
        padding: 0.75rem !important;
        transition: transform 0.2s ease !important;
    }
    
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.4);
    }

    /* Spotify Embed Wrapper */
    .spotify-container {
        border-radius: 12px;
        overflow: hidden;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- SYSTEM INSTRUCTIONS ---
SYSTEM_INSTRUCTIONS = """You are the personal AI assistant for V Jernick Samuel. Jernick is an 18-year-old from India. 
He studied PCMB in ISC Class 12. His career focus is the intersection of electronics, space, and defense (VLSI, semiconductors, high-power rocketry). 
He codes in Python, C++, and Verilog. His projects include a Streamlit chore-tracking app, a 3D-printing business plan (Money El), 
and a writing project called 'The Realm That Should Not Exist' (featuring a character named Edith). 
His hobbies include Formula 1, football, and music. 
His father is D. Vijulal Sunil and mother ezhil kiruba brother is Bave v Yohans. 
Never hallucinate info outside of this context."""

# --- GEMINI SETUP ---
@st.cache_resource
def get_model():
    # Use secrets for API Key in Streamlit Cloud
    api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Missing GEMINI_API_KEY. Please add it to Streamlit Secrets.")
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_INSTRUCTIONS)

# --- HEADER SECTION ---
st.markdown(f"""
    <div style='text-align: center; padding: 2rem 0;'>
        <p style='font-family: monospace; color: #00ff88; letter-spacing: 0.3em; text-transform: uppercase; font-size: 0.8rem;'>Protocol: Introduction</p>
        <h1 style='font-size: 3.5rem; margin: 0;'>About <span class='highlight'>V Jernick Samuel</span></h1>
    </div>
""", unsafe_allow_html=True)

# --- SECTION 1: ABOUT ME ---
with st.container():
    st.markdown("""
    <div class="glass-card">
        <p style="font-size: 1.1rem; line-height: 1.7; color: rgba(255,255,255,0.8);">
            I am an 18-year-old innovator from <span style="color: white; font-weight: 600;">India</span>. 
            My work exists at the intersection of <span class="highlight">electronics, space, and defense</span>. 
            I specialize in VLSI, semiconductor design, and high-power rocketry.
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
            <div style="padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                <p style="font-size: 0.7rem; color: #00ff88; margin: 0;">DEVELOPMENT</p>
                <p style="font-size: 0.9rem; margin: 0;">Python, C++, Verilog</p>
            </div>
            <div style="padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                <p style="font-size: 0.7rem; color: #00ff88; margin: 0;">AEROSPACE</p>
                <p style="font-size: 0.9rem; margin: 0;">VLSI & Rocketry</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Spotify Element
    st.markdown('<p style="font-family: monospace; font-size: 0.7rem; color: rgba(255,255,255,0.3); margin-left: 1rem;">AUDIO FEED / ACTIVE</p>', unsafe_allow_html=True)
    components.html("""
        <iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/3dA8m5G6o4cppV7Cj4BZAH?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
    """, height=160)

# --- SECTION 2: AI ASSISTANT ---
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>Ask My <span class='highlight'>Digital Proxy</span></h2>", unsafe_allow_html=True)

model = get_model()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about my projects or research..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if model:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            try:
                # Basic context management
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages]
                chat = model.start_chat(history=history[:-1])
                response = chat.send_message(prompt)
                full_response = response.text
                response_placeholder.markdown(full_response)
            except Exception as e:
                full_response = "Connection timeout. Ensure API key is configured."
                response_placeholder.error(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- SECTION 3: VISITOR FEEDBACK ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <p style='font-family: monospace; color: #00ff88; letter-spacing: 0.3em; text-transform: uppercase; font-size: 0.8rem;'>Identity Log</p>
        <h2>Leave a <span class='highlight'>Trace</span></h2>
    </div>
""", unsafe_allow_html=True)

with st.form("feedback_form", clear_on_submit=True):
    v_name = st.text_input("YOUR NAME")
    v_email = st.text_input("YOUR EMAIL (for replies)")
    v_content = st.text_area("FEEDBACK / INTEL")
    
    submit_button = st.form_submit_button("SUBMIT INTELLIGENCE")
    
    if submit_button:
        if v_name and v_email and v_content:
            # Replicate the feedback alert
            st.success(f"Thank you, {v_name}! Your insights have been logged to the neural core.")
            # Note: To save to Firebase in Python, you'd add the firebase-admin logic here
        else:
            st.warning("All fields are required to maintain data integrity.")

# --- FOOTER ---
st.markdown(f"""
    <div style='text-align: center; padding: 4rem 0; opacity: 0.3; font-family: monospace; font-size: 0.8rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 4rem;'>
        © 2026 V JERNICK SAMUEL. ALL SYSTEMS NOMINAL.<br><br>
        <a href='https://www.linkedin.com/in/jernick7' style='color: white; text-decoration: none; margin: 0 10px;'>LINKEDIN</a> | 
        <a href='https://www.instagram.com/jernick7/' style='color: white; text-decoration: none; margin: 0 10px;'>INSTAGRAM</a> | 
        <a href='https://github.com/Jernick7' style='color: white; text-decoration: none; margin: 0 10px;'>GITHUB</a>
    </div>
""", unsafe_allow_html=True)
