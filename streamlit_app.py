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
    
    /* Global Reset & Theme */
    .stApp {
        background-color: #050505;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(5, 5, 5, 0.8);
        backdrop-filter: blur(10px);
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.04em !important;
        color: white;
    }

    /* Neon Green Glow */
    .highlight {
        color: #00ff88;
        text-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
    }

    /* Bento Grid Elements */
    .bento-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 2rem;
        height: 100%;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .bento-card:hover {
        border-color: rgba(0, 255, 136, 0.5);
        background: rgba(0, 255, 136, 0.02);
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }

    .tag-container {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }

    .tag {
        padding: 4px 12px;
        background: rgba(0, 255, 136, 0.1);
        border: 1px solid rgba(0, 255, 136, 0.2);
        color: #00ff88;
        font-family: monospace;
        font-size: 0.7rem;
        border-radius: 100px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Chat Styling - Sleeker */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        margin-bottom: 1rem !important;
    }

    /* Intelligence Terminal Form */
    .terminal-header {
        font-family: monospace;
        color: #00ff88;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }

    .stTextInput input, .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.2) !important;
    }

    /* Submit Button - NVIDIA Style */
    .stButton button {
        background: linear-gradient(135deg, #00ff88 0%, #00bc6e 100%) !important;
        color: #000 !important;
        border: none !important;
        padding: 1rem 2rem !important;
        border-radius: 16px !important;
        font-weight: 700 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }

    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(0, 255, 136, 0.5);
    }

    /* Sidebar / Navigation (if used) */
    .css-1d391kg {
        background-color: #050505;
    }

    /* Spotify Wrapper */
    .spotify-box {
        border-left: 2px solid #00ff88;
        background: rgba(0, 255, 136, 0.02);
        padding: 1rem;
        border-radius: 0 12px 12px 0;
    }

    hr {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.1), transparent);
        margin: 4rem 0;
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
    <div style='text-align: center; padding: 4rem 0 2rem 0;'>
        <p style='font-family: monospace; color: #00ff88; letter-spacing: 0.5em; text-transform: uppercase; font-size: 0.7rem; margin-bottom: 1rem;'>Protocol: Introduction</p>
        <h1 style='font-size: 4rem; line-height: 1; margin: 0;'>About <br><span class='highlight' style='font-size: 5rem;'>V Jernick Samuel</span></h1>
    </div>
""", unsafe_allow_html=True)

# --- SECTION 1: BENTO ABOUT ME ---
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("""
    <div class="bento-card">
        <h3 style="margin-top: 0;">Visionary Core</h3>
        <p style="font-size: 1.1rem; line-height: 1.6; color: rgba(255,255,255,0.7); margin-bottom: 2rem;">
            Innovator based in <span style="color: white; font-weight: 600;">India</span>. 
            Exploring the limits of <span class="highlight">silicon and space</span>. 
            Focused on high-power rocketry and semiconductor architecture.
        </p>
        <div class="tag-container">
            <span class="tag">VLSI</span>
            <span class="tag">PCMB</span>
            <span class="tag">Semiconductors</span>
            <span class="tag">Defense Tech</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="bento-card" style="text-align: center;">
        <p style="font-family: monospace; font-size: 0.7rem; color: #00ff88; margin-bottom: 0.5rem;">PRIMARY OPS</p>
        <h2 style="margin: 0; font-size: 3rem;">ISC</h2>
        <p style="font-family: monospace; font-size: 0.8rem; opacity: 0.5;">Class 12 Architecture</p>
        <div style="height: 1px; width: 40%; background: #00ff88; margin: 1rem auto; opacity: 0.3;"></div>
        <p style="font-size: 0.9rem; opacity: 0.8;">Python | C++ | Verilog</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
# Audio Section
st.markdown("""
    <div class="spotify-box">
        <p style="font-family: monospace; font-size: 0.7rem; color: #00ff88; margin-bottom: 0.5rem; letter-spacing: 2px;">SECURE AUDIO LINK / LIVE</p>
    </div>
""", unsafe_allow_html=True)
components.html("""
    <iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/3dA8m5G6o4cppV7Cj4BZAH?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
""", height=160)

