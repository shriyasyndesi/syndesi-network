import streamlit as st
import pandas as pd

SHEET_ID = "1mjEM2jJ69Qc0m5R1mdw6wjsPhRJ0mscNhMJLwNdRM7Q"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

st.set_page_config(page_title="Syndesi Assistant", page_icon="🧠", layout="centered")

# ── CATEGORY MAPPING ──
# Maps each person to a top-level category based on their speciality keywords
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
        "David Forsdyke", "Hass Draper", "John Kent", "Joshua David",
        "Laura Fisher"
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

# Subcategory hints shown after a category is picked
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

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F7F7F8 !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { max-width: 780px !important; padding-top: 1.5rem !important; }

    .s-header {
        display: flex; align-items: center; gap: 12px;
        padding-bottom: 16px; margin-bottom: 4px;
        border-bottom: 1px solid #E5E7EB;
    }
    .brain-icon {
        width: 38px; height: 38px; background: #E8651A; border-radius: 9px;
        display: flex; align-items: center; justify-content: center; font-size: 22px;
    }

    /* Chat bubbles */
    .bubble-bot {
        display: flex; gap: 10px; margin-bottom: 18px; align-items: flex-start;
    }
    .bot-avatar {
        width: 32px; height: 32px; background: #E8651A; border-radius: 7px;
        display: flex; align-items: center; justify-content: center;
        font-size: 17px; flex-shrink: 0; margin-top: 2px;
    }
    .bot-msg {
        background: white; border: 1px solid #E5E7EB; border-radius: 0 14px 14px 14px;
        padding: 12px 16px; font-size: 15px; color: #111827; line-height: 1.6;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05); max-width: 85%;
    }
    .user-msg {
        background: #E8651A; color: white; border-radius: 14px 14px 0 14px;
        padding: 10px 16px; font-size: 15px; margin-left: auto;
        max-width: 75%; margin-bottom: 18px; line-height: 1.5;
    }

    /* Expert card */
    .expert-card {
        background: white; border: 1px solid #E5E7EB; border-radius: 14px;
        padding: 18px 20px; margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .pill-tag {
        background: #FFF7ED; color: #E8651A; font-weight: 700;
        font-size: 10px; padding: 3px 10px; border-radius: 999px;
        text-transform: uppercase; letter-spacing: 0.4px;
    }
    .expert-name { font-weight: 700; font-size: 16px; margin: 8px 0 2px; color: #111827; }
    .expert-co { color: #6B7280; font-size: 13px; margin-bottom: 12px; }
    .btn-email {
        display: inline-block; background: #E8651A; color: white !important;
        padding: 7px 16px; border-radius: 7px; text-decoration: none;
        font-size: 13px; font-weight: 600; margin-right: 8px;
    }
    .btn-phone {
        display: inline-block; background: white; color: #E8651A !important;
        border: 1.5px solid #E8651A; padding: 7px 16px; border-radius: 7px;
        text-decoration: none; font-size: 13px; font-weight: 600;
    }

    /* Streamlit button overrides for pills */
    div[data-testid="stHorizontalBlock"] .stButton button {
        background: white !important; border: 1.5px solid #E5E7EB !important;
        border-radius: 999px !important; color: #374151 !important;
        font-weight: 600 !important; font-size: 13px !important;
        padding: 6px 14px !important; transition: all 0.15s !important;
        width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton button:hover {
        border-color: #E8651A !important; color: #E8651A !important;
    }

    .divider { border: none; border-top: 1px solid #E5E7EB; margin: 16px 0; }
    .section-label { color: #9CA3AF; font-size: 12px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 10px; }
    .restart-hint { color: #9CA3AF; font-size: 12px; margin-top: 20px; text-align: center; }
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
        <div class="brain-icon">🧠</div>
        <h3 style="margin:0; color:#111827; font-weight:700; font-size:19px;">Syndesi Assistant</h3>
    </div>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
if "step" not in st.session_state:
    st.session_state.step = "category"
if "chosen_category" not in st.session_state:
    st.session_state.chosen_category = None
if "chosen_sub" not in st.session_state:
    st.session_state.chosen_sub = None

def reset():
    st.session_state.step = "category"
    st.session_state.chosen_category = None
    st.session_state.chosen_sub = None

def get_experts_for_names(names):
    if df is None:
        return []
    return df[df["Name"].isin(names)].to_dict("records")

def get_experts_for_keywords(keywords):
    if df is None:
        return []
    mask = df["Speciality"].astype(str).apply(
        lambda s: any(k.lower() in s.lower() for k in keywords)
    )
    return df[mask].to_dict("records")

def render_expert(expert):
    name = str(expert.get("Name", "")).strip()
    company = str(expert.get("Company", "")).strip()
    speciality = str(expert.get("Speciality", "")).strip()
    email = str(expert.get("Email", "")).strip()
    phone = str(expert.get("Phone", "")).strip()

    email_btn = f'<a href="mailto:{email}?subject=Syndesi Network Inquiry" class="btn-email">✉ Email</a>' if email and email != "nan" else ""
    phone_btn = f'<a href="tel:{phone}" class="btn-phone">📞 Call</a>' if phone and phone != "nan" else ""

    st.markdown(f"""
        <div class="expert-card">
            <span class="pill-tag">{speciality[:50]}</span>
            <div class="expert-name">{name}</div>
            <div class="expert-co">{company}</div>
            {email_btn}{phone_btn}
        </div>
    """, unsafe_allow_html=True)

# ── STEP 1: CATEGORY ──
st.markdown("""
    <div class="bubble-bot">
        <div class="bot-avatar">🧠</div>
        <div class="bot-msg">Hi! I'm the Syndesi Assistant. What area do you need help with?</div>
    </div>
""", unsafe_allow_html=True)

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

    # Show user's choice as a chat bubble
    st.markdown(f'<div class="user-msg">{cat}</div>', unsafe_allow_html=True)

    # Check if subcategories exist
    subs = SUBCATEGORIES.get(cat, [])

    if subs:
        st.markdown(f"""
            <div class="bubble-bot">
                <div class="bot-avatar">🧠</div>
                <div class="bot-msg">Great! Can you be a bit more specific?</div>
            </div>
        """, unsafe_allow_html=True)

        cols = st.columns(2)
        for i, (label, _keywords) in enumerate(subs):
            if cols[i % 2].button(label, key=f"sub_{i}"):
                st.session_state.chosen_sub = label
                st.session_state.step = "results"
                st.rerun()

        # Also option to see all in category
        st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
        if st.button("👥 Show all in this category", key="show_all"):
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

    st.markdown(f'<div class="user-msg">{cat}</div>', unsafe_allow_html=True)

    if sub and sub != "__all__":
        st.markdown(f'<div class="user-msg">{sub}</div>', unsafe_allow_html=True)

    # Find matching keywords for sub
    experts = []
    if sub == "__all__":
        names = CATEGORY_MAP.get(cat, [])
        experts = get_experts_for_names(names)
    else:
        subs = SUBCATEGORIES.get(cat, [])
        keywords = []
        for label, kws in subs:
            if label == sub:
                keywords = kws
                break
        # Filter from the category names only
        cat_names = CATEGORY_MAP.get(cat, [])
        cat_df = df[df["Name"].isin(cat_names)] if df is not None else pd.DataFrame()
        if not cat_df.empty and keywords:
            mask = cat_df["Speciality"].astype(str).apply(
                lambda s: any(k.lower() in s.lower() for k in keywords)
            )
            filtered = cat_df[mask]
            # fallback: show all in category if no keyword match
            experts = filtered.to_dict("records") if not filtered.empty else cat_df.to_dict("records")
        else:
            experts = get_experts_for_names(cat_names)

    count = len(experts)
    st.markdown(f"""
        <div class="bubble-bot">
            <div class="bot-avatar">🧠</div>
            <div class="bot-msg">I found <b>{count} expert{'s' if count != 1 else ''}</b> that can help you. Here {'they are' if count != 1 else 'they are'}:</div>
        </div>
    """, unsafe_allow_html=True)

    if experts:
        for expert in experts:
            render_expert(expert)
    else:
        st.markdown("""
            <div class="bubble-bot">
                <div class="bot-avatar">🧠</div>
                <div class="bot-msg">Sorry, I couldn't find anyone for that area right now.</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    if st.button("🔄 Start over", key="restart"):
        reset()
        st.rerun()

if err:
    st.warning(f"⚠️ Could not load live data: {err}. Showing cached data if available.")
