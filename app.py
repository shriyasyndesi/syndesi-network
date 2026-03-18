import streamlit as st
import pandas as pd
from datetime import datetime

SHEET_ID = "1mjEM2jJ69Qc0m5R1mdw6wjsPhRJ0mscNhMJLwNdRM7Q"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
SYNDESI_LINK = "https://app.syndesi.network/login"

st.set_page_config(page_title="Syndesi Assistant", page_icon="🧠", layout="wide")

CATEGORY_MAP = {
    "⚖️ Legal": [
        "Adeeb Chowdhry", "Alexander David Keenan", "Amaar Faaruq", "Daniel Wong",
        "Harpreet Talwar", "James Winfield", "Jonathan Jacobs", "Jonathan Warner-Reed",
        "Lily Malekyazdi", "Manjinder Talwar", "Matthew Dunne", "Nastassia Khilkevich",
        "Patrick Mulcahy", "Paul O'Flynn", "Stephen Carr", "Tamsyn Lees",
        "Zagam Hayat", "James Klein"
    ],
    "💰 Financial Planning": [
        "Andrew Mallon", "Duncan Butler-Wheelhouse", "Ian Richards", "Joshua Pomerance",
        "Michael Gould", "Richard Brain", "Tara Maiya"
    ],
    "🏠 Mortgages & Lending": [
        "David Forsdyke", "Hass Draper", "John Kent", "Joshua David", "Laura Fisher"
    ],
    "🛡️ Insurance": [
        "Jeremy Woolf", "Jigar Mehta", "Jordan Barnard", "Rebekah Humphries"
    ],
    "📊 Tax": [
        "Andy Wood", "Arnold Aaron", "Sadique Maskeen", "Stuart Stobie"
    ],
    "🏢 Corporate Finance & M&A": [
        "Alex Reed", "Kris Venkatesh", "Laurence Vogel", "Sue Collins"
    ],
    "💱 Other Services": [
        "Melvyn Marks", "Michael Torrin"
    ],
}

SUBCATEGORIES = {
    "⚖️ Legal": [
        ("🏠 Property", ["property", "conveyancing", "landlord", "tenant"]),
        ("👨‍👩‍👧 Family & Immigration", ["immigration", "asylum", "family"]),
        ("📜 Wills & Probate", ["wills", "probate", "lpa", "estate", "trust"]),
        ("⚔️ Disputes", ["dispute", "litigation", "resolution"]),
        ("🏥 Corporate & Commercial", ["corporate", "commercial", "healthcare", "insolvency", "restructur"]),
        ("🌾 Other Legal", ["agricultural", "notarial"]),
    ],
    "💰 Financial Planning": [
        ("🎯 Retirement & Pensions", ["retirement", "pension"]),
        ("📈 Investments & Wealth", ["investment", "wealth", "isa", "sipp"]),
        ("🏦 IHT & Estate Planning", ["iht", "inheritance", "estate"]),
        ("🛡️ Protection", ["protection"]),
    ],
    "🏠 Mortgages & Lending": [
        ("🏡 Residential", ["residential"]),
        ("🏢 Commercial", ["commercial"]),
        ("🌉 Bridging & Development", ["bridging", "development"]),
        ("📦 Asset & Invoice Finance", ["asset", "invoice"]),
        ("🌅 Later Life / Equity Release", ["later life", "equity release", "lifetime"]),
        ("💼 Buy-to-Let", ["buy-to-let"]),
    ],
    "🛡️ Insurance": [
        ("🏥 Medical Insurance", ["medical"]),
        ("🏠 Household & Commercial", ["household", "commercial", "liability"]),
        ("👷 Business & Contractor", ["business", "contractor", "sme", "trade", "freelance"]),
        ("🌍 General Insurance", ["general", "complex", "pi", "motor"]),
    ],
    "📊 Tax": [
        ("🏗️ Capital Allowances", ["capital allowance"]),
        ("💼 Tax Advisory", ["tax advisory", "advisory"]),
        ("🏛️ Inheritance Tax", ["inheritance tax", "iht"]),
        ("🌍 International / Relocation", ["uae", "relocation", "international"]),
    ],
    "🏢 Corporate Finance & M&A": [
        ("🚀 Venture Capital & Fundraising", ["venture", "fundraising", "start-up"]),
        ("🤝 M&A & Private Equity", ["m&a", "private equity", "private credit", "debt"]),
        ("📉 Insolvency & Restructuring", ["insolvency", "cva", "cvl", "administration", "restructur", "liquidat"]),
    ],
    "💱 Other Services": [
        ("💱 Foreign Exchange", ["foreign exchange", "payments", "fx"]),
        ("📲 Payment Services", ["payment", "open banking", "qr"]),
    ],
}

