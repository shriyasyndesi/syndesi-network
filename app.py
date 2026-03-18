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
LOGO_URL = "https://www.syndesi.network/syndesi_logo_white_on_orange.png" # Updated to Syndesi asset

st.set_page_config(
    page_title="Syndesi Concierge",
    page_icon="🔶",
    layout="wide",
)

# ── REFINED MODERN UI ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* Global Styles */
.stApp {
    background-color: #F9F8F6 !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }

.main-container {
    max-width: 700px;
    margin: 0 auto;
    padding: 20px 10px;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Header */
.header-area {
    text-align: center;
    margin-bottom: 40px;
    padding-top: 20px;
}
.brand-logo-img {
    width: 60px;
    margin-bottom: 12px;
    border-radius: 12px;
}

/* Chat Row Layout */
.chat-row {
    display: flex;
    margin-bottom: 20px;
    width: 100%;
    animation: fadeIn 0.3s ease-in;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.bot-row { justify-content: flex-start; }
.user-row { justify-content: flex-end; }

.bubble {
    padding: 14px 20px;
    border-radius: 20px;
    font-size: 15px;
    line-height: 1.6;
    max-width: 85%;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}
.bot-bubble {
    background: white;
    color: #1C1917;
    border: 1px solid #EEEBE6;
    border-bottom-left-radius: 4px;
}
.user-bubble {
    background: #1C1917;
    color: #FFFFFF;
    border-bottom-right-radius: 4px;
}

/* Expert Result Cards */
.expert-card {
    background: white;
    border-radius: 20px;
    padding: 24px;
    margin: 12px 0 20px 0;
    border: 1px solid #EAE8E4;
    box-shadow: 0 4px 15px rgba(0,0,0,0.02);
}
.match-badge {
    background: #FDF0E8;
    color: #E8651A;
    padding: 5px 12px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.expert-name { font-weight: 700; font-size: 18px; margin: 12px 0 4px; color: #1C1917; }
.expert-meta { color: #E8651A; font-weight: 600; font-size: 14px; margin-bottom: 12px; }
.expert-reason { color: #57534E; font-size: 14px; margin-bottom: 20px; line-height: 1.5; }

.action-btn {
    display: block;
    text-align: center;
    background: #E8651A;
    color: white !important;
    text-decoration: none;
    padding: 12px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 600;
    transition: background 0.2s;
}
.action-btn:hover { background: #D65A17; }

/* Input Bar Fix */
.stTextInput > div > div > input {
    background-color: white !important;
    border-radius: 14px !important;
    border: 1px solid #DEDAD6 !important;
    padding: 14px 20px !important;
    font-size: 15px !important;
}
</style>
""", unsafe_allow_html=True)

# ── CORE FUNCTIONS ──
def load_professionals():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip() for c in df.columns]
        return df.dropna(how="all"), None
    except Exception as e:
        return None, str(e)

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

# ── APP LAYOUT ──
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header with Logo
st.markdown(f"""
    <div class="header-area">
        <img src="{LOGO_URL}" class="brand-logo-img" onerror="this.src='https://www.syndesi.network/favicon.ico'">
        <h2 style="margin:0; color:#1C1917; font-weight:700; letter-spacing:-0.02em;">Syndesi Concierge</h2>
        <p style="color:#78716C; font-size:14px; margin-top:5px;">Intelligent Expert Matching Network</p>
    </div>
""", unsafe_allow_html=True)

# Chat Display
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
                        <span class="match-badge">{m.get('confidence')}% Match</span>
                        <div class="expert-name">{m.get('name')}</div>
                        <div class="expert-meta">{m.get('speciality')} · {m.get('company')}</div>
                        <div class="expert-reason">{m.get('reason')}</div>
                        <a href="mailto:{m.get('email')}?subject=Syndesi Concierge Referral" class="action-btn">Connect via Email</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-row bot-row"><div class="bubble bot-bubble">{content}</div></div>', unsafe_allow_html=True)

# Input area
st.write("") # Spacer
user_query = st.text_input("Describe your situation", key="user_input", placeholder="How can we help you today?", label_visibility="collapsed")

if user_query and not st.session_state.processing:
    st.session_state.processing = True
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    df, _ = load_professionals()
    summary = "\n".join([" | ".join(map(str, row)) for row in df.values])
    
    prompt = f"""Match this query: '{user_query}' against these professionals: {summary}. 
    Return ONLY valid JSON: {{'reply': 'A warm 1-sentence response', 'matches': [{{'name': '...', 'speciality': '...', 'company': '...', 'confidence': 90, 'reason': '...', 'email': '...'}}]}}"""
    
    raw_json, err = gemini_call(prompt)
    if not err:
        try:
            res_data = json.loads(raw_json)
            st.session_state.messages.append({"role": "assistant", "content": {"type": "result", "result": res_data}})
        except:
            st.session_state.messages.append({"role": "assistant", "content": "I found a match, but had a technical hiccup displaying it. Could you please try again with more detail?"})
    
    st.session_state.processing = False
    st.rerun()

# Initial Greeting
if not st.session_state.messages:
    st.session_state.messages.append({"role": "assistant", "content": "Welcome back. I'm the Syndesi Concierge. Describe your business or legal challenge, and I'll find the best specialist for you."})
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
