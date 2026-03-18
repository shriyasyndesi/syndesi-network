import streamlit as st
import pandas as pd
import json
import urllib.request
import urllib.error
import os
from dotenv import load_dotenv

# ── CONFIG ──
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mjEM2jJ69Qc0m5R1mdw6wjsPhRJ0mscNhMJLwNdRM7Q/export?format=csv"
LOGO_URL = "https://www.syndesi.network/syndesi_logo_white_on_orange.png"

st.set_page_config(
    page_title="Syndesi Concierge",
    page_icon="🔶",
    layout="wide",
)

# ── WHATSAPP-STYLE MODERN UI ──
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

.stApp {{
    background-color: #F0F2F5 !important; /* WhatsApp Web background */
}}

[data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none !important; }}

.main-container {{
    max-width: 700px;
    margin: 0 auto;
    padding-bottom: 120px; /* Space for fixed input */
    font-family: 'Inter', sans-serif;
}}

/* Header */
.chat-header {{
    background: #FFFFFF;
    padding: 15px 20px;
    display: flex;
    align-items: center;
    gap: 15px;
    position: sticky;
    top: 0;
    z-index: 1000;
    border-bottom: 1px solid #E9EDEF;
    margin-bottom: 20px;
}}
.header-avatar {{
    width: 40px; height: 40px;
    border-radius: 50%;
    background: #E8651A;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden;
}}

/* Chat Bubbles */
.chat-row {{
    display: flex;
    margin-bottom: 12px;
    width: 100%;
}}
.bot-row {{ justify-content: flex-start; }}
.user-row {{ justify-content: flex-end; }}

.bubble {{
    padding: 10px 15px;
    font-size: 14.5px;
    max-width: 75%;
    position: relative;
    box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
}}
.bot-bubble {{
    background: #FFFFFF;
    color: #111B21;
    border-radius: 0 10px 10px 10px;
}}
.user-bubble {{
    background: #D9FDD3; /* WhatsApp User Green */
    color: #111B21;
    border-radius: 10px 0 10px 10px;
}}

/* Expert Results */
.expert-card {{
    background: white;
    border-radius: 12px;
    padding: 15px;
    margin-top: 10px;
    border-left: 4px solid #E8651A;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}}
.expert-name {{ font-weight: 600; font-size: 16px; margin-bottom: 2px; }}
.expert-meta {{ color: #E8651A; font-size: 13px; font-weight: 500; margin-bottom: 8px; }}

.action-btn {{
    display: inline-block;
    background: #111B21;
    color: white !important;
    padding: 8px 15px;
    border-radius: 6px;
    font-size: 13px;
    text-decoration: none;
    margin-top: 10px;
}}

/* Fixed Bottom Input Bar */
.bottom-bar {{
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: #F0F2F5;
    padding: 15px;
    border-top: 1px solid #E9EDEF;
    display: flex;
    justify-content: center;
    z-index: 2000;
}}
.input-container {{
    width: 100%;
    max-width: 700px;
    display: flex;
    gap: 10px;
    align-items: center;
}}

/* Customizing the Streamlit text_input */
.stTextInput > div > div > input {{
    border-radius: 25px !important;
    border: none !important;
    padding: 12px 20px !important;
    background: white !important;
}}

.stButton > button {{
    border-radius: 50% !important;
    width: 45px !important;
    height: 45px !important;
    padding: 0 !important;
    background-color: #E8651A !important;
    color: white !important;
    border: none !important;
}}

/* Loading Animation */
@keyframes pulse {{ 0% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.5; }} }}
.searching {{
    font-size: 13px;
    color: #667781;
    font-style: italic;
    animation: pulse 1.5s infinite;
    margin-left: 20px;
}}
</style>
""", unsafe_allow_html=True)

# ── FUNCTIONS ──
def load_professionals():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip() for c in df.columns]
        return df.dropna(how="all"), None
    except Exception as e: return None, str(e)

def gemini_call(prompt):
    if not GEMINI_API_KEY: return None, "Missing API Key"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode())
        raw = res["candidates"][0]["content"]["parts"][0]["text"]
        clean = raw.replace("```json","").replace("```","").strip()
        if "{" in clean: clean = clean[clean.index("{"):clean.rindex("}")+1]
        return clean, None
    except Exception as e: return None, str(e)

# ── SESSION STATE ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False

# ── HEADER ──
st.markdown(f"""
    <div class="chat-header">
        <div class="header-avatar">
            <img src="{LOGO_URL}" width="40" onerror="this.src='https://www.syndesi.network/favicon.ico'">
        </div>
        <div>
            <div style="font-weight: 600; color: #111B21; font-size: 16px;">Syndesi Concierge</div>
            <div style="color: #667781; font-size: 13px;">Online</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ── MESSAGES ──
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-row user-row"><div class="bubble user-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)
    else:
        content = msg["content"]
        if isinstance(content, dict) and content.get("type") == "result":
            res = content["result"]
            st.markdown(f'<div class="chat-row bot-row"><div class="bubble bot-bubble">{res.get("reply")}</div></div>', unsafe_allow_html=True)
            for m in res.get("matches", []):
                st.markdown(f"""
                    <div class="expert-card">
                        <div class="expert-name">{m.get('name')}</div>
                        <div class="expert-meta">{m.get('speciality')} · {m.get('company')}</div>
                        <div style="font-size:13.5px; color:#54656f;">{m.get('reason')}</div>
                        <a href="mailto:{m.get('email')}" class="action-btn">Message</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-row bot-row"><div class="bubble bot-bubble">{content}</div></div>', unsafe_allow_html=True)

# ── SEARCHING STATE ──
if st.session_state.processing:
    st.markdown('<div class="searching">Syndesi is searching the network...</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── BOTTOM INPUT BAR ──
with st.container():
    st.markdown('<div class="bottom-bar"><div class="input-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        u_input = st.text_input("msg", placeholder="Type a message", label_visibility="collapsed", key="user_query")
    with col2:
        send_clicked = st.button("➤", key="send_btn")
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# ── LOGIC ──
if (send_clicked or (u_input and u_input != st.session_state.get('prev_input'))) and u_input.strip() and not st.session_state.processing:
    st.session_state.prev_input = u_input
    st.session_state.processing = True
    st.session_state.messages.append({"role": "user", "content": u_input})
    
    # Force a rerun to show the "Searching" state immediately
    st.rerun()

# Processing actual API call after rerun
if st.session_state.processing and st.session_state.messages[-1]["role"] == "user":
    df, _ = load_professionals()
    summary = "\n".join([" | ".join(map(str, row)) for row in df.values])
    
    prompt = f"Match query: '{st.session_state.messages[-1]['content']}' against network: {summary}. Return JSON: {{'reply': '...', 'matches': [{{'name': '...', 'speciality': '...', 'company': '...', 'reason': '...', 'email': '...'}}]}}"
    
    raw_json, err = gemini_call(prompt)
    if not err:
        try:
            res_data = json.loads(raw_json)
            st.session_state.messages.append({"role": "assistant", "content": {"type": "result", "result": res_data}})
        except:
            st.session_state.messages.append({"role": "assistant", "content": "I couldn't process that. Try again?"})
    
    st.session_state.processing = False
    st.rerun()

# Initial Greeting
if not st.session_state.messages:
    st.session_state.messages.append({"role": "assistant", "content": "Hi! I'm the Syndesi Concierge. How can I help you today?"})
    st.rerun()
