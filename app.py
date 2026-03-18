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

# FIX: Changed layout from "tight" to "centered"
st.set_page_config(page_title="Syndesi Concierge", page_icon="🔶", layout="centered")

# ── SMART CHAT UI ──
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    .stApp {{ background-color: #F7F7F8 !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }}
    [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none !important; }}
    
    /* Center the chat container */
    .block-container {{ max-width: 800px !important; padding-top: 2rem !important; }}

    /* Custom Message Styles */
    .chat-bubble-container {{ display: flex; gap: 12px; margin-bottom: 24px; animation: fadeIn 0.3s ease; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}

    .avatar {{
        width: 32px; height: 32px; border-radius: 6px;
        background: #E8651A; display: flex; align-items: center; justify-content: center;
        flex-shrink: 0; margin-top: 4px; overflow: hidden;
    }}
    
    .msg-content {{ font-size: 15px; line-height: 1.6; color: #374151; }}
    .user-msg-box {{
        background: #ECECF1; padding: 12px 16px; border-radius: 15px; 
        margin-left: auto; max-width: 80%; color: #1F2937; margin-bottom: 20px;
    }}

    /* Expert Card Style */
    .expert-card {{
        background: white; border: 1px solid #E5E7EB; border-radius: 12px;
        padding: 20px; margin-top: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }}
    .expert-tag {{
        background: #FFF7ED; color: #E8651A; font-weight: 700;
        font-size: 10px; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;
    }}
    .connect-btn {{
        display: inline-block; background: #E8651A; color: white !important;
        padding: 8px 16px; border-radius: 8px; text-decoration: none;
        font-size: 13px; font-weight: 600; margin-top: 12px;
    }}
</style>
""", unsafe_allow_html=True)

# ── LOGIC FUNCTIONS ──
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
    st.session_state.messages = [{"role": "assistant", "content": "Hi, I'm the Syndesi Concierge. How can I help you find an expert today?"}]

# ── HEADER ──
st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 30px; border-bottom: 1px solid #E5E7EB; padding-bottom: 15px;">
        <img src="{LOGO_URL}" width="35" style="border-radius: 5px;" onerror="this.src='https://www.syndesi.network/favicon.ico'">
        <h3 style="margin:0; color:#111827; font-weight:700;">Syndesi Concierge</h3>
    </div>
""", unsafe_allow_html=True)

# ── DISPLAY CHAT ──
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg-box">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        content = msg["content"]
        if isinstance(content, str):
            st.markdown(f"""
                <div class="chat-bubble-container">
                    <div class="avatar"><img src="{LOGO_URL}" width="20" onerror="this.src='https://www.syndesi.network/favicon.ico'"></div>
                    <div class="msg-content">{content}</div>
                </div>
            """, unsafe_allow_html=True)
        elif isinstance(content, dict) and content.get("type") == "result":
            res = content["result"]
            st.markdown(f"""
                <div class="chat-bubble-container">
                    <div class="avatar"><img src="{LOGO_URL}" width="20" onerror="this.src='https://www.syndesi.network/favicon.ico'"></div>
                    <div class="msg-content">{res.get('reply')}</div>
                </div>
            """, unsafe_allow_html=True)
            for m in res.get("matches", []):
                st.markdown(f"""
                    <div class="expert-card">
                        <span class="expert-tag">{m.get('confidence', '100')}% Match</span>
                        <div style="font-weight:700; font-size:17px; margin:8px 0 2px;">{m.get('name')}</div>
                        <div style="color:#E8651A; font-weight:600; font-size:13px; margin-bottom:10px;">{m.get('speciality')} · {m.get('company')}</div>
                        <div style="font-size:14px; color:#4B5563;">{m.get('reason')}</div>
                        <a href="mailto:{m.get('email')}?subject=Syndesi Network Inquiry" class="connect-btn">Connect with Specialist</a>
                    </div>
                """, unsafe_allow_html=True)

# ── CHAT INPUT ──
if prompt := st.chat_input("How can I help you?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# ── RESPONSE LOGIC ──
if st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Consulting the Syndesi network..."):
        df, _ = load_professionals()
        # Create a clean data summary for the AI
        summary = ""
        if df is not None:
            summary = df.to_string(index=False)
        
        ai_prompt = f"""You are the Syndesi network concierge. 
        User query: {st.session_state.messages[-1]['content']}
        Available network: {summary}
        
        Return a JSON object:
        {{
          "reply": "one warm sentence",
          "matches": [
            {{"name": "...", "speciality": "...", "company": "...", "confidence": 95, "reason": "...", "email": "..."}}
          ]
        }}
        Only return the JSON."""
        
        raw_json, err = gemini_call(ai_prompt)
        if not err:
            try:
                data = json.loads(raw_json)
                st.session_state.messages.append({"role": "assistant", "content": {"type": "result", "result": data}})
            except:
                st.session_state.messages.append({"role": "assistant", "content": "I've identified potential matches, but I'm having trouble displaying them. Could you try being a bit more specific?"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "I'm having trouble connecting to the network right now. Please try again in a moment."})
    st.rerun()
