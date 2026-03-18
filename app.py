import streamlit as st
import pandas as pd

# ── CONFIG ──
SHEET_ID = "1mjEM2jJ69Qc0m5R1mdw6wjsPhRJ0mscNhMJLwNdRM7Q"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

st.set_page_config(page_title="Syndesi Assistant", page_icon="🧠", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    .stApp { background-color: #F7F7F8 !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .block-container { max-width: 780px !important; padding-top: 2rem !important; }

    /* Header */
    .syndesi-header {
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 8px; padding-bottom: 16px;
        border-bottom: 1px solid #E5E7EB;
    }
    .brain-icon {
        width: 38px; height: 38px; background: #E8651A; border-radius: 9px;
        display: flex; align-items: center; justify-content: center; font-size: 22px;
    }

    /* Intro */
    .intro-text {
        font-size: 15px; color: #6B7280; margin: 18px 0 20px;
        line-height: 1.6;
    }

    /* Pills */
    .pills-wrap { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 24px; }
    .pill {
        background: white; border: 1.5px solid #E5E7EB; border-radius: 999px;
        padding: 8px 18px; font-size: 13px; font-weight: 600; color: #374151;
        cursor: pointer; transition: all 0.15s;
    }
    .pill:hover { border-color: #E8651A; color: #E8651A; }
    .pill.active { background: #E8651A; border-color: #E8651A; color: white; }

    /* Search */
    .stTextInput input {
        border-radius: 10px !important; border: 1.5px solid #E5E7EB !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 14px !important; padding: 10px 14px !important;
    }
    .stTextInput input:focus { border-color: #E8651A !important; box-shadow: none !important; }

    /* Cards */
    .expert-card {
        background: white; border: 1px solid #E5E7EB; border-radius: 14px;
        padding: 20px 22px; margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s;
    }
    .expert-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.09); }
    .pill-tag {
        background: #FFF7ED; color: #E8651A; font-weight: 700;
        font-size: 10px; padding: 3px 10px; border-radius: 999px;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    .expert-name { font-weight: 700; font-size: 17px; margin: 8px 0 2px; color: #111827; }
    .expert-company { color: #6B7280; font-size: 13px; margin-bottom: 14px; }
    .btn-row { display: flex; gap: 8px; flex-wrap: wrap; }
    .btn-email {
        display: inline-block; background: #E8651A; color: white !important;
        padding: 8px 18px; border-radius: 8px; text-decoration: none;
        font-size: 13px; font-weight: 600;
    }
    .btn-phone {
        display: inline-block; background: white; color: #E8651A !important;
        border: 1.5px solid #E8651A; padding: 8px 18px; border-radius: 8px;
        text-decoration: none; font-size: 13px; font-weight: 600;
    }

    /* Empty state */
    .empty-state { text-align: center; padding: 56px 20px; }
    .empty-state .icon { font-size: 44px; margin-bottom: 14px; }
    .empty-state h4 { color: #374151; font-size: 16px; font-weight: 700; margin-bottom: 6px; }
    .empty-state p { color: #9CA3AF; font-size: 14px; }

    /* Result count */
    .result-count { color: #6B7280; font-size: 13px; margin-bottom: 14px; }
    .result-count b { color: #111827; }
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
    <div class="syndesi-header">
        <div class="brain-icon">🧠</div>
        <h3 style="margin:0; color:#111827; font-weight:700; font-size:20px;">Syndesi Assistant</h3>
    </div>
    <div class="intro-text">Find the right expert from the Syndesi network. Pick a speciality or search below.</div>
""", unsafe_allow_html=True)

if err or df is None or df.empty:
    st.error("Could not load network data. Please check the sheet is publicly accessible.")
    st.stop()

# ── STATE ──
if "selected_area" not in st.session_state:
    st.session_state.selected_area = None

# ── SPECIALITY PILLS ──
areas = sorted(df["Speciality"].dropna().unique().tolist())

# Render pills as buttons in columns
cols = st.columns(4)
for i, area in enumerate(areas):
    is_active = st.session_state.selected_area == area
    label = f"✓ {area}" if is_active else area
    if cols[i % 4].button(label, key=f"pill_{i}", use_container_width=True):
        if st.session_state.selected_area == area:
            st.session_state.selected_area = None  # toggle off
        else:
            st.session_state.selected_area = area
        st.rerun()

st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

# ── SEARCH ──
search = st.text_input("", placeholder="🔎  Search by name, company or keyword...", label_visibility="collapsed")

st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

# ── FILTER ──
results = df.copy()
active_search = search.strip()
active_area = st.session_state.selected_area

if active_search:
    mask = results.apply(lambda row: row.astype(str).str.contains(active_search, case=False, na=False).any(), axis=1)
    results = results[mask]
elif active_area:
    results = results[results["Speciality"].astype(str) == active_area]
else:
    results = pd.DataFrame()

# ── DISPLAY ──
if not results.empty:
    label = f"<b>{len(results)}</b> expert{'s' if len(results) > 1 else ''} found"
    if active_area and not active_search:
        label += f" in <b>{active_area}</b>"
    st.markdown(f"<div class='result-count'>{label}</div>", unsafe_allow_html=True)

    for _, row in results.iterrows():
        name       = str(row.get("Name", "")).strip()
        speciality = str(row.get("Speciality", "")).strip()
        company    = str(row.get("Company", "")).strip()
        email      = str(row.get("Email", "")).strip()
        phone      = str(row.get("Phone", "")).strip()

        email_btn = f'<a href="mailto:{email}?subject=Syndesi Network Inquiry" class="btn-email">✉ Email</a>' if email and email != "nan" else ""
        phone_btn = f'<a href="tel:{phone}" class="btn-phone">📞 {phone}</a>' if phone and phone != "nan" else ""

        st.markdown(f"""
            <div class="expert-card">
                <span class="pill-tag">{speciality}</span>
                <div class="expert-name">{name}</div>
                <div class="expert-company">{company}</div>
                <div class="btn-row">{email_btn}{phone_btn}</div>
            </div>
        """, unsafe_allow_html=True)

elif active_area or active_search:
    st.markdown("""
        <div class="empty-state">
            <div class="icon">🔍</div>
            <h4>No experts found</h4>
            <p>Try a different speciality or keyword</p>
        </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
        <div class="empty-state">
            <div class="icon">👆</div>
            <h4>Select a speciality to get started</h4>
            <p>Or type a keyword to search the full network</p>
        </div>
    """, unsafe_allow_html=True)
