import streamlit as st
import pandas as pd
import json
import urllib.request
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
  height: 100% !important;
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

/* Hide all streamlit widget labels */
.stTextInput label,
.stTextArea label { display: none !important; }

/* TEXT INPUT */
.stTextInput > div,
.stTextInput > div > div { background: transparent !important; }

.stTextInput > div > div > input {
  background: #FFFFFF !important;
  border: 1.5px solid #DDD8D2 !important;
  border-radius: 28px !important;
  color: #1C1917 !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 15px !important;
  font-weight: 400 !important;
  caret-color: #E8651A !important;
  padding: 14px 20px !important;
  height: 52px !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
  transition: all 0.15s ease !important;
  width: 100% !important;
}

.stTextInput > div > div > input:focus {
  border-color: #E8651A !important;
  box-shadow: 0 0 0 3px rgba(232,101,26,0.12), 0 2px 8px rgba(0,0,0,0.06) !important;
  outline: none !important;
}

.stTextInput > div > div > input::placeholder {
  color: #A8A29E !important;
}

/* SEND BUTTON */
.send-btn .stButton > button {
  background: #E8651A !important;
  color: #fff !important;
  border: none !important;
  border-radius: 50% !important;
  width: 52px !important;
  height: 52px !important;
  padding: 0 !important;
  font-size: 20px !important;
  min-width: 52px !important;
  max-width: 52px !important;
  box-shadow: 0 3px 12px rgba(232,101,26,0.4) !important;
  transition: all 0.15s ease !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  line-height: 1 !important;
}

.send-btn .stButton > button:hover {
  background: #F07030 !important;
  transform: scale(1.05) !important;
  box-shadow: 0 4px 16px rgba(232,101,26,0.5) !important;
}

.send-btn .stButton > button:active {
  transform: scale(0.97) !important;
}

/* SUGGESTION CHIPS */
.chip-btn .stButton > button {
  background: #FFFFFF !important;
  color: #57534E !important;
  border: 1.5px solid #DDD8D2 !important;
  border-radius: 100px !important;
  width: auto !important;
  height: auto !important;
  min-width: auto !important;
  max-width: none !important;
  padding: 8px 18px !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
  transition: all 0.15s ease !important;
}

.chip-btn .stButton > button:hover {
  background: #FDF0E8 !important;
  border-color: #E8651A !important;
  color: #E8651A !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 2px 8px rgba(232,101,26,0.15) !important;
}

/* SPINNER */
[data-testid="stSpinner"] > div > div {
  border-top-color: #E8651A !important;
}

/* Alerts */
[data-testid="stAlert"] {
  background: rgba(232,101,26,0.06) !important;
  border: 1px solid rgba(232,101,26,0.2) !important;
  border-radius: 12px !important;
}
[data-testid="stAlert"] p {
  color: #92400e !important;
  font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ──
def pad():
    _, c, _ = st.columns([0.15, 0.7, 0.15])
    return c

@st.cache_data(ttl=300)
def load_professionals():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip() for c in df.columns]
        # Drop completely empty rows
        df = df.dropna(how="all")
        return df
    except Exception as e:
        # Sample fallback data
        return pd.DataFrame([
            {"Name":"Sarah Mitchell","Company":"Mitchell Tax Advisers","Speciality":"HMRC Tax Investigation","Email":"sarah@mitchelltax.co.uk","Phone":"07700 900123"},
            {"Name":"James Okonkwo","Company":"Okonkwo Legal","Speciality":"Corporate Law & Business Sales","Email":"j.okonkwo@okonkwolegal.com","Phone":"07700 900456"},
            {"Name":"Priya Sharma","Company":"Sharma Accountancy","Speciality":"VAT & HMRC Compliance","Email":"priya@sharmaaccountancy.co.uk","Phone":"07700 900789"},
            {"Name":"Tom Blackwell","Company":"Blackwell Financial","Speciality":"Financial Planning & Investments","Email":"tom@blackwellfinancial.com","Phone":"07700 900321"},
            {"Name":"Emma Clarke","Company":"Clarke Employment Law","Speciality":"Employment Law & Unfair Dismissal","Email":"emma@clarkelaw.co.uk","Phone":"07700 900654"},
            {"Name":"David Chen","Company":"Chen Insolvency Partners","Speciality":"Insolvency & Debt Restructuring","Email":"d.chen@cheninsolvency.com","Phone":"07700 900987"},
            {"Name":"Rachel Foster","Company":"Foster Wealth Management","Speciality":"Pension & Retirement Planning","Email":"rachel@fosterwm.co.uk","Phone":"07700 900147"},
            {"Name":"Marcus Webb","Company":"Webb & Co Solicitors","Speciality":"Property Law & Landlord Disputes","Email":"m.webb@webbsolicitors.com","Phone":"07700 900258"},
        ])

