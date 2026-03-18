import streamlit as st
import pandas as pd
import json
import urllib.request
import urllib.error
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mjEM2jJ69Qc0m5R1mdw6wjsPhRJ0mscNhMJLwNdRM7Q/export?format=csv"

st.set_page_config(
    page_title="Syndesi — Find an Expert",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
section.main, .main .block-container,
[data-testid="stMainBlockContainer"] {
  background: #EFEDE9 !important;
  font-family: 'Inter', sans-serif !important;
  color: #1C1917 !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu, footer { display: none !important; }

[data-testid="stSidebar"] { display: none !important; }

.block-container,
[data-testid="stMainBlockContainer"] {
  padding: 0 !important;
  max-width: 100% !important;
}

[data-testid="stColumn"] { background: transparent !important; }

.stTextInput label, .stTextArea label { display: none !important; }

.stTextInput > div, .stTextInput > div > div { background: transparent !important; }

.stTextInput > div > div > input {
  background: #FFFFFF !important;
  border: 1.5px solid #DDD8D2 !important;
  border-radius: 28px !important;
  color: #1C1917 !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 15px !important;
  caret-color: #E8651A !important;
  padding: 14px 20px !important;
  height: 52px !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
.stTextInput > div > div > input:focus {
  border-color: #E8651A !important;
  box-shadow: 0 0 0 3px rgba(232,101,26,0.12) !important;
  outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #A8A29E !important; }

.send-btn .stButton > button {
  background: #E8651A !important;
  color: #fff !important;
  border: none !important;
  border-radius: 50% !important;
  width: 52px !important; height: 52px !important;
  padding: 0 !important; font-size: 20px !important;
  min-width: 52px !important; max-width: 52px !important;
  box-shadow: 0 3px 12px rgba(232,101,26,0.4) !important;
}
.send-btn .stButton > button:hover {
  background: #F07030 !important;
  transform: scale(1.05) !important;
}

.chip-btn .stButton > button {
  background: #FFFFFF !important;
  color: #57534E !important;
  border: 1.5px solid #DDD8D2 !important;
  border-radius: 100px !important;
  width: auto !important; height: auto !important;
  min-width: auto !important; max-width: none !important;
  padding: 8px 18px !important;
  font-size: 13.5px !important; font-weight: 500 !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}
.chip-btn .stButton > button:hover {
  background: #FDF0E8 !important;
  border-color: #E8651A !important;
  color: #E8651A !important;
  transform: translateY(-1px) !important;
}

[data-testid="stSpinner"] > div > div { border-top-color: #E8651A !important; }
</style>
""", unsafe_allow_html=True)

# ── HELPERS ──
def pad():
    _, c, _ = st.columns([0.12, 0.76, 0.12])
    return c

def load_professionals():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip() for c in df.columns]
        df = df.dropna(how="all")
        return df, None
    except Exception as e:
        return None, str(e)

def get_summary(df):
    lines = []
    for _, row in df.iterrows():
        parts = [str(row.get(c,"")).strip() for c in df.columns
                 if str(row.get(c,"")).strip() and str(row.get(c,"")).lower() != "nan"]
        if parts:
            lines.append(" | ".join(parts))
    return "\n".join(lines)

def gemini_call(prompt):
    if not GEMINI_API_KEY:
        return None, "No API key found in Secrets"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode())
        raw = res["candidates"][0]["content"]["parts"][0]["text"]
        clean = raw.replace("```json","").replace("```","").strip()
        if "{" in clean:
            clean = clean[clean.index("{"):clean.rindex("}")+1]
        return clean, None
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        return None, f"HTTP {e.code}: {body_text[:200]}"
    except Exception as e:
        return None, str(e)

def find_experts(query, prof_summary):
    prompt = f"""You are the Syndesi concierge — a warm professional assistant helping find the right specialist.

User said: "{query}"

Available professionals (one per line):
{prof_summary}

1. Understand what they ACTUALLY need
2. Write a warm natural 1-sentence reply
3. Pick TOP 3 most suitable professionals
4. Give each a confidence score 0-100 and short specific reason

Return ONLY valid JSON, absolutely no other text:
{{
  "reply": "Warm 1-sentence reply",
  "expert_type": "Type of specialist e.g. Tax Specialist",
  "matches": [
    {{
      "name": "Exact name",
      "company": "Exact company",
      "speciality": "Exact speciality",
      "email": "Exact email",
      "phone": "Exact phone",
      "confidence": 92,
      "reason": "Why this person fits"
    }}
  ]
}}"""

    raw, err = gemini_call(prompt)
    if err:
        return None, err
    try:
        return json.loads(raw), None
    except Exception as e:
        return None, f"JSON parse error: {e} — Raw: {raw[:200]}"

def refine_experts(original_query, prev_result, refinement, prof_summary):
    prompt = f"""You are the Syndesi concierge.

Original query: "{original_query}"
User refinement: "{refinement}"

Previous matches:
{json.dumps(prev_result.get("matches",[]), indent=2)}

All professionals:
{prof_summary}

Apply refinement and return updated top 3.

Return ONLY valid JSON:
{{
  "reply": "Warm 1-sentence acknowledgement",
  "expert_type": "Updated expert type",
  "matches": [
    {{
      "name": "Name", "company": "Company",
      "speciality": "Speciality", "email": "Email",
      "phone": "Phone", "confidence": 85,
      "reason": "Why this fits the refined request"
    }}
  ]
}}"""

    raw, err = gemini_call(prompt)
    if err:
        return None, err
    try:
        return json.loads(raw), None
    except Exception as e:
        return None, f"JSON parse error: {e}"

def conf_col(s):
    if s >= 85: return "#16a34a","#f0fdf4","#bbf7d0"
    if s >= 65: return "#d97706","#fffbeb","#fde68a"
    return "#dc2626","#fef2f2","#fecaca"

def bot_bubble(text, extra=""):
    return f"""
    <div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:14px">
      <div style="width:34px;height:34px;background:#E8651A;border-radius:50%;flex-shrink:0;
                  display:flex;align-items:center;justify-content:center;margin-top:2px">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="5.5" r="2.5" fill="white"/>
          <circle cx="5.5" cy="18.5" r="2.5" fill="white" opacity="0.75"/>
          <circle cx="18.5" cy="18.5" r="2.5" fill="white" opacity="0.75"/>
          <line x1="12" y1="8" x2="5.5" y2="16" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
          <line x1="12" y1="8" x2="18.5" y2="16" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
        </svg>
      </div>
      <div style="background:#FFFFFF;border-radius:6px 20px 20px 20px;
                  padding:14px 18px;box-shadow:0 1px 4px rgba(0,0,0,0.08);max-width:82%">
        <p style="font-size:14.5px;color:#1C1917;margin:0;line-height:1.6">{text}</p>
        {extra}
      </div>
    </div>"""

SUGGESTIONS = [
    "I need an HMRC specialist",
    "Help selling my business",
    "Unfair dismissal advice",
    "Landlord dispute",
    "Setting up a company",
    "Can't pay my debts",
]

# ── STATE ──
for k, v in [("messages",[]),("last_result",None),("last_query",""),
              ("awaiting_refine",False),("processing",False),("debug_info","")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════
# TOP BAR
# ══════════════════════════════════════════
st.markdown("""
<div style="background:#FFFFFF;border-bottom:1px solid #E7E4DF;padding:0 24px;
            height:64px;display:flex;align-items:center;justify-content:space-between;
            position:sticky;top:0;z-index:100;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
  <div style="display:flex;align-items:center;gap:12px">
    <div style="width:40px;height:40px;background:#E8651A;border-radius:12px;
                display:flex;align-items:center;justify-content:center;flex-shrink:0">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="5.5" r="2.5" fill="white"/>
        <circle cx="5.5" cy="18.5" r="2.5" fill="white" opacity="0.75"/>
        <circle cx="18.5" cy="18.5" r="2.5" fill="white" opacity="0.75"/>
        <line x1="12" y1="8" x2="5.5" y2="16" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
        <line x1="12" y1="8" x2="18.5" y2="16" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
        <line x1="5.5" y1="18.5" x2="18.5" y2="18.5" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
      </svg>
    </div>
    <div>
      <p style="font-size:15px;font-weight:700;color:#1C1917;margin:0;letter-spacing:-0.01em">Syndesi</p>
      <p style="font-size:11.5px;color:#A8A29E;margin:0">Expert matching · Internal</p>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:7px">
    <div style="width:8px;height:8px;background:#22c55e;border-radius:50%"></div>
    <span style="font-size:12.5px;color:#78716C;font-weight:500">Online</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# DEBUG PANEL — shows exact errors
# ══════════════════════════════════════════
if st.session_state.debug_info:
    with pad():
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        with st.expander("🔧 Debug info (share this if something's wrong)", expanded=True):
            st.code(st.session_state.debug_info)

# ══════════════════════════════════════════
# CHAT AREA
# ══════════════════════════════════════════
st.markdown("<div style='max-width:760px;margin:0 auto;padding:28px 20px 130px'>", unsafe_allow_html=True)

# Welcome
if not st.session_state.messages:
    st.markdown(bot_bubble(
        "Hi! I'm the Syndesi concierge 👋",
        "<p style='font-size:14px;color:#78716C;margin:6px 0 0;line-height:1.65'>"
        "Describe your situation in plain English — no jargon needed. "
        "I'll identify what kind of specialist you need and find the best matches from our network."
        "</p>"
    ), unsafe_allow_html=True)

    st.markdown("""
    <div style="padding-left:46px;margin-bottom:10px">
      <p style="font-size:11px;color:#A8A29E;margin:0 0 10px;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em">Quick suggestions</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='padding-left:46px'><div class='chip-btn'>", unsafe_allow_html=True)
    cc = st.columns(3, gap="small")
    for i, sug in enumerate(SUGGESTIONS):
        with cc[i % 3]:
            if st.button(sug, key=f"sug_{i}"):
                st.session_state.messages.append({"role":"user","content":sug})
                st.session_state.last_query = sug
                st.session_state.last_result = None
                st.session_state.awaiting_refine = False
                st.session_state.processing = True
                st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)

# Messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;margin-bottom:14px">
          <div style="background:#E8651A;color:#fff;border-radius:20px 6px 20px 20px;
                      padding:12px 18px;max-width:75%;
                      box-shadow:0 2px 6px rgba(232,101,26,0.3)">
            <p style="font-size:14.5px;margin:0;line-height:1.55">{msg["content"]}</p>
          </div>
        </div>""", unsafe_allow_html=True)

    elif msg["role"] == "assistant":
        c = msg["content"]

        if c.get("type") == "result":
            result = c["result"]
            reply = result.get("reply","Here are your best matches:")
            expert_type = result.get("expert_type","")
            matches = result.get("matches",[])

            st.markdown(bot_bubble(
                reply,
                f"<div style='margin-top:8px;display:inline-flex;align-items:center;gap:6px;"
                f"padding:4px 12px;background:#FDF0E8;border-radius:100px'>"
                f"<div style='width:6px;height:6px;background:#E8651A;border-radius:50%'></div>"
                f"<span style='font-size:11.5px;color:#E8651A;font-weight:600'>{expert_type}</span></div>"
            ), unsafe_allow_html=True)

            rank_labels = ["Best match","Strong alternative","Also consider"]
            for i, m in enumerate(matches[:3]):
                conf = int(m.get("confidence",80))
                tc, bg, bc = conf_col(conf)
                rl = rank_labels[i] if i < 3 else f"Match {i+1}"

                st.markdown(f"""
                <div style="padding-left:46px;margin-bottom:10px">
                  <div style="background:#FFFFFF;border-radius:16px;padding:18px 20px;
                              box-shadow:0 1px 6px rgba(0,0,0,0.08);
                              border:1.5px solid #F0ECE8;position:relative;overflow:hidden">
                    <div style="position:absolute;top:0;left:0;bottom:0;width:4px;
                                background:{tc};border-radius:16px 0 0 16px"></div>
                    <div style="display:flex;justify-content:space-between;
                                align-items:flex-start;margin-bottom:12px">
                      <div style="flex:1">
                        <div style="display:inline-block;padding:2px 10px;background:{bg};
                                    border:1px solid {bc};border-radius:100px;margin-bottom:8px">
                          <span style="font-size:10.5px;font-weight:600;color:{tc};letter-spacing:0.04em">
                            {rl.upper()}
                          </span>
                        </div>
                        <p style="font-size:17px;font-weight:700;color:#1C1917;margin:0 0 3px;
                                   letter-spacing:-0.01em">{m.get("name","")}</p>
                        <p style="font-size:13px;color:#78716C;margin:0">
                          {m.get("company","")}
                          <span style="color:#D4CDC6;margin:0 5px">·</span>
                          <span style="color:#E8651A;font-weight:500">{m.get("speciality","")}</span>
                        </p>
                      </div>
                      <div style="text-align:center;flex-shrink:0;margin-left:16px">
                        <div style="width:52px;height:52px;border-radius:50%;
                                    background:{bg};border:2px solid {bc};
                                    display:flex;flex-direction:column;
                                    align-items:center;justify-content:center">
                          <p style="font-size:16px;font-weight:800;color:{tc};margin:0;line-height:1">{conf}%</p>
                        </div>
                        <p style="font-size:10px;color:#A8A29E;margin:4px 0 0">match</p>
                      </div>
                    </div>
                    <div style="background:#F7F4F1;border-radius:10px;padding:11px 14px;margin-bottom:14px">
                      <p style="font-size:13px;color:#78716C;line-height:1.65;margin:0">{m.get("reason","")}</p>
                    </div>
                    <div style="display:flex;gap:8px;flex-wrap:wrap">
                      <a href="mailto:{m.get('email','')}?subject=Enquiry via Syndesi Network"
                         style="display:inline-flex;align-items:center;gap:7px;padding:8px 16px;
                                background:#FDF0E8;border:1.5px solid #F0D0B0;border-radius:100px;
                                text-decoration:none;font-size:13px;color:#E8651A;font-weight:500">
                        ✉ {m.get("email","")}
                      </a>
                      <span style="display:inline-flex;align-items:center;gap:7px;padding:8px 16px;
                                    background:#F7F4F1;border:1.5px solid #E7E4DF;border-radius:100px;
                                    font-size:13px;color:#78716C">
                        ☎ {m.get("phone","")}
                      </span>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

            st.markdown(bot_bubble(
                "Not quite right? Tell me more — <em>\"show me someone else\"</em>, "
                "<em>\"I need someone in Manchester\"</em>, or <em>\"more senior please\"</em>."
            ), unsafe_allow_html=True)

        elif c.get("type") == "error":
            st.markdown(f"""
            <div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:14px">
              <div style="width:34px;height:34px;background:#E8651A;border-radius:50%;flex-shrink:0;
                          display:flex;align-items:center;justify-content:center">
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="5.5" r="2.5" fill="white"/>
                  <circle cx="5.5" cy="18.5" r="2.5" fill="white" opacity="0.75"/>
                  <circle cx="18.5" cy="18.5" r="2.5" fill="white" opacity="0.75"/>
                  <line x1="12" y1="8" x2="5.5" y2="16" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
                  <line x1="12" y1="8" x2="18.5" y2="16" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
                </svg>
              </div>
              <div style="background:#FFF5F5;border:1.5px solid #FECACA;
                          border-radius:6px 20px 20px 20px;padding:12px 18px;max-width:82%">
                <p style="font-size:14px;color:#DC2626;margin:0;line-height:1.55">{c.get("text","")}</p>
              </div>
            </div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# PROCESS QUERY
# ══════════════════════════════════════════
if st.session_state.processing and st.session_state.last_query and not st.session_state.last_result:
    st.session_state.processing = False
    debug_lines = []

    # Check API key
    if not GEMINI_API_KEY:
        debug_lines.append("ERROR: GEMINI_API_KEY is empty — add it to Streamlit Secrets")
        st.session_state.debug_info = "\n".join(debug_lines)
        st.session_state.messages.append({"role":"assistant","content":{"type":"error",
            "text":"No API key found. Please add GEMINI_API_KEY to Streamlit Secrets."}})
        st.rerun()

    debug_lines.append(f"API key found: {GEMINI_API_KEY[:8]}...")

    # Load sheet
    df, sheet_err = load_professionals()
    if sheet_err:
        debug_lines.append(f"SHEET ERROR: {sheet_err}")
        debug_lines.append("Using fallback sample data instead")
        df = pd.DataFrame([
            {"Name":"Sarah Mitchell","Company":"Mitchell Tax Advisers","Speciality":"HMRC Tax Investigation","Email":"sarah@mitchelltax.co.uk","Phone":"07700 900123"},
            {"Name":"James Okonkwo","Company":"Okonkwo Legal","Speciality":"Corporate Law & Business Sales","Email":"j.okonkwo@okonkwolegal.com","Phone":"07700 900456"},
            {"Name":"Priya Sharma","Company":"Sharma Accountancy","Speciality":"VAT & HMRC Compliance","Email":"priya@sharmaaccountancy.co.uk","Phone":"07700 900789"},
            {"Name":"Tom Blackwell","Company":"Blackwell Financial","Speciality":"Financial Planning","Email":"tom@blackwellfinancial.com","Phone":"07700 900321"},
            {"Name":"Emma Clarke","Company":"Clarke Employment Law","Speciality":"Employment Law","Email":"emma@clarkelaw.co.uk","Phone":"07700 900654"},
            {"Name":"David Chen","Company":"Chen Insolvency","Speciality":"Insolvency & Debt","Email":"d.chen@cheninsolvency.com","Phone":"07700 900987"},
        ])
    else:
        debug_lines.append(f"Sheet loaded: {len(df)} rows, columns: {list(df.columns)}")

    summary = get_summary(df)
    debug_lines.append(f"Summary lines: {len(summary.splitlines())}")

    with st.spinner("Searching the network..."):
        result, err = find_experts(st.session_state.last_query, summary)

    if err:
        debug_lines.append(f"GEMINI ERROR: {err}")
        st.session_state.debug_info = "\n".join(debug_lines)
        st.session_state.messages.append({"role":"assistant","content":{"type":"error",
            "text":f"Search failed. Error: {err}"}})
    elif result and result.get("matches"):
        debug_lines.append(f"SUCCESS: {len(result['matches'])} matches found")
        st.session_state.debug_info = ""
        st.session_state.last_result = result
        st.session_state.messages.append({"role":"assistant","content":{"type":"result","result":result}})
        st.session_state.awaiting_refine = True
    else:
        debug_lines.append(f"NO MATCHES: result was {result}")
        st.session_state.debug_info = "\n".join(debug_lines)
        st.session_state.messages.append({"role":"assistant","content":{"type":"error",
            "text":"Found the network but couldn't generate matches. Please try again."}})

    st.rerun()

# ══════════════════════════════════════════
# INPUT BAR
# ══════════════════════════════════════════
st.markdown("""
<div style="position:fixed;bottom:0;left:0;right:0;
            background:linear-gradient(to top,#EFEDE9 70%,transparent);
            padding:16px 20px 24px;z-index:200">
  <div style="max-width:760px;margin:0 auto">
""", unsafe_allow_html=True)

inp_col, btn_col = st.columns([1, 0.09], gap="small")
placeholder_text = "Refine results..." if st.session_state.awaiting_refine else "Describe your situation..."

with inp_col:
    user_input = st.text_input("msg", placeholder=placeholder_text,
                               label_visibility="collapsed", key="chat_input")
with btn_col:
    st.markdown("<div class='send-btn' style='padding-top:0px'>", unsafe_allow_html=True)
    send = st.button("↑", key="send_btn")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

if send and user_input.strip():
    msg_text = user_input.strip()

    if st.session_state.awaiting_refine and st.session_state.last_result:
        st.session_state.messages.append({"role":"user","content":msg_text})
        df, _ = load_professionals()
        if df is None:
            df = pd.DataFrame()
        summary = get_summary(df)
        with st.spinner("Refining..."):
            refined, err = refine_experts(st.session_state.last_query,
                                          st.session_state.last_result, msg_text, summary)
        if refined and refined.get("matches"):
            st.session_state.last_result = refined
            st.session_state.messages.append({"role":"assistant","content":{"type":"result","result":refined}})
        else:
            st.session_state.messages.append({"role":"assistant","content":{"type":"error",
                "text":f"Couldn't refine. {err or 'Please try again.'}"}})
        st.rerun()
    else:
        st.session_state.messages.append({"role":"user","content":msg_text})
        st.session_state.last_query = msg_text
        st.session_state.last_result = None
        st.session_state.awaiting_refine = False
        st.session_state.processing = True
        st.rerun()
