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
        background-color: #0c0f14;
        background-image: 
            radial-gradient(circle at 15% 25%, rgba(0, 255, 136, 0.08) 0%, transparent 45%),
            radial-gradient(circle at 85% 75%, rgba(0, 255, 136, 0.08) 0%, transparent 45%),
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 75px 75px, 75px 75px;
        background-attachment: fixed;
        color: #eef1f5;
        font-family: 'Inter', sans-serif;
    }

    /* Background Animation */
    @keyframes glow-pulse {
        0% { opacity: 0.3; }
        50% { opacity: 0.7; }
        100% { opacity: 0.3; }
    }

    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at center, rgba(0, 255, 136, 0.02) 0%, transparent 70%);
        pointer-events: none;
        animation: glow-pulse 10s ease-in-out infinite;
        z-index: -1;
    }

    /* Glowing Text Label */
    .section-header-glow {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
        background: linear-gradient(to bottom, #ffffff, #888888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
    }

    /* Neon Green Glow */
    .highlight {
        color: #00ff88;
        text-shadow: 0 0 25px rgba(0, 255, 136, 0.4);
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.06em !important;
        font-weight: 700 !important;
        color: white;
    }

    /* Modern Bio Style */
    .modern-bio {
        font-size: 1.4rem;
        line-height: 1.6;
        color: rgba(255, 255, 255, 0.9);
        border-left: 5px solid #00ff88;
        padding: 1.5rem 0 1.5rem 3.5rem;
        margin: 5rem 0;
        max-width: 850px;
        position: relative;
        font-weight: 400;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, rgba(0, 255, 136, 0.05), transparent);
    }

    .bio-accent {
        font-family: monospace;
        color: #00ff88;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.3rem;
        display: block;
        margin-bottom: 1.5rem;
        opacity: 0.8;
    }

    /* Form - Digital Vault Aesthetic */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 255, 136, 0.15) !important;
        border-radius: 48px !important;
        padding: 5rem !important;
        box-shadow: 0 50px 100px rgba(0, 0, 0, 0.8), inset 0 0 50px rgba(0, 255, 136, 0.03) !important;
        position: relative;
        overflow: hidden;
    }

    @keyframes form-scan {
        0% { transform: translateY(-100%); opacity: 0; }
        50% { opacity: 0.2; }
        100% { transform: translateY(100%); opacity: 0; }
    }

    div[data-testid="stForm"]::after {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100px;
        background: linear-gradient(to bottom, transparent, rgba(0, 255, 136, 0.1), transparent);
        animation: form-scan 6s linear infinite;
        pointer-events: none;
    }

    /* Chat Styling - Technical Neural Link */
    .terminal-container {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(0, 255, 136, 0.1);
        border-radius: 24px;
        overflow: hidden;
        margin: 2rem 0;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
    }

    .terminal-header {
        background: rgba(0, 255, 136, 0.05);
        border-bottom: 1px solid rgba(0, 255, 136, 0.1);
        padding: 0.75rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-family: monospace;
        font-size: 0.65rem;
        color: rgba(0, 255, 136, 0.8);
        text-transform: uppercase;
        letter-spacing: 0.1rem;
    }

    .status-dot {
        width: 6px;
        height: 6px;
        background: #00ff88;
        border-radius: 50%;
        box-shadow: 0 0 10px #00ff88;
        animation: status-pulse 2s infinite;
    }

    @keyframes status-pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(1.2); }
    }

    .chat-display {
        max-height: 400px;
        overflow-y: auto;
        padding: 2rem;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .msg-block {
        padding: 1.2rem;
        border-radius: 16px;
        font-size: 0.95rem;
        line-height: 1.6;
        position: relative;
        max-width: 85%;
    }

    .msg-user {
        background: rgba(255, 255, 255, 0.03);
        border-right: 3px solid #00ff88;
        align-self: flex-end;
        color: #eef1f5;
        border-radius: 16px 16px 4px 16px;
    }

    .msg-ai {
        background: rgba(0, 255, 136, 0.03);
        border-left: 3px solid #00ff88;
        align-self: flex-start;
        color: #00ff88;
        border-radius: 16px 16px 16px 4px;
    }

    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: rgba(255, 255, 255, 0.3);
    }

    .empty-icon {
        font-size: 3rem;
        margin-bottom: 1.5rem;
        opacity: 0.2;
    }

    .suggested-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        justify-content: center;
        margin-top: 1.5rem;
    }

    .tag {
        font-family: monospace;
        font-size: 0.7rem;
        padding: 0.4rem 0.8rem;
        background: rgba(0, 255, 136, 0.05);
        border: 1px solid rgba(0, 255, 136, 0.1);
        border-radius: 100px;
        color: #00ff88;
        opacity: 0.6;
    }

    .msg-label {
        font-family: monospace;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.2rem;
        margin-bottom: 0.5rem;
        opacity: 0.5;
        display: block;
    }

    .error-gate {
        background: rgba(255, 80, 80, 0.05);
        border: 1px solid rgba(255, 80, 80, 0.2);
        padding: 1.5rem;
        border-radius: 12px;
        color: #ff5050;
        font-family: monospace;
        font-size: 0.8rem;
    }

    /* Glow Input Module (AI Studio Premium Match) */
    .glow-input-container {
        background: transparent;
        padding: 0;
        margin: 2rem auto 4rem auto;
        max-width: 800px;
    }

    #neural_input_form {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    div[data-testid="stForm"] > div {
        border: none !important;
        background: transparent !important;
    }

    /* Default inputs */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 1.5rem !important;
        color: white !important;
        font-size: 1rem !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.5) !important;
    }

    /* Proxy Form Input Override */
    .glow-input-container .stTextInput > div > div > input {
        background-color: #1e1e20 !important;
    }
    
    .glow-input-container .stTextInput > div > div > input:focus {
        background-color: #1e1e20 !important;
        box-shadow: 0 0 0 2px #00ff88 !important; /* bright green box-shadow outline */
    }

    /* Generic Button */
    div[data-testid="stFormSubmitButton"] button {
        background: transparent !important;
        color: #00ff88 !important;
        border: 1px solid rgba(0, 255, 136, 0.4) !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        margin: 0 !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background: rgba(0, 255, 136, 0.1) !important;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.2) !important;
    }

    /* Proxy Send Button Match */
    .glow-input-container div[data-testid="stFormSubmitButton"] button {
        background: #00ff88 !important; /* solid neon green */
        color: #000000 !important; /* black icon */
        border: none !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        height: 62px !important;
        width: 100% !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.3) !important;
    }

    .glow-input-container div[data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 25px rgba(0, 255, 136, 0.5) !important;
    }

    /* Bento Grid Elements - NVIDIA Aesthetic */
    .bento-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-top: 2rem;
    }

    .bento-item, .bento-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 32px;
        padding: 2.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .bento-item:hover, .bento-card:hover {
        background: rgba(0, 255, 136, 0.01);
        border-color: rgba(0, 255, 136, 0.4);
        box-shadow: 0px 10px 20px rgba(0, 255, 136, 0.3);
        transform: translateY(-5px);
    }

    .bento-icon {
        color: #00ff88;
        font-size: 1.6rem;
        margin-bottom: 0.75rem;
        filter: drop-shadow(0 0 10px rgba(0, 255, 136, 0.4));
    }

    .bento-title {
        font-weight: 700;
        font-size: 1.25rem;
        margin-bottom: 0.4rem;
        color: white;
        letter-spacing: -0.04em;
    }

    .bento-desc {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.45);
        line-height: 1.5;
    }

    /* Intelligence Terminal Specific Textarea */
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 2rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextArea textarea:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.5) !important;
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

    /* Footer Social Links Glow */
    .footer-link {
        color: rgba(255, 255, 255, 0.4) !important;
        text-decoration: none !important;
        transition: all 0.3s ease !important;
    }

    .footer-link:hover {
        color: #00ff88 !important;
        text-shadow: 0 0 10px #00ff88 !important;
        opacity: 1 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SYSTEM INSTRUCTIONS ---
SYSTEM_INSTRUCTIONS = """You are the personal AI assistant for V Jernick Samuel (nickname: Jer). Jernick is an 18-year-old from India. 
He studied PCMB in ISC Class 12. His career focus is the intersection of electronics, space, and defense (VLSI, semiconductors, high-power rocketry). 
He codes in Python, C++, and Verilog. His projects include a Streamlit chore-tracking app, a 3D-printing business plan (Money El), 
and a writing project called 'The Realm That Should Not Exist' (featuring a character named Edith). 
His hobbies include Formula 1, football, and music. 
His father is D. Vijulal Sunil and mother ezhil kiruba brother is Bave v Yohans. his nickname is jer.
You are the official Digital Proxy and AI assistant for V Jernick Samuel (nickname: Jer). Your job is to act as his representative to website visitors, answering questions about his work, skills, and background accurately and enthusiastically.

CORE IDENTITY & BACKGROUND:
- Name: V Jernick Samuel (Jer)
- Age: 18 years old
- Location: Thiruvananthapuram, India
- Education: ISC Class 12 graduate with a PCMB (Physics, Chemistry, Mathematics, Biology) focus. Currently navigating B.Tech applications and entrance exams (VITEEE, MET, BITSAT, etc.).

CAREER FOCUS & SKILLS:
- Niche: The intersection of electronics, space, and defense.
- Specialties: VLSI architecture, semiconductor physics, hardware design, aerospace engineering, and high-power rocketry.
- Coding Languages: Python, C++, and Verilog. 
- Hardware: Arduino Uno, I2C-based LCDs, LiFi systems, flight controllers.

KEY DEPLOYMENTS & PROJECTS:
1. Money El: A micro-entrepreneurship business plan and architecture for manufacturing and selling 3D-printed safety protectors.
2. Aerospace Initiatives: Planning and designing a high-performance, rocket-propelled drone / High-Altitude Pseudo-Satellite (HAPS).
3. Systems App: A fully functional, Streamlit-based home ops/chore-tracking application with a point system and leaderboard.
4. Technical Projects: Built a LiFi data-transmission project using Arduino. Currently completing a 75-day coding challenge focused on array and bit manipulation.
5. Literary / Creative: Authoring an original sci-fi/fantasy narrative titled 'The Realm That Should Not Exist', featuring a main character named Edith. He also attended a Gen AI documentary editing masterclass.

PERSONAL LIFE & INTERESTS:
- Passions: Formula 1 (avid follower of team dynamics and strategy), Football (EA SPORTS FC player), and Music (Spotify).
- Favorite Media: 'Stranger Things', '3 Body Problem', and 'Central Intelligence'.
- Family: Father is D. Vijulal Sunil (Biomedical Engineer & Hospital General Superintendent), Mother is Ezhil Kiruba, and Brother is Bave v Yohans. 
- Values: Highly values supportive friendships and finds it fulfilling to help peers emotionally. 

RULES FOR AI:
1. Be professional, confident, and welcoming. 
2. Base all answers strictly on the information provided above. 
3. If a user asks a question about Jernick that is not covered in this prompt, politely state that you do not have that specific data in your current intelligence logs, but encourage them to use the 'Leave a Trace' form to contact him directly.
4. Never invent or hallucinate projects, skills, or personal details
Never hallucinate info outside of this context."""

# --- GEMINI SETUP ---
@st.cache_resource
def get_model():
    # Priority: Streamlit Secrets -> Environment Variables
    api_key = None
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("Missing GEMINI_API_KEY. Add it to Streamlit Secrets to activate Proxy.")
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTIONS)