def get_summary(df):
    lines = []
    for _, row in df.iterrows():
        parts = []
        for c in df.columns:
            val = str(row.get(c, "")).strip()
            if val and val.lower() != "nan":
                parts.append(val)
        if parts:
            lines.append(" | ".join(parts))
    return "\n".join(lines)

def gemini_call(prompt):
    if not GEMINI_API_KEY:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode())
        raw = res["candidates"][0]["content"]["parts"][0]["text"]
        return raw.replace("```json", "").replace("```", "").strip()
    except Exception as e:
        return None

def find_experts(query, prof_summary):
    prompt = f"""You are the Syndesi concierge — a warm, professional assistant helping people find the right specialist.

User said: "{query}"

Available professionals in the network (one per line):
{prof_summary}

Instructions:
1. Understand what the user ACTUALLY needs — even if described vaguely or emotionally
2. Write a warm, natural 1-sentence reply acknowledging their situation (conversational, not robotic)
3. Pick the TOP 3 most suitable professionals
4. Give each a confidence score 0-100 and a short specific reason why they match

Return ONLY valid JSON, no other text, no markdown fences:
{{
  "reply": "Warm 1-sentence acknowledgement of their situation",
  "expert_type": "Type of specialist needed e.g. HMRC Tax Specialist",
  "matches": [
    {{
      "name": "Exact name from list",
      "company": "Exact company",
      "speciality": "Exact speciality",
      "email": "Exact email",
      "phone": "Exact phone",
      "confidence": 92,
      "reason": "1-2 sentences: why specifically this person fits this situation"
    }}
  ]
}}"""

    raw = gemini_call(prompt)
    if not raw:
        return None
    # Try to extract JSON even if wrapped in text
    if "{" in raw:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        raw = raw[start:end]
    try:
        return json.loads(raw)
    except:
        return None

def refine_experts(original_query, prev_result, refinement, prof_summary):
    prompt = f"""You are the Syndesi concierge.

Original query: "{original_query}"
User wants to refine: "{refinement}"

Previous matches:
{json.dumps(prev_result.get("matches", []), indent=2)}

All available professionals:
{prof_summary}

Apply the refinement — show different people, filter by location/seniority/speciality, or show more options.

Return ONLY valid JSON:
{{
  "reply": "Warm 1-sentence acknowledgement of their refinement",
  "expert_type": "Updated expert type",
  "matches": [
    {{
      "name": "Name",
      "company": "Company",
      "speciality": "Speciality",
      "email": "Email",
      "phone": "Phone",
      "confidence": 85,
      "reason": "Why this person fits the refined request"
    }}
  ]
}}"""

    raw = gemini_call(prompt)
    if not raw:
        return None
    if "{" in raw:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        raw = raw[start:end]
    try:
        return json.loads(raw)
    except:
        return None

def conf_col(s):
    if s >= 85: return "#16a34a", "#f0fdf4", "#bbf7d0"
    if s >= 65: return "#d97706", "#fffbeb", "#fde68a"
    return "#dc2626", "#fef2f2", "#fecaca"

SUGGESTIONS = [
    "I need an HMRC specialist",
    "Help selling my business",
    "Unfair dismissal advice",
    "Landlord won't return deposit",
    "Setting up a limited company",
    "Can't pay my debts",
]

