import streamlit as st
import pandas as pd
import json
import urllib.request
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAu1-QAC04_voOMrPDYqBO6xwW5TOQ23MA")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1mjEM2jJ69Qc0m5R1mdw6wjsPhRJ0mscNhMJLwNdRM7Q/export?format=csv"

st.set_page_config(
    page_title="Syndesi Network",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stAppViewBlockContainer"],
section.main,.main .block-container,[data-testid="stMainBlockContainer"]{
  background:#08090e!important;font-family:'DM Sans',sans-serif!important;color:#fff!important
}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
#MainMenu,footer,[data-testid="stStatusWidget"]{display:none!important}
[data-testid="stSidebar"]{display:none!important}
.block-container,[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important}
[data-testid="stColumn"]{background:transparent!important}

.stTextArea>div,.stTextArea>div>div{background:transparent!important}
.stTextArea>div>div>textarea{
  background:#0e1018!important;border:1px solid rgba(212,182,115,.15)!important;
  border-radius:14px!important;color:rgba(255,255,255,.82)!important;
  font-family:'DM Sans',sans-serif!important;font-size:15px!important;
  font-weight:300!important;caret-color:#d4b673!important;
  line-height:1.7!important;padding:16px 18px!important;resize:none!important
}
.stTextArea>div>div>textarea:focus{
  border-color:rgba(212,182,115,.4)!important;
  box-shadow:0 0 0 3px rgba(212,182,115,.06)!important;outline:none!important
}
.stTextArea>div>div>textarea::placeholder{color:rgba(255,255,255,.16)!important}
.stTextArea label{display:none!important}

.stButton>button{
  background:#d4b673!important;color:#08090e!important;border:none!important;
  border-radius:10px!important;padding:14px 28px!important;
  font-family:'DM Sans',sans-serif!important;font-size:14px!important;
  font-weight:600!important;width:100%!important;letter-spacing:.02em!important;
  transition:all .2s ease!important
}
.stButton>button:hover{background:#e2c88a!important;transform:translateY(-1px)!important}
.stButton>button:active{transform:translateY(0)!important}

.refine-btn .stButton>button{
  background:transparent!important;color:rgba(212,182,115,.7)!important;
  border:1px solid rgba(212,182,115,.2)!important;border-radius:8px!important;
  padding:8px 18px!important;font-size:13px!important;font-weight:400!important
}
.refine-btn .stButton>button:hover{
  background:rgba(212,182,115,.06)!important;color:rgba(212,182,115,.95)!important;transform:none!important
}

.exbtn .stButton>button{
  background:transparent!important;color:rgba(255,255,255,.28)!important;
  border:1px solid rgba(255,255,255,.07)!important;border-radius:8px!important;
  padding:7px 12px!important;font-size:11.5px!important;font-weight:400!important
}
.exbtn .stButton>button:hover{
  color:rgba(255,255,255,.55)!important;border-color:rgba(255,255,255,.14)!important;
  background:rgba(255,255,255,.03)!important;transform:none!important
}

[data-testid="stInfo"]>div{
  background:rgba(212,182,115,.05)!important;border:1px solid rgba(212,182,115,.15)!important;border-radius:10px!important
}
[data-testid="stInfo"] p{color:rgba(212,182,115,.7)!important;font-size:13px!important}
[data-testid="stSpinner"]>div>div{border-top-color:#d4b673!important}
.stSpinner>div{color:rgba(255,255,255,.3)!important}
hr{border:none!important;border-top:1px solid rgba(255,255,255,.05)!important;margin:1.5rem 0!important}
</style>
""", unsafe_allow_html=True)

def pad():
    _, c, _ = st.columns([.07, .86, .07])
    return c

@st.cache_data(ttl=300)
def load_professionals():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Could not load professionals database: {e}")
        return pd.DataFrame()

def gemini_call(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    body = json.dumps({"contents":[{"parts":[{"text":prompt}]}]}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read().decode("utf-8"))
        raw = result["candidates"][0]["content"]["parts"][0]["text"]
        return raw.replace("```json","").replace("```","").strip()
    except Exception as e:
        return None

def get_summary(df):
    lines = []
    for _, row in df.iterrows():
        parts = [str(row.get(c,"")).strip() for c in df.columns if str(row.get(c,"")).strip() and str(row.get(c,"")) != "nan"]
        lines.append(" | ".join(parts))
    return "\n".join(lines)

def analyse(query, prof_summary):
    prompt = f"""You are an expert professional services concierge for Syndesi Network — a curated network of verified UK professionals.

A user has submitted this query:
"{query}"

Here are ALL available professionals in the network (one per line):
{prof_summary}

Your tasks:
1. Understand what the user ACTUALLY needs — even if described vaguely, emotionally, or without using technical terms
2. Identify which type of specialist they need
3. Match them to the TOP 3 most suitable professionals from the list above
4. Score each match 0-100 based on how well their speciality fits the user's actual need
5. Write a specific 2-3 sentence reason for each match explaining WHY they are right for this situation

Return ONLY valid JSON in this exact format, no other text:
{{
  "understood_need": "One clear sentence explaining what the user actually needs",
  "expert_type_needed": "The specific type of specialist needed",
  "matches": [
    {{
      "name": "Exact name from the list",
      "company": "Exact company from the list",
      "speciality": "Exact speciality from the list",
      "email": "Exact email from the list",
      "phone": "Exact phone from the list",
      "confidence": 92,
      "reason": "2-3 sentences explaining specifically why this person fits this query"
    }}
  ]
}}

Return exactly 3 matches ordered by confidence score (highest first). Return ONLY the JSON object."""

    raw = gemini_call(prompt)
    if raw:
        try:
            return json.loads(raw)
        except:
            return None
    return None

def refine(query, prev_result, refinement, prof_summary):
    prompt = f"""You are an expert professional services concierge for Syndesi Network.

Original query: "{query}"
User's refinement: "{refinement}"

Previous matches shown:
{json.dumps(prev_result.get('matches',[]), indent=2)}

All available professionals:
{prof_summary}

Apply the user's refinement request (e.g. show different people, filter by location, seniority, different speciality, show more options) and return an updated top 3.

Return ONLY valid JSON:
{{
  "understood_need": "Updated understanding incorporating the refinement",
  "expert_type_needed": "Updated expert type",
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
    if s >= 85: return "#34d399"
    if s >= 65: return "#fbbf24"
    return "#f87171"

def conf_badge(s):
    if s >= 85: return ("Strong Match","rgba(52,211,153,.08);color:#34d399")
    if s >= 65: return ("Good Match","rgba(251,191,36,.08);color:#fbbf24")
    return ("Possible Match","rgba(248,113,113,.08);color:#f87171")

EXAMPLES = [
    ("HMRC Debt","HMRC are chasing me for unpaid taxes and I don't know what to do"),
    ("Sell Business","I want to sell my business and need advice on valuation"),
    ("Landlord Dispute","My landlord won't return my deposit and is ignoring me"),
    ("Start a Company","I want to set up a limited company for my consultancy"),
    ("Unfair Dismissal","I've just been made redundant and I think it was unfair"),
    ("Debt Problems","I owe money to multiple creditors and can't keep up with payments"),
]

# ═══ HEADER ═══
with pad():
    h1, h2, h3 = st.columns([1,1,1])
    with h1:
        st.markdown("""
        <div style='padding:20px 0 12px;display:flex;align-items:center;gap:11px'>
          <svg width='32' height='32' viewBox='0 0 30 30' fill='none' xmlns='http://www.w3.org/2000/svg'>
            <circle cx='15' cy='15' r='13.5' stroke='#d4b673' stroke-width='1' opacity='0.35'/>
            <circle cx='15' cy='7'  r='3.5' fill='#d4b673'/>
            <circle cx='7'  cy='21' r='3.5' fill='#d4b673' opacity='0.65'/>
            <circle cx='23' cy='21' r='3.5' fill='#d4b673' opacity='0.65'/>
            <line x1='15' y1='10.5' x2='7'  y2='17.5' stroke='#d4b673' stroke-width='1' opacity='0.35'/>
            <line x1='15' y1='10.5' x2='23' y2='17.5' stroke='#d4b673' stroke-width='1' opacity='0.35'/>
            <line x1='7'  y1='21'   x2='23' y2='21'   stroke='#d4b673' stroke-width='1' opacity='0.25'/>
          </svg>
          <div>
            <p style='font-family:Cormorant Garamond,serif;font-size:19px;font-weight:600;
                       color:#d4b673;margin:0;letter-spacing:.05em;line-height:1'>SYNDESI</p>
            <p style='font-size:8px;color:rgba(255,255,255,.2);margin:2px 0 0;
                       letter-spacing:.22em;text-transform:uppercase'>NETWORK</p>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        st.markdown("""
        <div style='display:flex;align-items:center;justify-content:center;
                    gap:28px;padding:24px 0 12px'>
          <span style='font-size:12.5px;color:rgba(255,255,255,.22)'>Find an Expert</span>
          <span style='font-size:12.5px;color:rgba(255,255,255,.22)'>Our Network</span>
          <a href='https://www.syndesi.network' target='_blank'
             style='font-size:12.5px;color:rgba(212,182,115,.45);text-decoration:none'>
            syndesi.network
          </a>
        </div>
        """, unsafe_allow_html=True)
    with h3:
        st.markdown("""
        <div style='display:flex;justify-content:flex-end;align-items:center;padding:24px 0 12px'>
          <a href='mailto:hello@syndesi.network'
             style='font-size:12px;color:rgba(212,182,115,.55);text-decoration:none;
                    padding:7px 16px;border:1px solid rgba(212,182,115,.16);border-radius:8px'>
            Contact
          </a>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1px;background:rgba(255,255,255,.04)'></div>", unsafe_allow_html=True)

# ═══ HERO ═══
with pad():
    st.markdown("""
    <div style='padding:60px 0 48px;border-bottom:1px solid rgba(255,255,255,.04)'>
      <p style='font-size:10px;letter-spacing:.28em;text-transform:uppercase;
                color:rgba(212,182,115,.5);margin:0 0 18px;font-weight:500'>
        Professional Matching — Powered by AI
      </p>
      <h1 style='font-family:Cormorant Garamond,serif;
                 font-size:clamp(34px,4.5vw,60px);font-weight:600;
                 line-height:1.08;color:#fff;margin:0 0 18px;letter-spacing:-.01em'>
        Describe your situation.<br>
        <span style='color:#d4b673'>We find the right expert.</span>
      </h1>
      <p style='font-size:15px;font-weight:300;color:rgba(255,255,255,.32);
                max-width:500px;line-height:1.8;margin:0'>
        No need to know which specialist you need. Describe your situation in plain language —
        our AI understands the underlying need and connects you with the most suitable
        professionals from our verified network.
      </p>
      <div style='display:flex;gap:36px;margin-top:36px;padding-top:28px;
                  border-top:1px solid rgba(255,255,255,.04)'>
        <div>
          <p style='font-family:Cormorant Garamond,serif;font-size:24px;
                     font-weight:600;color:#d4b673;margin:0'>70+</p>
          <p style='font-size:9px;color:rgba(255,255,255,.2);text-transform:uppercase;
                     letter-spacing:.14em;margin:4px 0 0'>Verified Professionals</p>
        </div>
        <div>
          <p style='font-family:Cormorant Garamond,serif;font-size:24px;
                     font-weight:600;color:#d4b673;margin:0'>AI</p>
          <p style='font-size:9px;color:rgba(255,255,255,.2);text-transform:uppercase;
                     letter-spacing:.14em;margin:4px 0 0'>Smart Matching</p>
        </div>
        <div>
          <p style='font-family:Cormorant Garamond,serif;font-size:24px;
                     font-weight:600;color:#d4b673;margin:0'>Free</p>
          <p style='font-size:9px;color:rgba(255,255,255,.2);text-transform:uppercase;
                     letter-spacing:.14em;margin:4px 0 0'>To Use</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ═══ EXAMPLES ═══
with pad():
    st.markdown("""
    <p style='font-size:9.5px;letter-spacing:.2em;text-transform:uppercase;
               color:rgba(255,255,255,.18);font-weight:500;margin:28px 0 10px'>
      Example situations — click to try
    </p>
    """, unsafe_allow_html=True)
    st.markdown("<div class='exbtn'>", unsafe_allow_html=True)
    ec = st.columns(3, gap="small")
    for i,(label,query) in enumerate(EXAMPLES):
        with ec[i%3]:
            if st.button(label, key=f"eq_{i}"):
                st.session_state["prefill"] = query
                st.session_state["last_result"] = None
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ═══ INPUT ═══
with pad():
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <p style='font-family:Cormorant Garamond,serif;font-size:22px;font-weight:600;
               color:#fff;margin:0 0 6px'>Describe your situation</p>
    <p style='font-size:13px;color:rgba(255,255,255,.28);margin:0 0 14px;line-height:1.6'>
      Be as specific or as general as you like. Our AI will work out what you need.
    </p>
    """, unsafe_allow_html=True)

    prefill = st.session_state.get("prefill","")
    user_query = st.text_area(
        "query", value=prefill,
        placeholder="E.g. HMRC are chasing me for unpaid taxes from 3 years ago and I don't know where to start...\n\nOr: My business partner wants to buy me out but I think the valuation is too low...\n\nOr: I've been dismissed and my employer says it's redundancy but I think they just wanted me gone...",
        height=160, label_visibility="collapsed"
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    find = st.button("Find the Right Expert →")

# ═══ RESULTS ═══
if find and user_query.strip():
    st.session_state["last_query"] = user_query
    st.session_state["last_result"] = None

if st.session_state.get("last_query") and not st.session_state.get("last_result"):
    query = st.session_state["last_query"]
    df = load_professionals()
    if df.empty:
        with pad():
            st.error("Could not load the professionals database. Please check the Google Sheet connection.")
        st.stop()
    summary = get_summary(df)
    with pad():
        with st.spinner("Understanding your situation and searching our network..."):
            result = analyse(query, summary)
        if result:
            st.session_state["last_result"] = result
        else:
            st.markdown("""
            <div style='padding:14px 18px;background:rgba(239,68,68,.05);
                        border:1px solid rgba(239,68,68,.15);border-radius:10px;
                        font-size:13.5px;color:rgba(239,68,68,.65)'>
              Could not analyse your query. Please try again in a moment.
            </div>
            """, unsafe_allow_html=True)
            st.stop()

result = st.session_state.get("last_result")
if result:
    with pad():
        st.markdown("<hr>", unsafe_allow_html=True)

        # AI UNDERSTANDING BANNER
        st.markdown(f"""
        <div style='padding:18px 22px;background:rgba(212,182,115,.04);
                    border:1px solid rgba(212,182,115,.12);border-radius:12px;margin-bottom:24px'>
          <p style='font-size:9px;letter-spacing:.2em;text-transform:uppercase;
                     color:rgba(212,182,115,.4);margin:0 0 7px;font-weight:500'>
            AI Understanding
          </p>
          <p style='font-family:Cormorant Garamond,serif;font-size:20px;font-weight:500;
                     color:rgba(255,255,255,.75);margin:0 0 8px;line-height:1.5'>
            {result.get("understood_need","")}
          </p>
          <p style='font-size:12px;color:rgba(255,255,255,.26);margin:0'>
            Specialist identified:&nbsp;
            <strong style='color:rgba(212,182,115,.6);font-weight:500'>
              {result.get("expert_type_needed","")}
            </strong>
          </p>
        </div>
        """, unsafe_allow_html=True)

        # RESULTS HEADING
        st.markdown("""
        <p style='font-family:Cormorant Garamond,serif;font-size:22px;font-weight:600;
                   color:#fff;margin:0 0 4px'>Top matches from our network</p>
        <p style='font-size:13px;color:rgba(255,255,255,.25);margin:0 0 20px'>
          Ranked by relevance to your specific situation
        </p>
        """, unsafe_allow_html=True)

        # MATCH CARDS
        rank_labels = ["Best Match","Strong Alternative","Also Consider"]
        for i, m in enumerate(result.get("matches",[])[:3]):
            conf = int(m.get("confidence", 80))
            cc = conf_color(conf)
            cl, cs = conf_badge(conf)
            rl = rank_labels[i] if i < 3 else f"Match {i+1}"

            st.markdown(f"""
            <div style='padding:24px;background:#0e1018;
                        border:1px solid rgba(255,255,255,.06);
                        border-radius:14px;margin-bottom:12px;
                        position:relative;overflow:hidden'>
              <div style='position:absolute;top:0;left:0;right:0;height:2px;
                           background:linear-gradient(90deg,{cc}55,transparent)'></div>

              <div style='display:flex;justify-content:space-between;
                           align-items:flex-start;margin-bottom:18px;
                           flex-wrap:wrap;gap:12px'>
                <div>
                  <p style='font-size:9px;letter-spacing:.16em;text-transform:uppercase;
                             color:rgba(255,255,255,.18);margin:0 0 5px'>{rl}</p>
                  <p style='font-family:Cormorant Garamond,serif;font-size:24px;
                             font-weight:600;color:#fff;margin:0 0 3px;letter-spacing:.01em'>
                    {m.get("name","")}
                  </p>
                  <p style='font-size:13px;color:rgba(255,255,255,.35);margin:0'>
                    {m.get("company","")}&nbsp;&nbsp;
                    <span style='color:rgba(212,182,115,.5)'>·</span>&nbsp;&nbsp;
                    <span style='color:rgba(212,182,115,.55)'>{m.get("speciality","")}</span>
                  </p>
                </div>
                <div style='text-align:right;flex-shrink:0'>
                  <p style='font-family:Cormorant Garamond,serif;font-size:32px;
                             font-weight:600;color:{cc};margin:0;line-height:1'>{conf}%</p>
                  <p style='font-size:9px;color:rgba(255,255,255,.18);text-transform:uppercase;
                             letter-spacing:.1em;margin:3px 0 6px'>Match</p>
                  <span style='display:inline-block;padding:3px 10px;border-radius:5px;
                                font-size:10px;font-weight:500;background:{cs}'>{cl}</span>
                </div>
              </div>

              <div style='padding:13px 16px;background:rgba(255,255,255,.025);
                           border-radius:8px;margin-bottom:16px'>
                <p style='font-size:9px;letter-spacing:.14em;text-transform:uppercase;
                           color:rgba(255,255,255,.18);margin:0 0 5px'>Why this match</p>
                <p style='font-size:13.5px;color:rgba(255,255,255,.48);
                           line-height:1.7;margin:0'>{m.get("reason","")}</p>
              </div>

              <div style='display:flex;gap:10px;flex-wrap:wrap'>
                <a href='mailto:{m.get("email","")}?subject=Enquiry via Syndesi Network'
                   style='display:inline-flex;align-items:center;gap:7px;
                          padding:9px 16px;background:rgba(212,182,115,.08);
                          border:1px solid rgba(212,182,115,.18);border-radius:8px;
                          font-size:12.5px;color:#d4b673;text-decoration:none'>
                  ✉&nbsp; {m.get("email","")}
                </a>
                <span style='display:inline-flex;align-items:center;gap:7px;
                              padding:9px 16px;background:rgba(255,255,255,.04);
                              border:1px solid rgba(255,255,255,.07);border-radius:8px;
                              font-size:12.5px;color:rgba(255,255,255,.38)'>
                  ☎&nbsp; {m.get("phone","")}
                </span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # REFINE
        st.markdown("""
        <div style='margin-top:24px;padding-top:20px;border-top:1px solid rgba(255,255,255,.05)'>
          <p style='font-family:Cormorant Garamond,serif;font-size:18px;font-weight:500;
                     color:rgba(255,255,255,.6);margin:0 0 5px'>Not quite right?</p>
          <p style='font-size:13px;color:rgba(255,255,255,.25);margin:0 0 12px'>
            Tell us more and we'll refine your results.
          </p>
        </div>
        """, unsafe_allow_html=True)

        refine_input = st.text_area(
            "refine", key="refine_text",
            placeholder="E.g. Show me more options... I need someone in London... I need someone who specialises in VAT specifically... Show me a more senior specialist...",
            height=80, label_visibility="collapsed"
        )
        st.markdown("<div class='refine-btn'>", unsafe_allow_html=True)
        if st.button("Refine My Results →", key="refine_btn"):
            if refine_input.strip():
                df = load_professionals()
                summary = get_summary(df)
                with st.spinner("Refining your matches..."):
                    refined = refine(
                        st.session_state.get("last_query",""),
                        result, refine_input, summary
                    )
                if refined:
                    st.session_state["last_result"] = refined
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <p style='font-size:11.5px;color:rgba(255,255,255,.16);line-height:1.7;margin:0'>
          All professionals listed are verified members of the Syndesi Network.
          Matches provided by this tool do not constitute legal, financial or tax advice.
          Always conduct your own due diligence before engaging any professional.
        </p>
        """, unsafe_allow_html=True)

# ═══ FOOTER ═══
with pad():
    st.markdown("""
    <hr>
    <div style='display:flex;justify-content:space-between;align-items:center;
                padding-bottom:36px;flex-wrap:wrap;gap:16px'>
      <div style='display:flex;align-items:center;gap:10px'>
        <svg width='20' height='20' viewBox='0 0 30 30' fill='none'>
          <circle cx='15' cy='15' r='13.5' stroke='#d4b673' stroke-width='1' opacity='0.3'/>
          <circle cx='15' cy='7'  r='3'   fill='#d4b673' opacity='0.7'/>
          <circle cx='7'  cy='21' r='3'   fill='#d4b673' opacity='0.45'/>
          <circle cx='23' cy='21' r='3'   fill='#d4b673' opacity='0.45'/>
          <line x1='15' y1='10' x2='7'  y2='18' stroke='#d4b673' stroke-width='1' opacity='0.3'/>
          <line x1='15' y1='10' x2='23' y2='18' stroke='#d4b673' stroke-width='1' opacity='0.3'/>
        </svg>
        <div>
          <p style='font-family:Cormorant Garamond,serif;font-size:14px;font-weight:600;
                     color:rgba(212,182,115,.4);margin:0;letter-spacing:.05em'>SYNDESI NETWORK</p>
          <p style='font-size:9px;color:rgba(255,255,255,.14);margin:0;letter-spacing:.1em'>
            www.syndesi.network
          </p>
        </div>
      </div>
      <div style='display:flex;gap:20px;flex-wrap:wrap;align-items:center'>
        <a href='https://www.syndesi.network' target='_blank'
           style='font-size:12px;color:rgba(255,255,255,.2);text-decoration:none'>Website</a>
        <a href='mailto:hello@syndesi.network'
           style='font-size:12px;color:rgba(255,255,255,.2);text-decoration:none'>
          hello@syndesi.network
        </a>
        <span style='font-size:12px;color:rgba(255,255,255,.1)'>© 2026 Syndesi Network</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
