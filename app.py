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
    .block-container { max-width: 800px !important; padding-top: 2rem !important; }
    .expert-card {
        background: white; border: 1px solid #E5E7EB; border-radius: 12px;
        padding: 20px; margin-top: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.06);
    }
    .expert-tag {
        background: #FFF7ED; color: #E8651A; font-weight: 700;
        font-size: 10px; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;
    }
    .connect-btn {
        display: inline-block; background: #E8651A; color: white !important;
        padding: 8px 16px; border-radius: 8px; text-decoration: none;
        font-size: 13px; font-weight: 600; margin-top: 12px; margin-right: 8px;
    }
    .phone-btn {
        display: inline-block; background: white; color: #E8651A !important;
        border: 1.5px solid #E8651A; padding: 8px 16px; border-radius: 8px; text-decoration: none;
        font-size: 13px; font-weight: 600; margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_professionals():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip() for c in df.columns]
        return df.dropna(how="all"), None
    except Exception as e:
        return None, str(e)

# ── HEADER ──
st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:30px;
                border-bottom:1px solid #E5E7EB; padding-bottom:15px;">
        <div style="width:36px; height:36px; background:#E8651A; border-radius:8px;
                    display:flex; align-items:center; justify-content:center; font-size:20px;">🧠</div>
        <h3 style="margin:0; color:#111827; font-weight:700;">Syndesi Assistant</h3>
    </div>
""", unsafe_allow_html=True)

# ── LOAD ──
df, err = load_professionals()
if err:
    st.error(f"Could not load network data: {err}")
    st.stop()
if df is None or df.empty:
    st.warning("No professionals found in the sheet.")
    st.stop()

# ── FILTER UI ──
areas = sorted(df["Speciality"].dropna().unique().tolist())

st.markdown("<p style='color:#6B7280; font-size:14px; margin-bottom:4px;'>Browse by speciality</p>", unsafe_allow_html=True)
selected_area = st.selectbox("Speciality", ["— Select an area —"] + areas, label_visibility="collapsed")

st.markdown("<p style='color:#6B7280; font-size:14px; margin:12px 0 4px;'>Or search by keyword</p>", unsafe_allow_html=True)
search = st.text_input("Search", placeholder="e.g. capital allowance, tax, property...", label_visibility="collapsed")

# ── FILTER LOGIC ──
results = df.copy()
if search.strip():
    mask = results.apply(lambda row: row.astype(str).str.contains(search.strip(), case=False, na=False).any(), axis=1)
    results = results[mask]
elif selected_area != "— Select an area —":
    results = results[results["Speciality"].astype(str).str.contains(selected_area, case=False, na=False)]
else:
    results = pd.DataFrame()  # nothing selected yet

# ── RESULTS ──
if not results.empty:
    st.markdown(f"<p style='color:#6B7280; font-size:13px; margin-top:16px;'>Found <b>{len(results)}</b> professional(s)</p>", unsafe_allow_html=True)
    for _, row in results.iterrows():
        name       = str(row.get("Name", "")).strip()
        speciality = str(row.get("Speciality", "")).strip()
        company    = str(row.get("Company", "")).strip()
        email      = str(row.get("Email", "")).strip()
        phone      = str(row.get("Phone", "")).strip()

        email_btn = f'<a href="mailto:{email}?subject=Syndesi Network Inquiry" class="connect-btn">✉ Email</a>' if email and email != "nan" else ""
        phone_btn = f'<a href="tel:{phone}" class="phone-btn">📞 Call</a>' if phone and phone != "nan" else ""

        st.markdown(f"""
            <div class="expert-card">
                <span class="expert-tag">{speciality}</span>
                <div style="font-weight:700; font-size:17px; margin:8px 0 2px;">{name}</div>
                <div style="color:#6B7280; font-size:13px; margin-bottom:10px;">{company}</div>
                {email_btn}{phone_btn}
            </div>
        """, unsafe_allow_html=True)

elif selected_area != "— Select an area —" or search.strip():
    st.markdown("""
        <div style='text-align:center; padding:40px; color:#9CA3AF;'>
            <div style='font-size:32px;'>🔍</div>
            <p>No professionals found. Try a different keyword.</p>
        </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
        <div style='text-align:center; padding:60px 20px;'>
            <div style='font-size:48px; margin-bottom:16px;'>🧠</div>
            <p style='font-size:16px; color:#6B7280; font-weight:600;'>Find the right expert for your needs</p>
            <p style='font-size:14px; color:#9CA3AF;'>Select a speciality or search by keyword above</p>
        </div>
    """, unsafe_allow_html=True)