# ── INIT STATE ──
for key, default in [
    ("messages", []),
    ("last_result", None),
    ("last_query", ""),
    ("awaiting_refine", False),
    ("processing", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════
# TOP BAR
# ══════════════════════════════════════════
st.markdown("""
<div style="
  background: #FFFFFF;
  border-bottom: 1px solid #E7E4DF;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
">
  <div style="display:flex;align-items:center;gap:12px">
    <div style="
      width: 40px; height: 40px;
      background: #E8651A;
      border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0;
    ">
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
      <p style="font-size:15px;font-weight:700;color:#1C1917;margin:0;letter-spacing:-0.01em;line-height:1.2">Syndesi</p>
      <p style="font-size:11.5px;color:#A8A29E;margin:0;font-weight:400">Expert matching · Internal</p>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:7px">
    <div style="width:8px;height:8px;background:#22c55e;border-radius:50%;box-shadow:0 0 0 2px #dcfce7"></div>
    <span style="font-size:12.5px;color:#78716C;font-weight:500">Online</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# CHAT MESSAGES
# ══════════════════════════════════════════

def bot_avatar():
    return """
    <div style="width:34px;height:34px;background:#E8651A;border-radius:50%;
                flex-shrink:0;display:flex;align-items:center;justify-content:center;margin-top:2px">
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="5.5" r="2.5" fill="white"/>
        <circle cx="5.5" cy="18.5" r="2.5" fill="white" opacity="0.75"/>
        <circle cx="18.5" cy="18.5" r="2.5" fill="white" opacity="0.75"/>
        <line x1="12" y1="8" x2="5.5" y2="16" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
        <line x1="12" y1="8" x2="18.5" y2="16" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
      </svg>
    </div>"""

# Chat container
st.markdown("""
<div style="max-width:760px;margin:0 auto;padding:28px 20px 120px 20px">
""", unsafe_allow_html=True)

# Welcome message
if not st.session_state.messages:
    st.markdown(f"""
    <div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:24px">
      {bot_avatar()}
      <div style="
        background:#FFFFFF;
        border-radius:6px 20px 20px 20px;
        padding:16px 20px;
        box-shadow:0 1px 4px rgba(0,0,0,0.08);
        max-width:82%;
      ">
        <p style="font-size:15px;font-weight:600;color:#1C1917;margin:0 0 6px;line-height:1.4">
          Hi! I'm the Syndesi concierge 👋
        </p>
        <p style="font-size:14px;color:#78716C;margin:0;line-height:1.65">
          Describe your situation in plain English — no jargon needed.
          I'll identify what kind of specialist you need and find the best matches
          from our verified network.
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Suggestion chips
    st.markdown("""
    <div style="padding-left:46px;margin-bottom:8px">
      <p style="font-size:11.5px;color:#A8A29E;margin:0 0 10px;font-weight:500;
                text-transform:uppercase;letter-spacing:0.08em">Quick suggestions</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding-left:46px'>", unsafe_allow_html=True)
    st.markdown("<div class='chip-btn'>", unsafe_allow_html=True)
    chip_cols = st.columns(3, gap="small")
    for i, sug in enumerate(SUGGESTIONS):
        with chip_cols[i % 3]:
            if st.button(sug, key=f"sug_{i}"):
                st.session_state.messages.append({"role": "user", "content": sug})
                st.session_state.last_query = sug
                st.session_state.last_result = None
                st.session_state.awaiting_refine = False
                st.session_state.processing = True
                st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)

# Render messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;margin-bottom:14px">
          <div style="
            background:#E8651A;
            color:#fff;
            border-radius:20px 6px 20px 20px;
            padding:12px 18px;
            max-width:75%;
            box-shadow:0 2px 6px rgba(232,101,26,0.3);
          ">
            <p style="font-size:14.5px;margin:0;line-height:1.55;font-weight:400">{msg["content"]}</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

    elif msg["role"] == "assistant":
        c = msg["content"]

        if c.get("type") == "result":
            result = c["result"]
            reply = result.get("reply", "Here are your matches:")
            expert_type = result.get("expert_type", "")
            matches = result.get("matches", [])

            # Bot reply bubble
            st.markdown(f"""
            <div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:14px">
              {bot_avatar()}
              <div style="
                background:#FFFFFF;
                border-radius:6px 20px 20px 20px;
                padding:14px 18px;
                box-shadow:0 1px 4px rgba(0,0,0,0.08);
                max-width:82%;
              ">
                <p style="font-size:14.5px;color:#1C1917;margin:0 0 8px;line-height:1.6">{reply}</p>
                <div style="display:inline-flex;align-items:center;gap:6px;
                            padding:4px 12px;background:#FDF0E8;border-radius:100px">
                  <div style="width:6px;height:6px;background:#E8651A;border-radius:50%"></div>
                  <span style="font-size:11.5px;color:#E8651A;font-weight:600">{expert_type}</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Match cards
            rank_labels = ["Best match", "Strong alternative", "Also consider"]
            for i, m in enumerate(matches[:3]):
                conf = int(m.get("confidence", 80))
                text_col, bg_col, border_col = conf_col(conf)
                rl = rank_labels[i] if i < 3 else f"Match {i+1}"

                st.markdown(f"""
                <div style="padding-left:46px;margin-bottom:10px">
                  <div style="
                    background:#FFFFFF;
                    border-radius:16px;
                    padding:18px 20px;
                    box-shadow:0 1px 6px rgba(0,0,0,0.08);
                    border:1.5px solid #F0ECE8;
                    position:relative;
                    overflow:hidden;
                  ">
                    <div style="
                      position:absolute;top:0;left:0;bottom:0;width:4px;
                      background:{text_col};border-radius:16px 0 0 16px;
                    "></div>

                    <div style="
                      display:flex;justify-content:space-between;
                      align-items:flex-start;margin-bottom:12px;
                    ">
                      <div style="flex:1">
                        <div style="
                          display:inline-block;padding:2px 10px;
                          background:{bg_col};border:1px solid {border_col};
                          border-radius:100px;margin-bottom:8px;
                        ">
                          <span style="font-size:10.5px;font-weight:600;color:{text_col};letter-spacing:0.04em">{rl.upper()}</span>
                        </div>
                        <p style="font-size:17px;font-weight:700;color:#1C1917;margin:0 0 3px;letter-spacing:-0.01em">{m.get("name","")}</p>
                        <p style="font-size:13px;color:#78716C;margin:0">
                          {m.get("company","")}
                          <span style="color:#D4CDC6;margin:0 5px">·</span>
                          <span style="color:#E8651A;font-weight:500">{m.get("speciality","")}</span>
                        </p>
                      </div>
                      <div style="text-align:center;flex-shrink:0;margin-left:16px">
                        <div style="
                          width:52px;height:52px;border-radius:50%;
                          background:{bg_col};border:2px solid {border_col};
                          display:flex;flex-direction:column;align-items:center;justify-content:center;
                        ">
                          <p style="font-size:16px;font-weight:800;color:{text_col};margin:0;line-height:1">{conf}%</p>
                        </div>
                        <p style="font-size:10px;color:#A8A29E;margin:4px 0 0;white-space:nowrap">match</p>
                      </div>
                    </div>

                    <div style="
                      background:#F7F4F1;border-radius:10px;
                      padding:11px 14px;margin-bottom:14px;
                    ">
                      <p style="font-size:13px;color:#78716C;line-height:1.65;margin:0">{m.get("reason","")}</p>
                    </div>

                    <div style="display:flex;gap:8px;flex-wrap:wrap">
                      <a href="mailto:{m.get('email','')}?subject=Enquiry via Syndesi Network"
                         style="
                           display:inline-flex;align-items:center;gap:7px;
                           padding:8px 16px;
                           background:#FDF0E8;border:1.5px solid #F0D0B0;
                           border-radius:100px;text-decoration:none;
                           font-size:13px;color:#E8651A;font-weight:500;
                           transition:all 0.15s;
                         ">
                        ✉ {m.get("email","")}
                      </a>
                      <span style="
                        display:inline-flex;align-items:center;gap:7px;
                        padding:8px 16px;
                        background:#F7F4F1;border:1.5px solid #E7E4DF;
                        border-radius:100px;
                        font-size:13px;color:#78716C;
                      ">
                        ☎ {m.get("phone","")}
                      </span>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # Refine prompt
            st.markdown(f"""
            <div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:14px;margin-top:4px">
              {bot_avatar()}
              <div style="
                background:#FFFFFF;
                border-radius:6px 20px 20px 20px;
                padding:12px 18px;
                box-shadow:0 1px 4px rgba(0,0,0,0.08);
                max-width:82%;
              ">
                <p style="font-size:14px;color:#78716C;margin:0;line-height:1.6">
                  Not quite right? Just tell me — <em style="color:#57534E">"show me someone else"</em>,
                  <em style="color:#57534E">"I need someone in Manchester"</em>,
                  or <em style="color:#57534E">"more senior please"</em>.
                </p>
              </div>
            </div>
            """, unsafe_allow_html=True)

        elif c.get("type") == "error":
            st.markdown(f"""
            <div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:14px">
              {bot_avatar()}
              <div style="
                background:#FFF5F5;border:1.5px solid #FECACA;
                border-radius:6px 20px 20px 20px;
                padding:12px 18px;max-width:82%;
              ">
                <p style="font-size:14px;color:#DC2626;margin:0;line-height:1.55">
                  {c.get("text","Something went wrong. Please try again.")}
                </p>
              </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# PROCESS QUERY
# ══════════════════════════════════════════
needs_processing = (
    st.session_state.processing and
    st.session_state.last_query and
    not st.session_state.last_result
)

if needs_processing:
    st.session_state.processing = False
    df = load_professionals()
    summary = get_summary(df)

    with st.spinner("Searching the network..."):
        if not GEMINI_API_KEY:
            result = None
            err_text = "No API key found. Please add GEMINI_API_KEY to your Streamlit Secrets."
        else:
            result = find_experts(st.session_state.last_query, summary)
            err_text = "I had trouble searching right now. Please try again in a moment."

    if result and result.get("matches"):
        st.session_state.last_result = result
        st.session_state.messages.append({
            "role": "assistant",
            "content": {"type": "result", "result": result}
        })
        st.session_state.awaiting_refine = True
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": {"type": "error", "text": err_text}
        })
    st.rerun()

# ══════════════════════════════════════════
# INPUT BAR
# ══════════════════════════════════════════
st.markdown("""
<div style="
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: linear-gradient(to top, #EFEDE9 70%, transparent);
  padding: 16px 20px 24px;
  z-index: 200;
">
  <div style="max-width: 760px; margin: 0 auto;">
""", unsafe_allow_html=True)

inp_col, btn_col = st.columns([1, 0.09], gap="small")
placeholder_text = "Refine your results..." if st.session_state.awaiting_refine else "Describe your situation in plain English..."

with inp_col:
    user_input = st.text_input(
        "msg",
        placeholder=placeholder_text,
        label_visibility="collapsed",
        key="chat_input"
    )

with btn_col:
    st.markdown("<div class='send-btn' style='padding-top:0px'>", unsafe_allow_html=True)
    send = st.button("↑", key="send_btn")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

# Handle input
if send and user_input.strip():
    msg_text = user_input.strip()

    if st.session_state.awaiting_refine and st.session_state.last_result:
        st.session_state.messages.append({"role": "user", "content": msg_text})
        df = load_professionals()
        summary = get_summary(df)
        with st.spinner("Refining..."):
            refined = refine_experts(
                st.session_state.last_query,
                st.session_state.last_result,
                msg_text,
                summary
            )
        if refined and refined.get("matches"):
            st.session_state.last_result = refined
            st.session_state.messages.append({
                "role": "assistant",
                "content": {"type": "result", "result": refined}
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": {"type": "error", "text": "Couldn't refine results. Please try again."}
            })
        st.rerun()
    else:
        st.session_state.messages.append({"role": "user", "content": msg_text})
        st.session_state.last_query = msg_text
        st.session_state.last_result = None
        st.session_state.awaiting_refine = False
        st.session_state.processing = True
        st.rerun()