# --- SECTION 2: AI PROXY ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-family: monospace; color: #00ff88; font-size: 0.8rem; letter-spacing: 0.3em; margin-bottom: 0;'>NEURAL INTERFACE</p>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-top: 0.5rem;'>Digital <span class='highlight'>Proxy</span></h2>", unsafe_allow_html=True)

model = get_model()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat display in a contained area
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Query local history or projects..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    if model:
        with chat_container:
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                try:
                    history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages]
                    chat = model.start_chat(history=history[:-1])
                    response = chat.send_message(prompt)
                    full_response = response.text
                    response_placeholder.markdown(full_response)
                except Exception as e:
                    full_response = "Interface offline. Verify API configuration."
                    response_placeholder.error(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- SECTION 3: INTELLIGENCE TERMINAL ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; margin-bottom: 3rem;'>
    <p class="terminal-header">IDENTITY LOG V2.0</p>
    <h2>Leave a <span class='highlight'>Trace</span></h2>
</div>
""", unsafe_allow_html=True)

# Custom Bento Form
col_form1, col_form2 = st.columns([1, 1])

with st.form("terminal_intel", clear_on_submit=True):
    with col_form1:
        v_name = st.text_input("IDENTIFIER NAME", placeholder="User-77")
    with col_form2:
        v_email = st.text_input("REPLY ADDRESS", placeholder="agent@network.com")
        
    v_content = st.text_area("INTEL / FEEDBACK", placeholder="Transmission begins...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.form_submit_button("SYNC TO NEURAL CORE")
    
    if submit_button:
        if v_name and v_email and v_content:
            st.success(f"Log entry successful. Connection established, {v_name}.")
        else:
            st.error("Incomplete packet. Required fields missing.")

# --- PROJECTS BENTO (OPTIONAL - GIVING MORE CONTENT) ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-family: monospace; color: #00ff88; font-size: 0.8rem; letter-spacing: 0.3em; margin-bottom: 0;'>ACTIVE REPOSITORY</p>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-top: 0.5rem;'>Key <span class='highlight'>Deployments</span></h2>", unsafe_allow_html=True)

pcol1, pcol2, pcol3 = st.columns(3)
with pcol1:
    st.markdown("""
    <div class="bento-card">
        <p style="font-size: 0.7rem; color: #00ff88; font-family: monospace;">01. LITERARY</p>
        <p style="font-weight: 700; font-size: 1.1rem;">Edith Proj</p>
        <p style="font-size: 0.8rem; opacity: 0.6;">The Realm That Should Not Exist.</p>
    </div>
    """, unsafe_allow_html=True)
with pcol2:
    st.markdown("""
    <div class="bento-card">
        <p style="font-size: 0.7rem; color: #00ff88; font-family: monospace;">02. VENTURE</p>
        <p style="font-weight: 700; font-size: 1.1rem;">Money El</p>
        <p style="font-size: 0.8rem; opacity: 0.6;">3D-Printing business architecture.</p>
    </div>
    """, unsafe_allow_html=True)
with pcol3:
    st.markdown("""
    <div class="bento-card">
        <p style="font-size: 0.7rem; color: #00ff88; font-family: monospace;">03. SYSTEMS</p>
        <p style="font-weight: 700; font-size: 1.1rem;">Chore App</p>
        <p style="font-size: 0.8rem; opacity: 0.6;">Streamlit-based ops tracker.</p>
    </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"""
    <div style='text-align: center; padding: 6rem 0 4rem 0; font-family: monospace; font-size: 0.7rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 6rem;'>
        <p style='color: rgba(255,255,255,0.3);'>© 2026 V JERNICK SAMUEL. ALL SYSTEMS NOMINAL.</p>
        <div style='display: flex; justify-content: center; gap: 2rem; margin-top: 2rem;'>
            <a href='https://www.linkedin.com/in/jernick7' style='color: white; text-decoration: none; opacity: 0.5;'>LINKEDIN</a> 
            <a href='https://www.instagram.com/jernick7/' style='color: white; text-decoration: none; opacity: 0.5;'>INSTAGRAM</a> 
            <a href='https://github.com/Jernick7' style='color: white; text-decoration: none; opacity: 0.5;'>GITHUB</a>
        </div>
    </div>
""", unsafe_allow_html=True)