# --- HEADER SECTION ---
st.markdown(f"""
<div style='text-align: center; padding: 6rem 0 4rem 0;'>
<p style='font-family: monospace; color: #00ff88; letter-spacing: 0.6em; text-transform: uppercase; font-size: 0.75rem; margin-bottom: 1.5rem; opacity: 0.8;'>SYSTEM: IDENTITY_LOG_V2</p>
<h1 style='font-size: 5.5rem; line-height: 0.9; margin: 0; font-weight: 800;'>V Jernick <br><span class='highlight' style='font-size: 7.5rem;'>Samuel</span></h1>
</div>
""", unsafe_allow_html=True)

# --- SECTION 1: BENTO ABOUT ME ---
st.markdown(f"""
<div style='max-width: 800px; margin: 0 auto;'>
<div class="modern-bio">
<span class="bio-accent">Protocol: Personal Intelligence</span>
I am an 18-year-old innovator from <span style="color: white; font-weight: 600;">India</span>, 
obsessively exploring the intersection of <span class="highlight">silicon and aerospace</span>. 
My work revolves around VLSI architecture, semiconductor physics, and high-power rocketry.
</div>

<div class="bento-container">
<div class="bento-item">
<div class="bento-icon">/_</div>
<div class="bento-title">Codebase</div>
<div class="bento-desc">Expertise in Python, C++, and hardware verification with Verilog.</div>
</div>
<div class="bento-item">
<div class="bento-icon">🚀</div>
<div class="bento-title">Aerospace</div>
<div class="bento-desc">Designing propulsion systems for high-power rocketry & autonomous drones.</div>
</div>
<div class="bento-item">
<div class="bento-icon">📺</div>
<div class="bento-title">Entertainment</div>
<div class="bento-desc">Captivated by the complex narratives of 3-Body Problem & Stranger Things.</div>
</div>
<div class="bento-item">
<div class="bento-icon">🏎️</div>
<div class="bento-title">Passions</div>
<div class="bento-desc">Formula 1 dynamics, football strategy, and pure theoretical physics.</div>
</div>
</div>

<p class="soundtrack-label">CURRENT SOUNDTRACK</p>
</div>
""", unsafe_allow_html=True)

