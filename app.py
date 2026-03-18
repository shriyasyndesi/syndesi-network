import streamlit as st
import pandas as pd
import json
import urllib.request
import os
import time
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAu1-QAC04_voOMrPDYqBO6xwW5TOQ23MA")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mjEM2jJ69Qc0m5R1mdw6wjsPhRJ0mscNhMJLwNdRM7Q/export?format=csv"

# Syndesi brand orange extracted from website: warm peach-orange #E8651A
BRAND = "#E8651A"
BRAND_LIGHT = "#F07030"
BRAND_PALE = "#FDF0E8"

st.set_page_config(
    page_title="Syndesi — Find an Expert",
    page_icon="🔶",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stAppViewBlockContainer"],
section.main,.main .block-container,[data-testid="stMainBlockContainer"]{{
  background:#F7F4F1!important;
  font-family:'Plus Jakarta Sans',sans-serif!important;
  color:#1a1a1a!important;
}}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
#MainMenu,footer,[data-testid="stStatusWidget"]{{display:none!important}}
[data-testid="stSidebar"]{{display:none!important}}
.block-container,[data-testid="stMainBlockContainer"]{{
  padding:0!important;max-width:100%!important;
}}

/* TEXT INPUT */
.stTextInput>div,.stTextInput>div>div{{background:transparent!important}}
.stTextInput>div>div>input{{
  background:#fff!important;
  border:1.5px solid #e8e0d8!important;
  border-radius:24px!important;
  color:#1a1a1a!important;
  font-family:'Plus Jakarta Sans',sans-serif!important;
  font-size:15px!important;
  font-weight:400!important;
  caret-color:{BRAND}!important;
  padding:14px 52px 14px 20px!important;
  height:52px!important;
  box-shadow:0 1px 4px rgba(0,0,0,.06)!important;
  transition:border-color .15s ease!important;
}}
.stTextInput>div>div>input:focus{{
  border-color:{BRAND}!important;
  box-shadow:0 0 0 3px rgba(232,101,26,.1)!important;
  outline:none!important;
}}
.stTextInput>div>div>input::placeholder{{color:#b0a89e!important}}
.stTextInput label{{display:none!important}}

/* SEND BUTTON */
.stButton>button{{
  background:{BRAND}!important;color:#fff!important;border:none!important;
  border-radius:50%!important;
  width:42px!important;height:42px!important;
  padding:0!important;font-size:18px!important;
  min-width:42px!important;max-width:42px!important;
  box-shadow:0 2px 8px rgba(232,101,26,.35)!important;
  transition:all .15s ease!important;
  display:flex!important;align-items:center!important;justify-content:center!important;
}}
.stButton>button:hover{{
  background:{BRAND_LIGHT}!important;
  transform:scale(1.06)!important;
  box-shadow:0 4px 12px rgba(232,101,26,.45)!important;
}}
.stButton>button:active{{transform:scale(.97)!important}}

/* CHIP BUTTONS */
.chip-btn .stButton>button{{
  background:#fff!important;color:#4a3f35!important;
  border:1.5px solid #e8e0d8!important;
  border-radius:100px!important;
  width:auto!important;height:auto!important;
  min-width:auto!important;max-width:none!important;
  padding:7px 16px!important;font-size:13px!important;font-weight:500!important;
  box-shadow:0 1px 3px rgba(0,0,0,.06)!important;
  border-radius:100px!important;
}}
.chip-btn .stButton>button:hover{{
  background:#FDF0E8!important;border-color:{BRAND}!important;
  color:{BRAND}!important;transform:none!important;box-shadow:none!important;
}}

/* REFINE CHIP */
.refine-chip .stButton>button{{
  background:transparent!important;
  color:rgba(232,101,26,.8)!important;
  border:1.5px solid rgba(232,101,26,.3)!important;
  border-radius:100px!important;
  width:auto!important;height:auto!important;
  min-width:auto!important;max-width:none!important;
  padding:6px 14px!important;font-size:12.5px!important;font-weight:500!important;
  box-shadow:none!important;
}}
.refine-chip .stButton>button:hover{{
  background:rgba(232,101,26,.06)!important;
  border-color:{BRAND}!important;color:{BRAND}!important;
  transform:none!important;box-shadow:none!important;
}}

[data-testid="stSpinner"]>div>div{{border-top-color:{BRAND}!important}}
.stSpinner>div{{color:#b0a89e!important}}
</style>
""", unsafe_allow_html=True)

# ── DATA ──
@st.cache_data(ttl=300)
def load_professionals():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame([
            {"Name":"Sarah Mitchell","Company":"Mitchell Tax Advisers","Speciality":"HMRC Tax Investigation Specialist","Email":"sarah@mitchelltax.co.uk","Phone":"07700 900123"},
            {"Name":"James Okonkwo","Company":"Okonkwo Legal","Speciality":"Corporate Law & Business Sales","Email":"j.okonkwo@okonkwolegal.com","Phone":"07700 900456"},
            {"Name":"Priya Sharma","Company":"Sharma Accountancy","Speciality":"VAT & HMRC Compliance","Email":"priya@sharmaaccountancy.co.uk","Phone":"07700 900789"},
            {"Name":"Tom Blackwell","Company":"Blackwell Financial","Speciality":"Financial Planning & Investment","Email":"tom@blackwellfinancial.com","Phone":"07700 900321"},
            {"Name":"Emma Clarke","Company":"Clarke Employment Law","Speciality":"Employment Law & Unfair Dismissal","Email":"emma@clarkelaw.co.uk","Phone":"07700 900654"},
            {"Name":"David Chen","Company":"Chen Insolvency Partners","Speciality":"Corporate Insolvency & Debt Restructuring","Email":"d.chen@cheninsolvency.com","Phone":"07700 900987"},
            {"Name":"Rachel Foster","Company":"Foster Wealth Management","Speciality":"Pension & Retirement Planning","Email":"rachel@fosterwm.co.uk","Phone":"07700 900147"},
            {"Name":"Marcus Webb","Company":"Webb & Co Solicitors","Speciality":"Property Law & Landlord Disputes","Email":"m.webb@webbsolicitors.com","Phone":"07700 900258"},
        ])

def get_summary(df):
    lines = []
    for _, row in df.iterrows():
        parts = [str(row.get(c,"")).strip() for c in df.columns
                 if str(row.get(c,"")).strip() and str(row.get(c,"")) != "nan"]
        if parts:
            lines.append(" | ".join(parts))
    return "\n".join(lines)

def gemini_call(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    body = json.dumps({"contents":[{"parts":[{"text":prompt}]}]}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode())
        raw = res["candidates"][0]["content"]["parts"][0]["text"]
        return raw.replace("```json","").replace("```","").strip()
    except:
        return None

def find_experts(query, prof_summary):
    prompt = f"""You are the Syndesi concierge — a warm, professional assistant that helps people find the right specialist.

A user has said: "{query}"

Available professionals:
{prof_summary}

Your tasks:
1. Understand what they ACTUALLY need (even if vague, emotional or technical)
2. Write a warm, concise 1-sentence reply acknowledging their situation
3. Find the TOP 3 most suitable professionals
4. For each, give a confidence score (0-100) and a clear specific reason

Return ONLY valid JSON:
{{
  "reply": "Warm 1-sentence response acknowledging their situation before showing matches",
  "understood_need": "What they actually need in plain English",
  "expert_type": "Type of specialist needed",
  "matches": [
    {{
      "name": "Exact name",
      "company": "Exact company",
      "speciality": "Exact speciality",
      "email": "Exact email",
      "phone": "Exact phone",
      "confidence": 92,
      "reason": "1-2 sentences: why specifically this person fits this situation"
    }}
  ]
}}

Return ONLY JSON. The reply should be warm and human, not robotic."""

    raw = gemini_call(prompt)
    if raw:
        try:
            return json.loads(raw)
        except:
            return None
    return None

def refine_experts(original_query, prev_result, refinement, prof_summary):
    prompt = f"""You are the Syndesi concierge.

Original query: "{original_query}"
User's follow-up: "{refinement}"

Previous matches:
{json.dumps(prev_result.get("matches",[]), indent=2)}

All professionals:
{prof_summary}

Apply the refinement (show different people, filter, more senior, different speciality, etc).

Return ONLY valid JSON:
{{
  "reply": "Warm 1-sentence acknowledgement of their refinement",
  "understood_need": "Updated understanding",
  "expert_type": "Updated expert type",
  "matches": [
    {{
      "name": "Name",
      "company": "Company",
      "speciality": "Speciality",
      "email": "Email",
      "phone": "Phone",
      "confidence": 88,
      "reason": "Why this person fits the refined request"
    }}
  ]
}}

Return ONLY JSON."""

    raw = gemini_call(prompt)
    if raw:
        try:
            return json.loads(raw)
        except:
            return None
    return None

def conf_color(s):
    if s >= 85: return "#16a34a"
    if s >= 65: return "#d97706"
    return "#dc2626"

def conf_label(s):
    if s >= 85: return "Strong match"
    if s >= 65: return "Good match"
    return "Possible match"

BRAND = "#E8651A"

# ── INIT STATE ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "awaiting_refine" not in st.session_state:
    st.session_state.awaiting_refine = False

SUGGESTIONS = [
    "HMRC back taxes",
    "Selling my business",
    "Landlord dispute",
    "Redundancy advice",
    "Setting up a company",
    "Debt problems",
]

# ══════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════
st.markdown(f"""
<div style='background:#fff;border-bottom:1px solid #ede8e3;
            padding:14px 24px;display:flex;align-items:center;
            justify-content:space-between;position:sticky;top:0;z-index:100'>
  <div style='display:flex;align-items:center;gap:12px'>
    <div style='width:36px;height:36px;background:{BRAND};border-radius:10px;
                display:flex;align-items:center;justify-content:center;flex-shrink:0'>
      <svg width='20' height='20' viewBox='0 0 24 24' fill='none'>
        <circle cx='12' cy='6'  r='2.5' fill='white'/>
        <circle cx='6'  cy='18' r='2.5' fill='white' opacity='.7'/>
        <circle cx='18' cy='18' r='2.5' fill='white' opacity='.7'/>
        <line x1='12' y1='8.5' x2='6'  y2='15.5' stroke='white' stroke-width='1.5' opacity='.6'/>
        <line x1='12' y1='8.5' x2='18' y2='15.5' stroke='white' stroke-width='1.5' opacity='.6'/>
        <line x1='6'  y1='18'  x2='18' y2='18'   stroke='white' stroke-width='1.5' opacity='.4'/>
      </svg>
    </div>
    <div>
      <p style='font-size:15px;font-weight:700;color:#1a1a1a;margin:0;letter-spacing:-.01em'>Syndesi</p>
      <p style='font-size:11px;color:#b0a89e;margin:0'>Expert matching · Internal tool</p>
    </div>
  </div>
  <div style='display:flex;align-items:center;gap:6px'>
    <div style='width:8px;height:8px;background:#22c55e;border-radius:50%'></div>
    <span style='font-size:12px;color:#6b7280'>Online</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# CHAT AREA
# ══════════════════════════════════════════
st.markdown("""
<div style='max-width:720px;margin:0 auto;padding:24px 16px 120px'>
""", unsafe_allow_html=True)

# Welcome message (always shown if no messages)
if not st.session_state.messages:
    st.markdown(f"""
    <div style='display:flex;gap:10px;margin-bottom:20px'>
      <div style='width:32px;height:32px;background:{BRAND};border-radius:50%;
                  flex-shrink:0;display:flex;align-items:center;justify-content:center;
                  margin-top:2px'>
        <svg width='16' height='16' viewBox='0 0 24 24' fill='none'>
          <circle cx='12' cy='6'  r='2.5' fill='white'/>
          <circle cx='6'  cy='18' r='2.5' fill='white' opacity='.7'/>
          <circle cx='18' cy='18' r='2.5' fill='white' opacity='.7'/>
          <line x1='12' y1='8.5' x2='6'  y2='15.5' stroke='white' stroke-width='1.5' opacity='.6'/>
          <line x1='12' y1='8.5' x2='18' y2='15.5' stroke='white' stroke-width='1.5' opacity='.6'/>
        </svg>
      </div>
      <div style='background:#fff;border-radius:4px 18px 18px 18px;
                  padding:14px 18px;box-shadow:0 1px 3px rgba(0,0,0,.08);
                  max-width:85%'>
        <p style='font-size:15px;color:#1a1a1a;margin:0 0 6px;font-weight:500'>
          Hi! I'm the Syndesi concierge.
        </p>
        <p style='font-size:14px;color:#6b7280;margin:0;line-height:1.6'>
          Tell me what's going on — in your own words, no jargon needed.
          I'll find the right specialist from our network for you.
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Suggestion chips
    st.markdown("<div style='margin-left:42px;margin-bottom:8px'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:11.5px;color:#b0a89e;margin:0 0 8px'>Quick suggestions:</p>", unsafe_allow_html=True)
    chip_cols = st.columns(3, gap="small")
    st.markdown("<div class='chip-btn'>", unsafe_allow_html=True)
    for i, sug in enumerate(SUGGESTIONS):
        with chip_cols[i % 3]:
            if st.button(sug, key=f"sug_{i}"):
                st.session_state.messages.append({"role":"user","content":sug})
                st.session_state.last_query = sug
                st.session_state.last_result = None
                st.session_state.awaiting_refine = False
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Render existing messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style='display:flex;justify-content:flex-end;margin-bottom:12px'>
          <div style='background:{BRAND};color:#fff;border-radius:18px 4px 18px 18px;
                      padding:12px 16px;max-width:80%;
                      box-shadow:0 1px 3px rgba(232,101,26,.25)'>
            <p style='font-size:14px;margin:0;line-height:1.5'>{msg["content"]}</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

    elif msg["role"] == "assistant":
        content = msg["content"]

        if content.get("type") == "thinking":
            st.markdown(f"""
            <div style='display:flex;gap:10px;margin-bottom:12px'>
              <div style='width:32px;height:32px;background:{BRAND};border-radius:50%;
                          flex-shrink:0;display:flex;align-items:center;justify-content:center'>
                <svg width='16' height='16' viewBox='0 0 24 24' fill='none'>
                  <circle cx='12' cy='6' r='2.5' fill='white'/>
                  <circle cx='6' cy='18' r='2.5' fill='white' opacity='.7'/>
                  <circle cx='18' cy='18' r='2.5' fill='white' opacity='.7'/>
                  <line x1='12' y1='8.5' x2='6' y2='15.5' stroke='white' stroke-width='1.5' opacity='.6'/>
                  <line x1='12' y1='8.5' x2='18' y2='15.5' stroke='white' stroke-width='1.5' opacity='.6'/>
                </svg>
              </div>
              <div style='background:#fff;border-radius:4px 18px 18px 18px;
                          padding:12px 16px;box-shadow:0 1px 3px rgba(0,0,0,.08)'>
                <p style='font-size:13px;color:#b0a89e;margin:0'>Searching the network...</p>
              </div>
            </div>
            """, unsafe_allow_html=True)

        elif content.get("type") == "result":
            result = content["result"]
            reply = result.get("reply","")
            matches = result.get("matches",[])
            understood = result.get("understood_need","")
            expert_type = result.get("expert_type","")

            # Bot reply text
            st.markdown(f"""
            <div style='display:flex;gap:10px;margin-bottom:12px'>
              <div style='width:32px;height:32px;background:{BRAND};border-radius:50%;
                          flex-shrink:0;display:flex;align-items:center;
                          justify-content:center;margin-top:2px'>
                <svg width='16' height='16' viewBox='0 0 24 24' fill='none'>
                  <circle cx='12' cy='6' r='2.5' fill='white'/>
                  <circle cx='6' cy='18' r='2.5' fill='white' opacity='.7'/>
                  <circle cx='18' cy='18' r='2.5' fill='white' opacity='.7'/>
                  <line x1='12' y1='8.5' x2='6' y2='15.5' stroke='white' stroke-width='1.5' opacity='.6'/>
                  <line x1='12' y1='8.5' x2='18' y2='15.5' stroke='white' stroke-width='1.5' opacity='.6'/>
                </svg>
              </div>
              <div style='background:#fff;border-radius:4px 18px 18px 18px;
                          padding:14px 18px;box-shadow:0 1px 3px rgba(0,0,0,.08);max-width:85%'>
                <p style='font-size:14px;color:#1a1a1a;margin:0 0 6px;line-height:1.6'>{reply}</p>
                <p style='font-size:12px;color:#b0a89e;margin:0'>
                  Specialist identified: <span style='color:{BRAND};font-weight:500'>{expert_type}</span>
                </p>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Match cards
            rank_labels = ["Best match","Strong alternative","Also consider"]
            for i, m in enumerate(matches[:3]):
                conf = int(m.get("confidence",80))
                cc = conf_color(conf)
                cl = conf_label(conf)
                rl = rank_labels[i] if i < 3 else f"Match {i+1}"

                st.markdown(f"""
                <div style='margin-left:42px;margin-bottom:10px'>
                  <div style='background:#fff;border-radius:14px;padding:16px 18px;
                              box-shadow:0 1px 4px rgba(0,0,0,.08);
                              border-left:3px solid {cc}'>
                    <div style='display:flex;justify-content:space-between;
                                align-items:flex-start;margin-bottom:10px;flex-wrap:wrap;gap:6px'>
                      <div>
                        <p style='font-size:10px;text-transform:uppercase;letter-spacing:.1em;
                                   color:#b0a89e;margin:0 0 3px;font-weight:500'>{rl}</p>
                        <p style='font-size:16px;font-weight:700;color:#1a1a1a;margin:0 0 2px'>{m.get("name","")}</p>
                        <p style='font-size:13px;color:#6b7280;margin:0'>
                          {m.get("company","")} &nbsp;·&nbsp;
                          <span style='color:{BRAND}'>{m.get("speciality","")}</span>
                        </p>
                      </div>
                      <div style='text-align:right;flex-shrink:0'>
                        <p style='font-size:22px;font-weight:700;color:{cc};margin:0;line-height:1'>{conf}%</p>
                        <p style='font-size:11px;color:#b0a89e;margin:2px 0 0'>{cl}</p>
                      </div>
                    </div>
                    <div style='background:#f9f6f3;border-radius:8px;padding:10px 12px;margin-bottom:12px'>
                      <p style='font-size:12.5px;color:#6b7280;line-height:1.65;margin:0'>{m.get("reason","")}</p>
                    </div>
                    <div style='display:flex;gap:8px;flex-wrap:wrap'>
                      <a href='mailto:{m.get("email","")}?subject=Enquiry via Syndesi'
                         style='display:inline-flex;align-items:center;gap:6px;
                                padding:7px 14px;background:#FDF0E8;
                                border:1px solid #f0d8c4;border-radius:100px;
                                font-size:12.5px;color:{BRAND};text-decoration:none;font-weight:500'>
                        ✉ {m.get("email","")}
                      </a>
                      <span style='display:inline-flex;align-items:center;gap:6px;
                                    padding:7px 14px;background:#f5f3f0;
                                    border:1px solid #e8e0d8;border-radius:100px;
                                    font-size:12.5px;color:#6b7280'>
                        ☎ {m.get("phone","")}
                      </span>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # Refine prompt
            st.markdown(f"""
            <div style='display:flex;gap:10px;margin-bottom:12px;margin-top:4px'>
              <div style='width:32px;flex-shrink:0'></div>
              <div style='background:#fff;border-radius:4px 18px 18px 18px;
                          padding:12px 16px;box-shadow:0 1px 3px rgba(0,0,0,.08);max-width:85%'>
                <p style='font-size:14px;color:#6b7280;margin:0;line-height:1.6'>
                  Not the right fit? You can tell me more — e.g. <em>"show me someone in London"</em>,
                  <em>"I need someone more senior"</em>, or <em>"show me different options"</em>.
                </p>
              </div>
            </div>
            """, unsafe_allow_html=True)

        elif content.get("type") == "error":
            st.markdown(f"""
            <div style='display:flex;gap:10px;margin-bottom:12px'>
              <div style='width:32px;flex-shrink:0'></div>
              <div style='background:#fff5f5;border:1px solid #fecaca;border-radius:4px 18px 18px 18px;
                          padding:12px 16px;max-width:85%'>
                <p style='font-size:14px;color:#dc2626;margin:0'>{content.get("text","Something went wrong. Please try again.")}</p>
              </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# PROCESS PENDING QUERY
# ══════════════════════════════════════════
pending_query = st.session_state.get("last_query","")
has_result = st.session_state.get("last_result") is not None
needs_processing = (
    pending_query and
    not has_result and
    len(st.session_state.messages) > 0 and
    st.session_state.messages[-1]["role"] == "user"
)

if needs_processing:
    df = load_professionals()
    summary = get_summary(df)

    with st.spinner(""):
        result = find_experts(pending_query, summary)

    if result:
        st.session_state.last_result = result
        st.session_state.messages.append({
            "role":"assistant",
            "content":{"type":"result","result":result}
        })
        st.session_state.awaiting_refine = True
    else:
        st.session_state.messages.append({
            "role":"assistant",
            "content":{"type":"error","text":"I had trouble searching the network. Please try again in a moment."}
        })
    st.rerun()

# ══════════════════════════════════════════
# INPUT BAR — sticky bottom
# ══════════════════════════════════════════
st.markdown(f"""
<div style='position:fixed;bottom:0;left:0;right:0;
            background:linear-gradient(transparent,#F7F4F1 30%);
            padding:16px 16px 20px;z-index:99'>
  <div style='max-width:720px;margin:0 auto'>
""", unsafe_allow_html=True)

inp_col, btn_col = st.columns([1, 0.08], gap="small")

with inp_col:
    placeholder = "Refine your results..." if st.session_state.awaiting_refine else "Describe your situation..."
    user_input = st.text_input("msg", placeholder=placeholder, label_visibility="collapsed", key="chat_input")

with btn_col:
    st.markdown("<div style='padding-top:5px'>", unsafe_allow_html=True)
    send = st.button("→", key="send_btn")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

# Handle send
if (send or user_input) and user_input.strip():
    msg_text = user_input.strip()

    if st.session_state.awaiting_refine and st.session_state.last_result:
        # Refinement
        st.session_state.messages.append({"role":"user","content":msg_text})
        df = load_professionals()
        summary = get_summary(df)
        with st.spinner(""):
            refined = refine_experts(
                st.session_state.last_query,
                st.session_state.last_result,
                msg_text,
                summary
            )
        if refined:
            st.session_state.last_result = refined
            st.session_state.messages.append({
                "role":"assistant",
                "content":{"type":"result","result":refined}
            })
        else:
            st.session_state.messages.append({
                "role":"assistant",
                "content":{"type":"error","text":"I couldn't refine those results. Please try again."}
            })
    else:
        # New query
        st.session_state.messages.append({"role":"user","content":msg_text})
        st.session_state.last_query = msg_text
        st.session_state.last_result = None
        st.session_state.awaiting_refine = False

    st.rerun()
