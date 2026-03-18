import streamlit as st
import pandas as pd

SHEET_ID = "1mjEM2jJ69Qc0m5R1mdw6wjsPhRJ0mscNhMJLwNdRM7Q"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
SYNDESI_LINK = "https://app.syndesi.network/login"

st.set_page_config(page_title="Syndesi Assistant", page_icon="🧠", layout="centered")

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

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800&display=swap');

    * {{ box-sizing: border-box; }}
    .stApp {{ background: #F4F4F6 !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }}
    [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none !important; }}
    .block-container {{ max-width: 720px !important; padding: 0 0 90px 0 !important; margin: 0 auto; }}
    section[data-testid="stMain"] > div {{ padding: 0 !important; }}

    /* ── HEADER ── */
    .s-header {{
        position: sticky; top: 0; z-index: 100;
        background: white;
        border-bottom: 1px solid #EBEBED;
        padding: 14px 24px;
        display: flex; align-items: center; gap: 12px;
        box-shadow: 0 1px 12px rgba(0,0,0,0.06);
    }}
    .brand-mark {{
        width: 36px; height: 36px; background: linear-gradient(135deg, #E8651A, #F0853A);
        border-radius: 10px; display: flex; align-items: center; justify-content: center;
        font-size: 20px; box-shadow: 0 2px 8px rgba(232,101,26,0.35);
    }}
    .brand-name {{
        font-weight: 800; font-size: 17px; color: #0F0F0F; letter-spacing: -0.3px;
    }}
    .brand-sub {{
        font-size: 11px; color: #9CA3AF; font-weight: 500; margin-left: auto;
        background: #F4F4F6; padding: 3px 10px; border-radius: 20px;
    }}

    /* ── CHAT AREA ── */
    /* Bot bubble */
    .bubble-bot {{ display: flex; gap: 10px; align-items: flex-end; margin-bottom: 16px; }}
    .bot-av {{
        width: 30px; height: 30px; background: linear-gradient(135deg, #E8651A, #F0853A);
        border-radius: 8px; display: flex; align-items: center; justify-content: center;
        font-size: 15px; flex-shrink: 0; box-shadow: 0 2px 6px rgba(232,101,26,0.3);
    }}
    .bot-msg {{
        background: white; border: 1px solid #EBEBED;
        border-radius: 4px 16px 16px 16px;
        padding: 12px 16px; font-size: 14px; color: #1A1A1A; line-height: 1.65;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05); max-width: 82%;
        font-weight: 450;
    }}

    /* User bubble */
    .user-bubble-wrap {{ display: flex; justify-content: flex-end; margin-bottom: 16px; }}
    .user-msg {{
        background: linear-gradient(135deg, #E8651A, #D45515);
        color: white; border-radius: 16px 4px 16px 16px;
        padding: 11px 16px; font-size: 14px; font-weight: 500;
        max-width: 72%; line-height: 1.5;
        box-shadow: 0 2px 10px rgba(232,101,26,0.3);
    }}

    /* ── OPTION BUTTONS ── */
    .options-wrap {{ margin: 4px 0 20px 40px; display: flex; flex-wrap: wrap; gap: 8px; }}
    div[data-testid="stHorizontalBlock"] .stButton > button {{
        background: white !important;
        border: 1.5px solid #E2E2E6 !important;
        border-radius: 10px !important;
        color: #2D2D2D !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 9px 14px !important;
        width: 100% !important;
        text-align: left !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    }}
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {{
        border-color: #E8651A !important;
        color: #E8651A !important;
        box-shadow: 0 2px 8px rgba(232,101,26,0.15) !important;
        transform: translateY(-1px) !important;
    }}

    /* Show all / restart buttons */
    div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] > button {{
        background: transparent !important;
        border: 1.5px solid #E2E2E6 !important;
        border-radius: 10px !important;
        color: #6B7280 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important; font-size: 13px !important;
        padding: 9px 18px !important;
        transition: all 0.15s !important;
    }}
    div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] > button:hover {{
        border-color: #E8651A !important; color: #E8651A !important;
    }}

    /* ── EXPERT CARD ── */
    .expert-card {{
        background: white;
        border: 1px solid #EBEBED;
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 10px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        transition: box-shadow 0.2s, transform 0.2s;
    }}
    .expert-card:hover {{
        box-shadow: 0 6px 20px rgba(0,0,0,0.09);
        transform: translateY(-1px);
    }}
    .expert-header {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }}
    .expert-initials {{
        width: 44px; height: 44px; border-radius: 12px;
        background: linear-gradient(135deg, #FFF0E6, #FFD9BE);
        color: #E8651A; font-weight: 800; font-size: 15px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0; letter-spacing: -0.5px;
    }}
    .expert-info {{ flex: 1; }}
    .expert-name {{ font-weight: 700; font-size: 16px; color: #0F0F0F; margin-bottom: 2px; }}
    .expert-co {{ color: #6B7280; font-size: 12.5px; font-weight: 500; }}
    .spec-tag {{
        display: inline-block;
        background: #FFF7ED; color: #C05C17;
        font-size: 10.5px; font-weight: 700;
        padding: 3px 10px; border-radius: 20px;
        text-transform: uppercase; letter-spacing: 0.5px;
        margin: 12px 0 14px;
        border: 1px solid #FDDCBC;
    }}
    .contact-row {{
        display: flex; flex-direction: column; gap: 6px;
        margin-bottom: 14px;
    }}
    .contact-item {{
        display: flex; align-items: center; gap: 8px;
        font-size: 13px; color: #374151; font-weight: 500;
    }}
    .contact-icon {{
        width: 26px; height: 26px; background: #F4F4F6; border-radius: 6px;
        display: flex; align-items: center; justify-content: center; font-size: 13px;
        flex-shrink: 0;
    }}
    .contact-text {{ color: #374151; font-size: 13px; font-weight: 500; }}
    .syndesi-btn {{
        display: inline-flex; align-items: center; gap: 7px;
        background: linear-gradient(135deg, #E8651A, #D45515);
        color: white !important; text-decoration: none;
        padding: 9px 18px; border-radius: 10px;
        font-size: 13px; font-weight: 700;
        box-shadow: 0 2px 10px rgba(232,101,26,0.35);
        transition: all 0.15s; letter-spacing: 0.1px;
    }}
    .syndesi-btn:hover {{
        box-shadow: 0 4px 16px rgba(232,101,26,0.45);
        transform: translateY(-1px);
        color: white !important;
    }}

    /* ── CHAT INPUT AREA ── */
    .input-area {{
        background: white;
        border-top: 1px solid #EBEBED;
        padding: 14px 20px 10px;
        margin-top: 8px;
    }}
    .stTextInput > div > div > input {{
        border-radius: 12px !important;
        border: 1.5px solid #E2E2E6 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 14px !important;
        padding: 11px 16px !important;
        background: #F9F9FB !important;
        color: #1A1A1A !important;
        transition: border-color 0.15s !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: #E8651A !important;
        box-shadow: 0 0 0 3px rgba(232,101,26,0.1) !important;
        background: white !important;
    }}
    .stTextInput > div > div > input::placeholder {{
        color: #ABABAB !important; font-weight: 400 !important;
    }}
    .stTextInput label {{ display: none !important; }}

    .divider {{ border: none; border-top: 1px solid #EBEBED; margin: 20px 0 16px; }}
</style>
""", unsafe_allow_html=True)

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

# ── HEADER ──
st.markdown("""
    <div class="s-header">
        <div class="brand-mark">🧠</div>
        <span class="brand-name">Syndesi Assistant</span>
        <span class="brand-sub">Expert Network</span>
    </div>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
for key, default in [("step","category"),("chosen_category",None),("chosen_sub",None),("keyword","")]:
    if key not in st.session_state:
        st.session_state[key] = default

def reset():
    st.session_state.step = "category"
    st.session_state.chosen_category = None
    st.session_state.chosen_sub = None
    st.session_state.keyword = ""

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

    email_html = f'''
        <div class="contact-item">
            <div class="contact-icon">✉️</div>
            <span class="contact-text">{email}</span>
        </div>''' if email and email != "nan" else ""

    phone_html = f'''
        <div class="contact-item">
            <div class="contact-icon">📞</div>
            <span class="contact-text">{phone}</span>
        </div>''' if phone and phone != "nan" else ""

    card_html = f'''
        <div class="expert-card">
            <div class="expert-header">
                <div class="expert-initials">{initials(name)}</div>
                <div class="expert-info">
                    <div class="expert-name">{name}</div>
                    <div class="expert-co">{company}</div>
                </div>
            </div>
            <div class="spec-tag">{speciality[:60]}</div>
            <div class="contact-row">
                {email_html}
                {phone_html}
            </div>
            <a href="{SYNDESI_LINK}" target="_blank" class="syndesi-btn">&#128279; Contact on Syndesi</a>
        </div>
    '''
    st.markdown(card_html, unsafe_allow_html=True)

# ── CHAT AREA ──
# Opening message
st.markdown("""
    <div class="bubble-bot">
        <div class="bot-av">🧠</div>
        <div class="bot-msg">Hi! I'm the <strong>Syndesi Assistant</strong>.<br>What area do you need expert help with today?</div>
    </div>
""", unsafe_allow_html=True)

# ── STEP 1: CATEGORY ──
if st.session_state.step == "category":
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
                st.rerun()
        st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)
        if st.button("👥 Show everyone in this area", key="show_all"):
            st.session_state.chosen_sub = "__all__"
            st.session_state.step = "results"
            st.rerun()
    else:
        st.session_state.chosen_sub = "__all__"
        st.session_state.step = "results"
        st.rerun()

# ── STEP 3: RESULTS ──
elif st.session_state.step == "results":
    cat = st.session_state.chosen_category
    sub = st.session_state.chosen_sub

    st.markdown(f'<div class="user-bubble-wrap"><div class="user-msg">{cat}</div></div>', unsafe_allow_html=True)
    if sub and sub != "__all__":
        st.markdown(f'<div class="user-bubble-wrap"><div class="user-msg">{sub}</div></div>', unsafe_allow_html=True)

    # Resolve experts
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

    # Keyword filter from chat input
    kw = st.session_state.get("keyword", "").strip()
    if kw:
        experts = [e for e in experts if kw.lower() in str(e.get("Speciality","")).lower()
                   or kw.lower() in str(e.get("Name","")).lower()
                   or kw.lower() in str(e.get("Company","")).lower()]

    count = len(experts)
    st.markdown(f"""
        <div class="bubble-bot">
            <div class="bot-av">🧠</div>
            <div class="bot-msg">I found <strong>{count} expert{'s' if count != 1 else ''}</strong> for you{' matching <em>' + kw + '</em>' if kw else ''}. Here {'they are' if count != 1 else 'they are'}:</div>
        </div>
    """, unsafe_allow_html=True)

    if experts:
        for expert in experts:
            render_expert(expert)
    else:
        st.markdown("""
            <div class="bubble-bot">
                <div class="bot-av">🧠</div>
                <div class="bot-msg">No results found for that keyword. Try something else or clear the search.</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    if st.button("🔄 Start a new search", key="restart"):
        reset()
        st.rerun()

# ── INPUT ──
st.markdown('<div class="input-area">', unsafe_allow_html=True)
keyword = st.text_input(
    "keyword",
    value=st.session_state.get("keyword", ""),
    placeholder="💬 Type a keyword to filter results, e.g. 'capital allowance', 'probate'...",
    key="keyword_input"
)
if keyword != st.session_state.get("keyword", ""):
    st.session_state.keyword = keyword
    if st.session_state.step == "results":
        st.rerun()
if err:
    st.warning(f"⚠️ Could not load live data: {err}")
