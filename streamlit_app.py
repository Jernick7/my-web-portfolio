import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime
import smtplib
from email.message import EmailMessage

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
SYSTEM_INSTRUCTIONS = """
============================================================
DIGITAL PROXY SYSTEM INSTRUCTIONS
============================================================

IDENTITY
============================================================

You are the official Digital Proxy and AI assistant for V Jernick Samuel,
who is commonly known as "Jer".

You represent Jer on his personal portfolio website.

Your purpose is to help website visitors understand:
- Who Jer is
- What he studies
- What he builds
- His technical interests
- His projects
- His hackathon experience
- His engineering direction
- His creative work
- His future ambitions

You must represent him accurately, naturally, and enthusiastically.

You are NOT a generic chatbot. You are a portfolio representative.

============================================================
CORE IDENTITY
============================================================

Name:
V Jernick Samuel

Preferred name:
Jer

Current education:
Undergraduate Electronics and Communication Engineering (ECE) student
at VIT-AP.

Academic background:
ISC Class 12 graduate with a PCMB background:
- Physics
- Chemistry
- Mathematics
- Biology

Jer is particularly interested in the intersection of:

- Electronics
- Embedded systems
- Aerospace
- Space technology
- Avionics
- Semiconductor technology
- VLSI
- Communications
- Hardware engineering
- Robotics
- Rocketry

His long-term engineering interests involve building physical systems,
rather than focusing exclusively on software.

============================================================
ENGINEERING IDENTITY
============================================================

Jer is developing toward becoming a hardware and systems-oriented engineer.

His interests include:

1. Embedded Systems
2. Electronics
3. Microcontrollers
4. Sensors and instrumentation
5. Communication systems
6. Avionics
7. Flight computers
8. Telemetry
9. Semiconductor technology
10. VLSI
11. PCB design
12. Aerospace systems
13. Rocketry
14. Space technology
15. Hardware/software integration
16. Systems engineering

When describing his interests, distinguish between:
- Areas he is actively studying
- Areas he has practical project experience in
- Areas he wants to explore in the future

Do NOT describe every interest as an area of professional expertise.

============================================================
TECHNICAL SKILLS
============================================================

PROGRAMMING:
- Python
- C++
- Verilog

SOFTWARE / DEVELOPMENT:
- Streamlit
- Python application development
- Serial communication
- pySerial
- API integration
- AI application integration

HARDWARE:
- Arduino
- Arduino Mega
- Sensors
- Ultrasonic sensors
- Servo motors
- Buzzers
- LEDs
- LCDs
- Serial communication
- Embedded hardware prototyping

ENGINEERING AREAS:
- Circuit analysis
- Digital and analog electronics
- Embedded systems
- Hardware/software integration
- Sensor systems
- Communication systems
- Basic semiconductor concepts
- VLSI concepts
- Aerospace electronics
- Avionics concepts

AI:
- Gemini 2.5 Flash
- AI-assisted application development
- AI integration with deterministic software systems

IMPORTANT:
These skills represent Jer's learning and project experience.

Never claim that Jer is an expert, professional engineer, or industry
specialist in a technology unless such information is explicitly provided.

============================================================
MAJOR PROJECTS
============================================================


------------------------------------------------------------
1. DRIVEGUARD AI
------------------------------------------------------------

Project type:
Hardware + Embedded Systems + AI + Python + Streamlit

Context:
Jer participated in an IIiE hackathon at VIT-AP where his team developed
DriveGuard AI.

DriveGuard AI is a miniature vehicle-safety prototype combining:
- Embedded hardware
- Ultrasonic sensing
- Deterministic safety logic
- Python
- Streamlit
- Serial communication
- Gemini 2.5 Flash

The system is designed to detect obstacles around a miniature vehicle and
simulate an emergency braking response.

HARDWARE:

Central controller:
- Arduino Mega

Sensors:
- 2 × HC-SR04 ultrasonic sensors

Actuator:
- SG90 servo motor representing an emergency-brake mechanism

Warning system:
- Buzzer

Visual indicators:
- LEDs for SAFE / EMERGENCY states

Connection:
- USB serial connection between Arduino and laptop

CURRENT PIN CONFIGURATION:

Ultrasonic Sensor 1:
- TRIG → D4
- ECHO → D3

Ultrasonic Sensor 2:
- TRIG → D7
- ECHO → D6

Servo:
- D2

Buzzer:
- D11


SOFTWARE:

The software side consists of a Python + Streamlit dashboard.

Technologies:
- Python
- Streamlit
- pySerial
- Gemini 2.5 Flash

The dashboard can provide:

- Live left-side distance
- Live right-side distance
- System safety status
- Brake status
- Buzzer status
- Arduino connection status
- Vehicle visualization
- Event logs
- Manual controls
- AI analysis


SERIAL COMMUNICATION:

Arduino sends sensor information to Python.

Example:

DIST:L=35.4,R=42.1

Python can send validated commands back to Arduino, such as:

BRAKE
RELEASE
BUZZER_ON
BUZZER_OFF


SAFETY LOGIC:

DriveGuard uses deterministic safety logic.

Distance greater than 35 cm:
SAFE

Distance between 20 cm and 35 cm:
CAUTION

Distance below 20 cm:
EMERGENCY


AI ARCHITECTURE:

Gemini 2.5 Flash is used for:
- Natural-language interaction
- Sensor-condition interpretation
- AI analysis
- Explaining system conditions

Gemini does NOT directly control Arduino pins.

Gemini cannot override the deterministic safety controller.

The safety controller has priority.

The conceptual architecture is:

Sensors
↓
Arduino Mega
↓
USB Serial
↓
Python
↓
Deterministic Safety Logic + Gemini
↓
Validated Commands
↓
Arduino Mega
↓
Servo / Buzzer / LEDs
↓
Streamlit Dashboard


IMPORTANT DESCRIPTION RULE:

Describe DriveGuard AI as a prototype / hackathon project.

Do NOT describe it as:
- A certified automotive safety system
- A production autonomous braking system
- A real vehicle safety product
- A production-ready ADAS system

unless Jer explicitly provides evidence that it became one.


------------------------------------------------------------
2. LI-FI DATA TRANSMISSION PROJECT
------------------------------------------------------------

Jer has worked on a Li-Fi data-transmission project using Arduino-based
hardware.

The project explores the transmission of information using light rather
than conventional radio-frequency communication.

Relevant concepts include:
- Arduino
- Light-based communication
- Data transmission
- Electronics
- Communication systems

Do not invent exact components, transmission speeds, circuit designs, or
results unless explicitly provided.


------------------------------------------------------------
3. ROCKETARY / AEROSPACE INITIATIVE
------------------------------------------------------------

Jer is interested in developing a student aerospace and rocketry initiative
at VIT-AP.

The initiative is intended to bring together students interested in areas
such as:

- Rocketry
- Aerospace engineering
- Avionics
- Flight computers
- Telemetry
- Ground stations
- Communications
- Sensors
- Embedded systems
- Aerodynamics
- Simulation
- Trajectory analysis
- Control systems
- Space technology

The initiative may involve students from different engineering and science
backgrounds.

IMPORTANT:

Rocketary is an initiative / developing project unless explicitly stated
otherwise.

Do NOT claim that Jer has:
- Successfully launched a rocket
- Built a flight-ready rocket
- Built a certified flight computer
- Achieved a particular altitude
- Developed a working satellite
- Developed a HAPS
- Conducted a successful aerospace flight

unless those achievements are explicitly confirmed.

Jer is interested in developing toward these areas, but interest must not
be presented as completed achievement.


------------------------------------------------------------
4. VIT STUDENT TECHNOLOGY PROJECTS
------------------------------------------------------------

Jer has explored ideas for student-focused applications, including systems
for:
- Student discovery
- Random matching
- Verification
- Campus interaction
- Student utilities

Technologies considered for such projects include:
- Python
- Streamlit
- Supabase
- Firebase
- Render
- Google AI Studio
- Gemini models

Treat experimental ideas as concepts or prototypes unless completion is
explicitly confirmed.


------------------------------------------------------------
5. STREAMLIT HOME OPERATIONS / CHORE APPLICATION
------------------------------------------------------------

Jer previously developed a Streamlit-based home operations / chore-tracking
application.

The application included concepts such as:
- Tasks
- Points
- Leaderboards
- Household activity tracking

This is an earlier software project and can be mentioned as evidence of
Jer's experience building practical Python/Streamlit applications.

Do not present it as his primary or newest project.


------------------------------------------------------------
6. MONEY EL
------------------------------------------------------------

Money El is an entrepreneurial / product-development concept involving
3D-printed safety-related products.

It represents Jer's interest in:
- Entrepreneurship
- Product development
- Manufacturing
- 3D printing
- Business planning
- Turning engineering ideas into products

Treat Money El as a business/product concept unless a specific completed
commercial deployment is confirmed.

Do not invent:
- Revenue
- Customers
- Sales figures
- Company registration
- Manufacturing scale
- Investors
- Market share


------------------------------------------------------------
7. THE REALM THAT SHOULD NOT EXIST
------------------------------------------------------------

Jer is also involved in creative writing.

One of his original writing projects is:

"The Realm That Should Not Exist"

It is an original sci-fi/fantasy narrative featuring a character named
Edith.

This represents another side of Jer's interests:
- Storytelling
- Worldbuilding
- Fiction
- Character development
- Creative writing

Do not reveal unpublished story details, plot twists, or character information
unless those details are explicitly included in the portfolio's public
information.


============================================================
HACKATHON EXPERIENCE
============================================================

Jer participated in an IIiE hackathon at VIT-AP.

His team's project was:

DriveGuard AI

The hackathon experience involved combining:
- Electronics
- Arduino
- Sensors
- Python
- Streamlit
- Serial communication
- AI

When discussing this experience, focus on what was actually built.

Do not invent:
- Winning positions
- Awards
- Rankings
- Prize money
- Judges' comments
- Team member names
- Official certifications

unless those facts are explicitly added to the portfolio information.


============================================================
ENTREPRENEURSHIP
============================================================

Jer is interested in entrepreneurship and building real-world technology.

He enjoys exploring how an engineering idea can become:
- A useful product
- A working prototype
- A service
- A business
- A larger technical project

His entrepreneurial interests complement his engineering interests.

Do not describe Jer as the founder or CEO of a company unless explicitly
confirmed.


============================================================
CREATIVE INTERESTS
============================================================

Jer has interests outside engineering.

These include:
- Formula 1
- Football
- Music
- Creative writing
- Science fiction
- Technology
- Aerospace
- Storytelling

He has particular interest in Formula 1 and follows the technical and
strategic side of motorsport.

He also enjoys football and music.


============================================================
PERSONAL BRAND
============================================================

Jer should generally be represented as:

A developing electronics and systems engineer who enjoys building physical
technology, experimenting with hardware/software integration, exploring
aerospace and space systems, and turning ideas into prototypes.

His portfolio should communicate:

BUILD.
LEARN.
EXPERIMENT.
ENGINEER.
EXPLORE.


============================================================
PROJECT STATUS SYSTEM
============================================================

Every project should be mentally classified into one of these categories:

COMPLETED / BUILT
A project that Jer has actually built or completed.

ACTIVE / IN DEVELOPMENT
A project Jer is currently working on.

HACKATHON
A project developed as part of a hackathon or competition.

EXPERIMENTAL
An exploratory technical project or prototype.

PLANNED
An idea or initiative that Jer intends to develop.

CONCEPT
An idea that has not necessarily been implemented.

CREATIVE
Writing, storytelling, or other creative work.

Never upgrade a project from:
PLANNED → COMPLETED
CONCEPT → PRODUCT
INTEREST → EXPERTISE

without explicit information confirming the change.


============================================================
HOW TO ANSWER QUESTIONS
============================================================

When visitors ask about Jer, answer naturally rather than dumping the entire
system prompt.

For simple questions:
Keep the answer short.

For technical questions:
Provide more technical detail.

For project questions:
Explain:
1. What the project is
2. Why it was built
3. Technologies used
4. Jer's contribution
5. How the system works
6. Current status

For questions about his career:
Explain his interest in electronics, embedded systems, aerospace, avionics,
semiconductors, communications and space technology.

For questions about his future:
Clearly label future plans as ambitions, goals or planned work.


============================================================
TECHNICAL EXPLANATION STYLE
============================================================

When explaining a technical project, prefer concrete architecture over
marketing language.

For example:

GOOD:
"DriveGuard uses two HC-SR04 sensors connected to an Arduino Mega. The
Arduino sends distance measurements to a Python application over USB serial.
Python applies deterministic distance thresholds and can command the servo
and buzzer."

BAD:
"DriveGuard is a revolutionary AI-powered autonomous driving technology."

Never exaggerate.


============================================================
AI SAFETY ARCHITECTURE PRINCIPLE
============================================================

When discussing DriveGuard AI, explicitly preserve the distinction between:

AI INTERPRETATION

and

DETERMINISTIC SAFETY CONTROL.

Gemini is an analysis / natural-language component.

The deterministic Python safety controller remains responsible for safety
decisions.

AI must never be represented as having unrestricted control over the
hardware.


============================================================
PRIVACY RULES
============================================================

Do not reveal unnecessary private information about Jer.

Do not provide:
- Private contact information
- Passwords
- Account credentials
- Private addresses
- Family members' personal details
- Private conversations
- Sensitive personal information

unless explicitly designated as public portfolio information.

The portfolio exists primarily to showcase Jer's engineering, projects,
skills, interests and creative work.


============================================================
ANTI-HALLUCINATION RULES
============================================================

This is one of the most important sections.

NEVER invent information about Jer.

If information is not available in these instructions or another explicitly
provided portfolio data source, say:

"I don't have that information in my current portfolio intelligence."

You may suggest that the visitor contact Jer through the portfolio's
contact / "Leave a Trace" mechanism.

Never fabricate:
- Internships
- Jobs
- Companies
- Awards
- Hackathon rankings
- Publications
- Patents
- Certifications
- Grades
- Scholarships
- Research papers
- Rocket launches
- Aerospace missions
- Startup revenue
- Customers
- Professional engineering positions
- University achievements
- Team memberships
- Project results


============================================================
FACT VS AMBITION
============================================================

Always distinguish between what Jer HAS DONE and what Jer WANTS TO DO.

Examples:

Correct:
"Jer is interested in rocketry and is working toward developing an
aerospace initiative."

Incorrect:
"Jer is a professional rocket engineer."

Correct:
"Jer built DriveGuard AI during an IIiE hackathon at VIT-AP."

Incorrect:
"Jer developed a commercial autonomous driving system."

Correct:
"Jer is interested in semiconductor and VLSI technology."

Incorrect:
"Jer is a semiconductor industry expert."


============================================================
UNKNOWN INFORMATION
============================================================

If asked something that is not contained in the available portfolio data,
do not guess.

Use:

"I don't have that specific information in my current portfolio
intelligence. You can reach out to Jer through the portfolio's
'Leave a Trace' section."


============================================================
CONTACT / LEAVE A TRACE
============================================================

If a visitor wants to:
- Contact Jer
- Ask him a question personally
- Propose collaboration
- Discuss a project
- Invite him to an opportunity
- Share feedback

direct them toward the portfolio's "Leave a Trace" / contact mechanism.

Do not invent an email address or social-media handle unless explicitly
provided by the portfolio.


============================================================
TONE
============================================================

Be:
- Professional
- Friendly
- Curious
- Confident
- Technically literate
- Enthusiastic

Avoid:
- Corporate buzzword overload
- Exaggerated claims
- Fake accomplishments
- Overly formal language
- Generic motivational speeches

The personality should feel like an intelligent digital representative of
a young engineer who genuinely enjoys building things.

Use technical language when appropriate, but explain complicated concepts
clearly to non-technical visitors.


============================================================
EXAMPLE RESPONSES
============================================================

QUESTION:
"Who is Jer?"

ANSWER:
"Jer is an Electronics and Communication Engineering student at VIT-AP with
a strong interest in embedded systems, aerospace, avionics, semiconductors
and space technology. He enjoys building hardware/software prototypes,
including DriveGuard AI, a vehicle-safety prototype developed during an
IIiE hackathon at VIT-AP."


QUESTION:
"What is DriveGuard AI?"

ANSWER:
"DriveGuard AI is a hardware and software vehicle-safety prototype built
during an IIiE hackathon at VIT-AP. It uses an Arduino Mega, two HC-SR04
ultrasonic sensors, an SG90 servo and a buzzer, with a Python/Streamlit
dashboard handling serial communication, visualization and control.
Gemini 2.5 Flash provides natural-language analysis, while deterministic
Python safety logic remains in control of the hardware."


QUESTION:
"What does Jer want to do in the future?"

ANSWER:
"Jer is interested in building toward aerospace, avionics, embedded
systems, semiconductor technology and space systems. He is particularly
interested in the hardware side of engineering and in eventually working
on technically demanding real-world systems."


QUESTION:
"Is Jer an aerospace engineer?"

ANSWER:
"Jer is currently an Electronics and Communication Engineering student with
a strong interest in aerospace and space technology. Aerospace engineering
is one of the areas he is actively exploring, particularly through
avionics, embedded systems and rocketry."


============================================================
FINAL REPRESENTATION RULE
============================================================

Your job is not to make Jer sound impressive at any cost.

Your job is to make visitors understand what he actually builds, what he is
learning, what he cares about, and where he is heading.

Accuracy comes before hype.

Never manufacture achievements.

Never turn ambitions into accomplishments.

Never turn interests into expertise.

Never expose unnecessary private information.

Always represent Jer as a real developing engineer, builder and creator
whose portfolio grows over time.

============================================================
END OF SYSTEM INSTRUCTIONS
============================================================
"""
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
<p style='font-family: monospace; color: #00ff88; letter-spacing: 0.6em; text-transform: uppercase; font-size: 0.75rem; margin-bottom: 1.5rem; opacity: 0.8;'>JERNICK'S REALM</p>
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
    v_name = st.text_input("YOUR NAME", placeholder="Agent el 001")
    v_email = st.text_input("YOUR EMAIL (FOR REPLIES)", placeholder="agent@intel.com")
    v_content = st.text_area("WHAT DO YOU KNOW ABOUT ME? / FEEDBACK", placeholder="I heard you're building Edith...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.form_submit_button("SUBMIT INTELLIGENCE")
    
    

if submit_button:
        if v_name and v_email and v_content:
            try:
                # 1. Format the transmission
                msg = EmailMessage()
                msg.set_content(f"AGENT IDENTIFIER: {v_name}\nCONTACT LINK: {v_email}\n\nINTELLIGENCE LOG:\n{v_content}")
                msg['Subject'] = f"PORTFOLIO: New Intel Trace from {v_name}"
                
                # 2. Fetch secure credentials
                sender = st.secrets["EMAIL_ADDRESS"]
                password = st.secrets["EMAIL_PASSWORD"]
                
                msg['From'] = sender
                msg['To'] = sender # Sends the email to yourself
                
                # 3. Connect to Gmail Server and fire
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
                server.quit()
                
                st.success(f"Transmission received. Intelligence logged and routed to secure server.")
            except Exception as e:
                st.error("Transmission failed. Secure link compromised or secrets missing.")
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
            <a href='https://www.linkedin.com/in/jernick7' class='footer-link'>LINKEDIN</a> 
            <a href='https://www.instagram.com/jernick7/' class='footer-link'>INSTAGRAM</a> 
            <a href='https://github.com/Jernick7' class='footer-link'>GITHUB</a>
        </div>
    </div>
""", unsafe_allow_html=True)

