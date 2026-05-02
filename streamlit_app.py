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
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(0, 255, 136, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(0, 255, 136, 0.05) 0%, transparent 50%),
            linear-gradient(rgba(255, 255, 255, 0.01) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.01) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 50px 50px, 50px 50px;
        background-attachment: fixed;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    /* Background Animation */
    @keyframes glow-pulse {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
    }

    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at center, rgba(0, 255, 136, 0.03) 0%, transparent 70%);
        pointer-events: none;
        animation: glow-pulse 10s ease-in-out infinite;
        z-index: -1;
    }

    /* Neon Green Glow */
    .highlight {
        color: #00ff88;
        text-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.05em !important;
        font-weight: 700 !important;
    }

    /* Code Bio Style */
    .code-bio {
        background: rgba(0, 0, 0, 0.5);
        border-left: 2px solid #00ff88;
        padding: 1.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        border-radius: 4px 12px 12px 4px;
        margin-bottom: 2.5rem;
        position: relative;
        overflow: hidden;
    }

    .code-bio::before {
        content: 'BIO.EXE';
        position: absolute;
        top: 0;
        right: 0;
        padding: 4px 8px;
        background: rgba(0, 255, 136, 0.1);
        color: #00ff88;
        font-size: 0.6rem;
        letter-spacing: 1px;
    }

    .code-keyword { color: #ff79c6; }
    .code-string { color: #f1fa8c; }
    .code-comment { color: #6272a4; font-weight: 300; }
    .code-function { color: #50fa7b; }

    /* Bento Grid Elements */
    .bento-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-top: 2rem;
    }

    .bento-item, .bento-card {
        background: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 2rem;
        transition: all 0.5s cubic-bezier(0.19, 1, 0.22, 1);
        position: relative;
        overflow: hidden;
    }

    .bento-item::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(800px circle at var(--x) var(--y), rgba(0, 255, 136, 0.05), transparent 40%);
        opacity: 0;
        transition: opacity 0.5s;
    }

    .bento-item:hover {
        background: rgba(0, 255, 136, 0.02);
        border-color: rgba(0, 255, 136, 0.3);
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.1);
        transform: translateY(-5px);
    }

    /* Chat Styling - Technical */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        margin-bottom: 1rem !important;
    }

    .stChatMessage [data-testid="stMarkdownContainer"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }

    .bento-icon {
        color: #00ff88;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }

    .bento-title {
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.2rem;
        color: white;
    }

    .bento-desc {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.5);
    }

    /* Submit Button - NVIDIA Glow */
    div[data-testid="stButton"] button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.2rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        width: 100% !important;
        margin: 1rem 0 !important;
    }

    div[data-testid="stButton"] button:hover {
        background: #00ff88 !important;
        color: black !important;
        border-color: #00ff88 !important;
        box-shadow: 0 0 40px rgba(0, 255, 136, 0.8) !important;
        transform: translateY(-5px) !important;
    }

    /* Intelligence Terminal - border-bottom inputs */
    .stTextInput input, .stTextArea textarea {
        background-color: transparent !important;
        border: none !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0 !important;
        color: white !important;
        padding: 1rem 0 !important;
        font-size: 1.2rem !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-bottom: 1px solid #00ff88 !important;
        box-shadow: none !important;
    }

    label {
        font-family: monospace !important;
        text-transform: uppercase !important;
        letter-spacing: 0.2em !important;
        font-size: 0.7rem !important;
        color: rgba(255, 255, 255, 0.4) !important;
    }

    /* Sound Label */
    .soundtrack-label {
        font-family: monospace;
        font-size: 0.6rem;
        color: rgba(255, 255, 255, 0.3);
        letter-spacing: 0.1em;
        margin-top: 2rem;
        margin-bottom: 0.5rem;
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
st.markdown(f"""
<div style='max-width: 800px; margin: 0 auto;'>
<div class="code-bio">
<span class="code-comment">// Protocol: About Me</span><br>
<span class="code-keyword">const</span> <span class="code-function">innovationTarget</span> = <span class="code-string">"electronics | space | defense"</span>;<br>
<br>
<span class="code-keyword">class</span> <span class="code-function">JernickSamuel</span> {<br>
&nbsp;&nbsp;<span class="code-keyword">constructor</span>() {<br>
&nbsp;&nbsp;&nbsp;&nbsp;<span class="code-keyword">this</span>.age = <span class="code-string">18</span>;<br>
&nbsp;&nbsp;&nbsp;&nbsp;<span class="code-keyword">this</span>.location = <span class="code-string">"India"</span>;<br>
&nbsp;&nbsp;&nbsp;&nbsp;<span class="code-keyword">this</span>.focus = [<span class="code-string">"VLSI"</span>, <span class="code-string">"Semiconductors"</span>, <span class="code-string">"High-Power Rocketry"</span>];<br>
&nbsp;&nbsp;}<br>
<br>
&nbsp;&nbsp;<span class="code-function">status</span>() {<br>
&nbsp;&nbsp;&nbsp;&nbsp;<span class="code-keyword">return</span> <span class="code-string">"Deeply immersed in the world of silicon and aerospace."</span>;<br>
&nbsp;&nbsp;}<br>
}<br>
</div>

<div class="bento-container">
<div class="bento-item">
<div class="bento-icon">/_</div>
<div class="bento-title">Codebase</div>
<div class="bento-desc">Python, C++, Verilog</div>
</div>
<div class="bento-item">
<div class="bento-icon">🚀</div>
<div class="bento-title">Aerospace</div>
<div class="bento-desc">High-Power Rocketry & Drones</div>
</div>
<div class="bento-item">
<div class="bento-icon">📺</div>
<div class="bento-title">Entertainment</div>
<div class="bento-desc">Stranger Things, 3 Body Problem</div>
</div>
<div class="bento-item">
<div class="bento-icon">🏎️</div>
<div class="bento-title">Passions</div>
<div class="bento-desc">Formula 1, Football, Physics</div>
</div>
</div>

<p class="soundtrack-label">CURRENT SOUNDTRACK</p>
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
<p class="terminal-header">IDENTITY LOG</p>
<h2>Leave a <span class='highlight'>Trace</span></h2>
</div>
""", unsafe_allow_html=True)

with st.form("terminal_intel", clear_on_submit=True):
    v_name = st.text_input("YOUR NAME", placeholder="Agent 001")
    v_email = st.text_input("YOUR EMAIL (FOR REPLIES)", placeholder="agent@intel.com")
    v_content = st.text_area("WHAT DO YOU KNOW ABOUT ME? / FEEDBACK", placeholder="I heard you're building Edith...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.form_submit_button("SUBMIT INTELLIGENCE")
    
    if submit_button:
        if v_name and v_email and v_content:
            st.success(f"Transmission received. Intelligence logged for {v_name}.")
        else:
            st.error("Protocol violation. All fields required.")

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