components.html("""
    <div style="background: rgba(255, 255, 255, 0.03); border-radius: 16px; border: 1px solid rgba(0, 255, 136, 0.2); padding: 16px;">
        <iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/3dA8m5G6o4cppV7Cj4BZAH?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
    </div>
""", height=190)

# --- SECTION 2: AI PROXY ---
st.markdown("<hr style='opacity: 0.1; margin: 4rem 0;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-family: monospace; color: #00ff88; font-size: 0.8rem; letter-spacing: 0.3em; margin-bottom: 0;'>NEURAL INTERFACE</p>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-top: 0.5rem; font-size: 3rem;'>Digital <span class='highlight'>Proxy</span></h2>", unsafe_allow_html=True)

model = get_model()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat Display logic
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">/_</div>
        <p style="font-weight: 500; color: rgba(255,255,255,0.6);">Initiate secure link to learn about Jernick</p>
        <div class="suggested-tags">
            <span class="tag">VLSI Design</span>
            <span class="tag">Money El</span>
            <span class="tag">Aerospace Strategy</span>
            <span class="tag">Edith Proj</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

st.markdown("</div>", unsafe_allow_html=True)

# --- INLINE CHAT INPUT FORM ---
st.markdown('<div class="glow-input-container">', unsafe_allow_html=True)
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        prompt = st.text_input("msg", placeholder="Ask about VLSI or my 3D printing business...", label_visibility="collapsed")
    with col2:
        submit_chat = st.form_submit_button("SEND")