# ── SESSION STATE ──
defaults = {
    "step": "category",
    "chosen_category": None,
    "chosen_sub": None,
    "search_query": "",
    "recent_searches": [],  # list of dicts: {category, sub, time}
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def reset():
    st.session_state.step = "category"
    st.session_state.chosen_category = None
    st.session_state.chosen_sub = None
    st.session_state.search_query = ""

def add_recent(category, sub):
    label = category + (" › " + sub if sub and sub != "__all__" else "")
    entry = {"label": label, "category": category, "sub": sub, "time": datetime.now().strftime("%H:%M")}
    # avoid duplicates
    st.session_state.recent_searches = [r for r in st.session_state.recent_searches if r["label"] != label]
    st.session_state.recent_searches.insert(0, entry)
    st.session_state.recent_searches = st.session_state.recent_searches[:10]  # keep last 10

def restore_search(entry):
    st.session_state.chosen_category = entry["category"]
    st.session_state.chosen_sub = entry["sub"]
    st.session_state.step = "results"
    st.session_state.search_query = ""

# ── LOAD DATA ──
@st.cache_data(ttl=300)
def load_professionals():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip() for c in df.columns]
        return df.dropna(how="all"), None
    except Exception as e:
        return None, str(e)

df, err = load_professionals()

def get_experts_for_names(names):
    if df is None: return []
    return df[df["Name"].isin(names)].to_dict("records")

def initials(name):
    parts = name.strip().split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else name[:2].upper()

def render_expert(expert):
    name       = str(expert.get("Name", "")).strip()
    company    = str(expert.get("Company", "")).strip()
    speciality = str(expert.get("Speciality", "")).strip()
    email      = str(expert.get("Email", "")).strip()
    phone      = str(expert.get("Phone", "")).strip()

    contact_rows = ""
    if email and email != "nan":
        contact_rows += (
            "<div class='contact-item'>"
            "<div class='contact-icon'>&#9993;</div>"
            "<span class='contact-text'>" + email + "</span>"
            "</div>"
        )
    if phone and phone != "nan":
        contact_rows += (
            "<div class='contact-item'>"
            "<div class='contact-icon'>&#128222;</div>"
            "<span class='contact-text'>" + phone + "</span>"
            "</div>"
        )

    card_html = (
        "<div class='expert-card'>"
        "<div class='expert-header'>"
        "<div class='expert-initials'>" + initials(name) + "</div>"
        "<div class='expert-info'>"
        "<div class='expert-name'>" + name + "</div>"
        "<div class='expert-co'>" + company + "</div>"
        "</div></div>"
        "<div class='spec-tag'>" + speciality[:60] + "</div>"
        "<div class='contact-row'>" + contact_rows + "</div>"
        "<a href='" + SYNDESI_LINK + "' target='_blank' class='syndesi-btn'>&#128279; Contact on Syndesi</a>"
        "</div>"
    )
    st.markdown(card_html, unsafe_allow_html=True)

