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
SHEET_ID = "1mjEM2jJ69Qc0m5R1mdw6wjsPhRJ0mscNhMJLwNdRM7Q"
# Use gviz JSON endpoint — avoids CORS and auth issues
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

st.set_page_config(page_title="Syndesi Assistant", page_icon="🔶", layout="centered")

# ── STYLES ──
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    .stApp {{ background-color: #F7F7F8 !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }}
    [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none !important; }}
    .block-container {{ max-width: 800px !important; padding-top: 2rem !important; }}

    .chat-bubble-container {{ display: flex; gap: 12px; margin-bottom: 24px; animation: fadeIn 0.3s ease; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}

    
    .msg-content {{ font-size: 15px; line-height: 1.6; color: #374151; }}
    .user-msg-box {{
        background: #ECECF1; padding: 12px 16px; border-radius: 15px; 
        margin-left: auto; max-width: 80%; color: #1F2937; margin-bottom: 20px;
    }}

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

# ── LOAD SHEET ──
@st.cache_data(ttl=300)
def load_professionals():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip() for c in df.columns]
        df = df.dropna(how="all")
        return df, None
    except Exception as e:
        return None, str(e)

# ── GEMINI CALL ──
def gemini_call(prompt):
    if not GEMINI_API_KEY:
        return None, "Missing GEMINI_API_KEY in environment"
    
    # Try gemini-2.0-flash first, fall back to gemini-1.5-flash
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash"]
    
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        body = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024
            }
        }).encode()
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                res = json.loads(r.read().decode())
            
            raw = res["candidates"][0]["content"]["parts"][0]["text"]
            clean = raw.replace("```json", "").replace("```", "").strip()
            if "{" in clean:
                clean = clean[clean.index("{"):clean.rindex("}") + 1]
            return clean, None
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            # If model not found, try next
            if e.code == 404 or "not found" in err_body.lower():
                continue
            return None, f"HTTP {e.code}: {err_body}"
        except Exception as e:
            return None, str(e)
    
    return None, "All Gemini models failed"

# ── SESSION STATE ──
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm the Syndesi Assistant. How can I help you find an expert today?"}
    ]

# ── HEADER ──
st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 30px; border-bottom: 1px solid #E5E7EB; padding-bottom: 15px;">
        <h3 style="margin:0; color:#111827; font-weight:700;">Syndesi Assistant</h3>
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
                    <div class="msg-content">{content}</div>
                </div>
            """, unsafe_allow_html=True)
        elif isinstance(content, dict) and content.get("type") == "result":
            res = content["result"]
            st.markdown(f"""
                <div class="chat-bubble-container">
                    <div class="msg-content">{res.get('reply', '')}</div>
                </div>
            """, unsafe_allow_html=True)
            for m in res.get("matches", []):
                st.markdown(f"""
                    <div class="expert-card">
                        <span class="expert-tag">{m.get('confidence', '95')}% Match</span>
                        <div style="font-weight:700; font-size:17px; margin:8px 0 2px;">{m.get('name', '')}</div>
                        <div style="color:#E8651A; font-weight:600; font-size:13px; margin-bottom:10px;">{m.get('speciality', '')} · {m.get('company', '')}</div>
                        <div style="font-size:14px; color:#4B5563;">{m.get('reason', '')}</div>
                        <a href="mailto:{m.get('email', '')}?subject=Syndesi Network Inquiry" class="connect-btn">Connect with Specialist</a>
                    </div>
                """, unsafe_allow_html=True)

# ── CHAT INPUT ──
if prompt := st.chat_input("How can I help you?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# ── RESPONSE LOGIC ──
if st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Consulting the Syndesi network..."):
        df, err = load_professionals()

        if err:
            st.warning(f"⚠️ Could not load network data: {err}")

        summary = df.to_string(index=False) if df is not None else "No network data available."

        ai_prompt = f"""You are the Syndesi network concierge. Your job is to match users with the right expert from the Syndesi professional network.

User query: {st.session_state.messages[-1]['content']}

Available professionals in the network:
{summary}

Instructions:
- Carefully read the user's need
- Match them to the most relevant professionals from the list above
- Return ONLY a valid JSON object with no extra text or markdown

Return this exact JSON format:
{{
  "reply": "A warm, one-sentence acknowledgement of their need",
  "matches": [
    {{
      "name": "Full name from the data",
      "speciality": "Their specialty",
      "company": "Their company",
      "confidence": 95,
      "reason": "1-2 sentences explaining why they are a great match",
      "email": "Their email from the data"
    }}
  ]
}}"""

        raw_json, err = gemini_call(ai_prompt)

        if err:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"I'm having trouble reaching the AI right now ({err}). Please check your GEMINI_API_KEY and try again."
            })
        elif raw_json:
            try:
                data = json.loads(raw_json)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": {"type": "result", "result": data}
                })
            except json.JSONDecodeError:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "I found some matches but had trouble formatting the results. Please try again."
                })
        
    st.rerun()