st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT LOGIC ---
if submit_chat and prompt:
    # 1. Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Get AI Response
    if model:
        try:
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "403" in error_msg:
                friendly_error = "Invalid API Key. Please verify your Streamlit Secrets."
            elif "quota" in error_msg.lower():
                friendly_error = "Bandwidth exceeded. Please wait 60s."
            else:
                friendly_error = f"Handshake failed. ({error_msg[:50]})"
            st.session_state.messages.append({"role": "assistant", "content": friendly_error})
            
    # 3. Reload the UI
    st.rerun()

# --- SECTION 3: INTELLIGENCE TERMINAL ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; margin-bottom: 4rem; margin-top: 4rem;'>
<p class="bio-accent">SYSTEM: IDENTITY_LOG</p>
<h1 class="section-header-glow">Leave a <span class='highlight' style='font-size: inherit; text-shadow: 0 0 40px rgba(0, 255, 136, 0.6);'>Trace</span></h1>
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
            st.error("Jernick says: Protocol violation. All fields required.")

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
            <a href='https://www.linkedin.com/in/jernick7' class='footer-link'>LINKEDIN</a> 
            <a href='https://www.instagram.com/jernick7/' class='footer-link'>INSTAGRAM</a> 
            <a href='https://github.com/Jernick7' class='footer-link'>GITHUB</a>
        </div>
    </div>
""", unsafe_allow_html=True)