# ── STYLES ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: #F2F2F5 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stMain"] { padding: 0 !important; background: #F2F2F5 !important; }
section[data-testid="stMain"] > div { padding: 0 !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #18181B !important;
    box-shadow: 2px 0 20px rgba(0,0,0,0.25) !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

.sb-header {
    padding: 32px 24px 22px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.sb-brand { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.sb-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #E8651A, #F0853A);
    border-radius: 10px; display: flex; align-items: center;
    justify-content: center; font-size: 19px;
    box-shadow: 0 2px 8px rgba(232,101,26,0.4); flex-shrink: 0;
}
.sb-title { font-weight: 800; font-size: 16px; color: #F5F5F7; letter-spacing: -0.2px; }
.sb-subtitle { font-size: 11px; color: #52525B; padding-left: 48px; font-weight: 500; }
.sb-section-label {
    font-size: 10px; font-weight: 700; color: #3F3F46;
    text-transform: uppercase; letter-spacing: 1.2px;
    padding: 24px 24px 10px;
}
.sb-empty {
    padding: 12px 24px 20px; text-align: center;
    color: #3F3F46; font-size: 12px; line-height: 1.6; font-style: italic;
}
.sb-item {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 24px; border-left: 2px solid transparent;
    transition: all 0.15s;
}
.sb-item:hover { background: rgba(255,255,255,0.05); border-left-color: #E8651A; }
.sb-item-label { font-size: 12px; color: #A1A1AA; font-weight: 500; line-height: 1.4; flex: 1; }
.sb-item-time { font-size: 10px; color: #3F3F46; flex-shrink: 0; }

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #E8651A, #D45515) !important;
    border: none !important; border-radius: 12px !important;
    color: white !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important; font-size: 13px !important;
    padding: 12px 18px !important; width: 100% !important;
    box-shadow: 0 2px 12px rgba(232,101,26,0.4) !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    box-shadow: 0 4px 20px rgba(232,101,26,0.55) !important;
    transform: translateY(-1px) !important; color: white !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important; color: #A1A1AA !important;
    font-size: 14px !important; padding: 5px 10px !important;
    font-weight: 400 !important; box-shadow: none !important; transform: none !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button:hover {
    background: rgba(232,101,26,0.15) !important;
    border-color: #E8651A !important; color: #E8651A !important; transform: none !important;
}

/* ── CHAT HEADER ── */
.chat-header {
    background: white;
    border-bottom: 1px solid #E5E5EA;
    padding: 14px 40px 14px 60px;
    display: flex; align-items: center; gap: 14px;
    box-shadow: 0 1px 0 rgba(0,0,0,0.06);
}
.hdr-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #E8651A, #F0853A);
    border-radius: 11px; display: flex; align-items: center;
    justify-content: center; font-size: 20px;
    box-shadow: 0 2px 8px rgba(232,101,26,0.3); flex-shrink: 0;
}
.hdr-name { font-weight: 800; font-size: 17px; color: #09090B; letter-spacing: -0.3px; }
.hdr-badge {
    margin-left: auto; font-size: 11px; color: #71717A; font-weight: 600;
    background: #F4F4F5; padding: 4px 12px; border-radius: 20px; border: 1px solid #E4E4E7;
}

/* ── CHAT BODY ── */
.chat-body {
    padding: 28px 40px 20px 60px;
    max-width: 1000px; width: 100%;
}

/* Bot bubble */
.bubble-bot { display: flex; gap: 12px; align-items: flex-start; margin-bottom: 20px; }
.bot-av {
    width: 32px; height: 32px; flex-shrink: 0; margin-top: 2px;
    background: linear-gradient(135deg, #E8651A, #F0853A);
    border-radius: 9px; display: flex; align-items: center;
    justify-content: center; font-size: 16px;
    box-shadow: 0 2px 6px rgba(232,101,26,0.3);
}
.bot-msg {
    background: white; border: 1px solid #E5E5EA;
    border-radius: 6px 18px 18px 18px;
    padding: 14px 18px; font-size: 14.5px; color: #18181B;
    line-height: 1.7; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    max-width: 78%;
}

/* User bubble */
.user-bubble-wrap { display: flex; justify-content: flex-end; margin-bottom: 20px; }
.user-msg {
    background: linear-gradient(135deg, #E8651A, #D45515);
    color: white; border-radius: 18px 6px 18px 18px;
    padding: 12px 18px; font-size: 14px; font-weight: 500;
    max-width: 65%; line-height: 1.55;
    box-shadow: 0 2px 12px rgba(232,101,26,0.3);
}

/* Category / subcategory option buttons */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background: white !important;
    border: 1.5px solid #E4E4E7 !important;
    border-radius: 14px !important; color: #27272A !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 14px !important;
    padding: 14px 18px !important; width: 100% !important;
    text-align: left !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    transition: all 0.15s !important;
    margin-bottom: 4px !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    border-color: #E8651A !important; color: #E8651A !important;
    box-shadow: 0 3px 12px rgba(232,101,26,0.15) !important;
    transform: translateY(-1px) !important;
}

/* Show all / restart */
div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] > button {
    background: transparent !important; border: 1.5px solid #E4E4E7 !important;
    border-radius: 10px !important; color: #71717A !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 13px !important;
    padding: 10px 20px !important; transition: all 0.15s !important;
}
div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] > button:hover {
    border-color: #E8651A !important; color: #E8651A !important;
}

/* ── EXPERT CARD ── */
.expert-card {
    background: white; border: 1px solid #E5E5EA;
    border-radius: 18px; padding: 22px 24px; margin-bottom: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s, transform 0.2s;
}
.expert-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.09); transform: translateY(-2px); }
.expert-header { display: flex; align-items: flex-start; gap: 14px; }
.expert-initials {
    width: 46px; height: 46px; border-radius: 13px; flex-shrink: 0;
    background: linear-gradient(135deg, #FFF0E6, #FDDCBE);
    color: #E8651A; font-weight: 800; font-size: 16px;
    display: flex; align-items: center; justify-content: center;
}
.expert-info { flex: 1; }
.expert-name { font-weight: 700; font-size: 16px; color: #09090B; margin-bottom: 3px; }
.expert-co { color: #71717A; font-size: 13px; font-weight: 500; }
.spec-tag {
    display: inline-block; background: #FFF7ED; color: #C2571A;
    font-size: 10px; font-weight: 700; padding: 3px 10px;
    border-radius: 20px; text-transform: uppercase; letter-spacing: 0.6px;
    margin: 14px 0 12px; border: 1px solid #FDDCBC;
}
.contact-row { display: flex; flex-direction: column; gap: 7px; margin-bottom: 16px; }
.contact-item { display: flex; align-items: center; gap: 10px; }
.contact-icon {
    width: 28px; height: 28px; background: #F4F4F5; border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; flex-shrink: 0;
}
.contact-text { font-size: 13px; color: #3F3F46; font-weight: 500; }
.syndesi-btn {
    display: inline-flex; align-items: center; gap: 8px;
    background: linear-gradient(135deg, #E8651A, #D45515);
    color: white !important; text-decoration: none;
    padding: 10px 20px; border-radius: 11px;
    font-size: 13px; font-weight: 700;
    box-shadow: 0 2px 10px rgba(232,101,26,0.35);
    transition: all 0.15s;
}
.syndesi-btn:hover {
    box-shadow: 0 4px 18px rgba(232,101,26,0.5);
    transform: translateY(-1px); color: white !important;
}

/* ── CHAT INPUT ── */
[data-testid="stBottom"] {
    background: transparent !important;
    border: none !important; box-shadow: none !important; padding: 0 !important;
}
[data-testid="stBottom"] > div {
    background: transparent !important; border: none !important; padding: 0 !important;
}
[data-testid="stChatInput"] {
    background: white !important;
    border-top: 1px solid #E5E5EA !important;
    padding: 16px 40px 20px 60px !important;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.06) !important;
    margin: 0 !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important; color: #18181B !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #A1A1AA !important; font-size: 14px !important;
}
[data-testid="stChatInputSubmitButton"] button {
    background: linear-gradient(135deg, #E8651A, #D45515) !important;
    border: none !important;
}

.divider { border: none; border-top: 1px solid #E5E5EA; margin: 24px 0 18px; }

</style>
""", unsafe_allow_html=True)



# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
        <div class="sb-header">
            <div class="sb-brand">
                <div class="sb-icon">🧠</div>
                <span class="sb-title">Syndesi</span>
            </div>
            <div class="sb-subtitle">Expert Network</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section-label">Recent Searches</div>', unsafe_allow_html=True)

    if not st.session_state.recent_searches:
        st.markdown(
            "<div class='sb-empty'>Your recent searches<br>will appear here</div>",
            unsafe_allow_html=True
        )
    else:
        for i, entry in enumerate(st.session_state.recent_searches):
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(
                    "<div class='sb-item'>"
                    "<div>"
                    "<div class='sb-item-label'>" + entry['label'] + "</div>"
                    "<div class='sb-item-time'>" + entry['time'] + "</div>"
                    "</div></div>",
                    unsafe_allow_html=True
                )
            with col2:
                if st.button("↩", key=f"restore_{i}", help="Jump back to this search"):
                    restore_search(entry)
                    st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("＋  New Search", key="sb_new", use_container_width=True):
        reset()
        st.rerun()

# ── HEADER ──
st.markdown("""
    <div class="chat-header">
        <div class="hdr-icon">🧠</div>
        <span class="hdr-name">Syndesi Assistant</span>
        <span class="hdr-badge">Expert Network</span>
    </div>
""", unsafe_allow_html=True)

# ── CHAT BODY START ──
st.markdown('<div class="chat-body">', unsafe_allow_html=True)

st.markdown("""
    <div class="bubble-bot">
        <div class="bot-av">🧠</div>
        <div class="bot-msg">Hi! I'm the <strong>Syndesi Assistant</strong>.<br>
        What area do you need expert help with today? Pick a category or type a keyword below.</div>
    </div>
""", unsafe_allow_html=True)

# ── STEP 1: CATEGORY ──
if st.session_state.step == "global_search":
    kw = st.session_state.search_query.strip()
    all_experts = df.to_dict("records") if df is not None else []
    filtered = [
        e for e in all_experts
        if kw.lower() in str(e.get("Speciality", "")).lower()
        or kw.lower() in str(e.get("Name", "")).lower()
        or kw.lower() in str(e.get("Company", "")).lower()
    ]
    count = len(filtered)
    st.markdown(f'<div class="user-bubble-wrap"><div class="user-msg">🔎 {kw}</div></div>', unsafe_allow_html=True)
    st.markdown(
        f"<div class='bubble-bot'><div class='bot-av'>🧠</div>"
        f"<div class='bot-msg'>I found <strong>{count} expert{'s' if count != 1 else ''}</strong> matching <em>{kw}</em>:</div></div>",
        unsafe_allow_html=True
    )
    if filtered:
        for expert in filtered:
            render_expert(expert)
    else:
        st.markdown("<div class='bubble-bot'><div class='bot-av'>🧠</div><div class='bot-msg'>No experts found for that keyword. Try something else.</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    if st.button("🔄 Start a new search", key="restart_global"):
        reset()
        st.rerun()

elif st.session_state.step == "category":
    categories = list(CATEGORY_MAP.keys())
    cols = st.columns(2)
    for i, cat in enumerate(categories):
        if cols[i % 2].button(cat, key=f"cat_{i}"):
            st.session_state.chosen_category = cat
            st.session_state.step = "subcategory"
            st.rerun()

# ── STEP 2: SUBCATEGORY ──
elif st.session_state.step == "subcategory":
    cat = st.session_state.chosen_category
    st.markdown(f'<div class="user-bubble-wrap"><div class="user-msg">{cat}</div></div>', unsafe_allow_html=True)
    subs = SUBCATEGORIES.get(cat, [])
    if subs:
        st.markdown("""
            <div class="bubble-bot">
                <div class="bot-av">🧠</div>
                <div class="bot-msg">Got it! Can you narrow it down a little?</div>
            </div>
        """, unsafe_allow_html=True)
        cols = st.columns(2)
        for i, (label, _kws) in enumerate(subs):
            if cols[i % 2].button(label, key=f"sub_{i}"):
                st.session_state.chosen_sub = label
                st.session_state.step = "results"
                add_recent(cat, label)
                st.rerun()
        st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)
        if st.button("👥 Show everyone in this area", key="show_all"):
            st.session_state.chosen_sub = "__all__"
            st.session_state.step = "results"
            add_recent(cat, "__all__")
            st.rerun()
    else:
        st.session_state.chosen_sub = "__all__"
        st.session_state.step = "results"
        add_recent(cat, "__all__")
        st.rerun()

# ── STEP 3: RESULTS ──
elif st.session_state.step == "results":
    cat = st.session_state.chosen_category
    sub = st.session_state.chosen_sub

    st.markdown(f'<div class="user-bubble-wrap"><div class="user-msg">{cat}</div></div>', unsafe_allow_html=True)
    if sub and sub != "__all__":
        st.markdown(f'<div class="user-bubble-wrap"><div class="user-msg">{sub}</div></div>', unsafe_allow_html=True)

    # Resolve base experts
    if sub == "__all__":
        experts = get_experts_for_names(CATEGORY_MAP.get(cat, []))
    else:
        subs = SUBCATEGORIES.get(cat, [])
        keywords = next((kws for lbl, kws in subs if lbl == sub), [])
        cat_names = CATEGORY_MAP.get(cat, [])
        cat_df = df[df["Name"].isin(cat_names)] if df is not None else pd.DataFrame()
        if not cat_df.empty and keywords:
            mask = cat_df["Speciality"].astype(str).apply(
                lambda s: any(k.lower() in s.lower() for k in keywords)
            )
            filtered = cat_df[mask]
            experts = filtered.to_dict("records") if not filtered.empty else cat_df.to_dict("records")
        else:
            experts = get_experts_for_names(cat_names)

    # Apply keyword filter from submitted search
    kw = st.session_state.search_query.strip()
    filtered_experts = experts
    if kw:
        filtered_experts = [
            e for e in experts
            if kw.lower() in str(e.get("Speciality", "")).lower()
            or kw.lower() in str(e.get("Name", "")).lower()
            or kw.lower() in str(e.get("Company", "")).lower()
        ]

    count = len(filtered_experts)
    kw_note = f" matching <em>{kw}</em>" if kw else ""
    st.markdown(
        f"<div class='bubble-bot'><div class='bot-av'>🧠</div>"
        f"<div class='bot-msg'>I found <strong>{count} expert{'s' if count != 1 else ''}</strong>"
        f"{kw_note}. Here {'they are' if count != 1 else 'they are'}:</div></div>",
        unsafe_allow_html=True
    )

    if filtered_experts:
        for expert in filtered_experts:
            render_expert(expert)
    else:
        st.markdown("""
            <div class="bubble-bot">
                <div class="bot-av">🧠</div>
                <div class="bot-msg">No results for that keyword. Try something different or clear the search below.</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    if st.button("🔄 Start a new search", key="restart"):
        reset()
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)  # close chat-body

# ── SEARCH INPUT ── native bottom bar, no gaps
query = st.chat_input("🔎  Search experts, e.g. 'capital allowance', 'probate', 'bridging'...")
if query:
    # If on results page, filter further; otherwise do a global search across all experts
    if st.session_state.step == "results":
        st.session_state.search_query = query
        st.rerun()
    else:
        # Global keyword search across all experts regardless of category
        st.session_state.search_query = query
        st.session_state.chosen_category = "⚖️ Legal"  # dummy, overridden below
        st.session_state.chosen_sub = "__all__"
        st.session_state.step = "global_search"
        st.rerun()

if err:
    st.warning(f"⚠️ Could not load live data: {err}")
