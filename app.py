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

st.set_page_config(
    page_title="Syndesi Concierge",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── MODERN UI STYLING ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* Global Reset */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #F8F7F4 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.main .block-container {
    padding-top: 2rem !important;
    max-width: 850px !important;
}

/* Hide Streamlit elements */
[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }

/* Chat Bubbles */
.user-msg {
    background: #1C1917;
    color: white;
    padding: 14px 20px;
    border-radius: 20px 20px 4px 20px;
    margin-bottom: 20px;
    align-self: flex-end;
    max-width: 80%;
    margin-left: auto;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.bot-container {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
}

.bot-avatar {
    width: 36px; height: 36px;
    background: #E8651A;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 10px rgba(232, 101, 26, 0.2);
}

.bot-msg {
    background: white;
    color: #1C1917;
    padding: 16px 20px;
    border-radius: 4px 22px 22px 22px;
    border: 1px solid #EEEBE6;
    max-width: 85%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    line-height: 1.6;
}

/* Expert Cards */
.expert-card {
    background: white;
    border-radius: 24px;
    padding: 24px;
    margin: 16px 0 16px 48px;
    border: 1px solid #EAE8E4;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.expert-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.04);
}

.confidence-badge {
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Floating Input Bar */
.stTextInput > div > div > input {
    border-radius: 100px !important;
    padding: 24px 28px !important;
    border: 1px solid #E0DDD7 !important;
    background: white !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.04) !important;
    font-size: 16px !important;
}

.send-btn-container {
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 800px;
    padding: 0 20px;
    z-index: 1000;
}

/* Custom Buttons */
.stButton > button {
    border-radius: 100px !important;
    border: 1px solid #E0DDD7 !important;
    background: white !important;
    transition: all 0.2s !important;
    color: #444 !important;
    font-weight: 500 !important;
}
.stButton > button:hover {
    border-color: #E8651A !important;
    color: #E8651A !important;
    background: #FFF9F5 !important;
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
    except Exception as e:
        return None, str(e)

# ── SESSION STATE ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False

# ── HEADER ──
st.markdown(f"""
    <div style="text-align: center; margin-bottom: 40px;">
        <img src="https://www.syndesi.network/favicon.ico" width="40" style="margin-bottom:10px">
        <h2 style="font-weight: 700; color: #1C1917; margin-bottom: 4px;">Syndesi Concierge</h2>
        <p style="color: #78716C; font-size: 14px;">Intelligent Expert Matching Network</p>
    </div>
""", unsafe_allow_html=True)

# ── CHAT DISPLAY ──
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        # Check if it's a result or a simple text message
        content = msg["content"]
        if isinstance(content, dict) and content.get("type") == "result":
            res = content["result"]
            st.markdown(f"""
                <div class="bot-container">
                    <div class="bot-avatar">🔶</div>
                    <div class="bot-msg">{res.get('reply')}</div>
                </div>
            """, unsafe_allow_html=True)
            
            for m in res.get("matches", []):
                conf = m.get("confidence", 0)
                color = "#16a34a" if conf > 85 else "#E8651A"
                st.markdown(f"""
                    <div class="expert-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                            <div>
                                <span class="confidence-badge" style="background: {color}15; color: {color};">{conf}% Match</span>
                                <h3 style="margin: 8px 0 2px 0; font-size: 18px; font-weight: 700;">{m.get('name')}</h3>
                                <p style="color: #E8651A; font-weight: 600; font-size: 13px; margin:0;">{m.get('speciality')} @ {m.get('company')}</p>
                            </div>
                        </div>
                        <p style="color: #57534E; font-size: 14px; line-height: 1.5; margin-bottom: 20px;">{m.get('reason')}</p>
                        <div style="display: flex; gap: 10px;">
                            <a href="mailto:{m.get('email')}" style="text-decoration: none; flex: 1;">
                                <div style="background: #1C1917; color: white; text-align: center; padding: 10px; border-radius: 12px; font-size: 13px; font-weight: 500;">Email Specialist</div>
                            </a>
                            <div style="background: #F4F2EE; color: #1C1917; text-align: center; padding: 10px; border-radius: 12px; font-size: 13px; font-weight: 500; flex: 1;">{m.get('phone')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="bot-container">
                    <div class="bot-avatar">🔶</div>
                    <div class="bot-msg">{content}</div>
                </div>
            """, unsafe_allow_html=True)

# ── INPUT LOGIC ──
st.markdown('<div class="send-btn-container">', unsafe_allow_html=True)
user_query = st.text_input("How can we help?", placeholder="e.g. I need help with an HMRC tax investigation...", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if user_query and not st.session_state.processing:
    st.session_state.processing = True
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Process
    df, err = load_professionals()
    if not err:
        summary = "\n".join([" | ".join(map(str, row)) for row in df.values])
        prompt = f"Match this query: '{user_query}' against these pros: {summary}. Return JSON: {{'reply': '...', 'matches': [{{'name': '...', 'confidence': 90, 'reason': '...'}}]}}"
        raw_json, call_err = gemini_call(prompt)
        
        if not call_err:
            res_data = json.loads(raw_json)
            st.session_state.messages.append({"role": "assistant", "content": {"type": "result", "result": res_data}})
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {call_err}"})
    
    st.session_state.processing = False
    st.rerun()

# ── INITIAL MESSAGE ──
if not st.session_state.messages:
    st.session_state.messages.append({"role": "assistant", "content": "Welcome back. I'm connected to the Syndesi network. Describe your legal or business challenge, and I'll find the right specialist for you."})
    st.rerun()
