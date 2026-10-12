import html
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
API_URL = os.environ.get("API_URL", "http://localhost:8084")
TIMEOUT = 10

st.set_page_config(
    page_title="EduTrack · Student Records",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

ACCENT = "#0F766E"        # deep teal
ACCENT_SOFT = "#CCFBF1"
INK = "#1C1917"
MUTED = "#78716C"
LINE = "#E7E5E0"
PAPER = "#F6F5F1"

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600&display=swap');

html, body, [class*="css"], .stApp {{ font-family: 'Inter', sans-serif; color: {INK}; }}
.stApp {{ background: {PAPER}; }}
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2.2rem; max-width: 1180px; }}

/* Sidebar */
section[data-testid="stSidebar"] {{ background: #FFFFFF; border-right: 1px solid {LINE}; }}
.brand {{ display:flex; align-items:center; gap:10px; margin: 4px 0 22px; }}
.brand-mark {{ width:38px; height:38px; border-radius:10px; background:{ACCENT};
              color:#fff; display:flex; align-items:center; justify-content:center;
              font-family:'Fraunces',serif; font-size:20px; }}
.brand-name {{ font-family:'Fraunces',serif; font-size:21px; line-height:1; }}
.brand-tag {{ font-size:12px; color:{MUTED}; margin-top:3px; }}
section[data-testid="stSidebar"] div[role="radiogroup"] label {{
    padding: 9px 12px; border-radius: 9px; margin-bottom: 2px; width: 100%;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{ background: {PAPER}; }}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
    background: {ACCENT_SOFT}; color: {ACCENT}; font-weight: 600;
}}
.status {{ font-size:13px; padding:10px 12px; border-radius:10px; border:1px solid {LINE}; }}
.dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; }}

/* Page header */
.page-head {{ display:flex; justify-content:space-between; align-items:flex-end;
             border-bottom:1px solid {LINE}; padding-bottom:18px; margin-bottom:26px; gap:16px; flex-wrap:wrap; }}
.eyebrow {{ font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:{ACCENT}; font-weight:600; }}
.page-title {{ font-family:'Fraunces',serif; font-size:36px; margin:4px 0 4px; color:{INK}; }}
.page-sub {{ color:{MUTED}; font-size:15px; margin:0; }}
.date-chip {{ font-size:13px; color:{MUTED}; background:#fff; border:1px solid {LINE};
             padding:6px 12px; border-radius:999px; white-space:nowrap; }}

/* Cards */
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div[data-testid="stVerticalBlock"]) {{
    background:#FFFFFF; border-color:{LINE} !important; border-radius:14px;
}}
.stat {{ background:#fff; border:1px solid {LINE}; border-radius:14px; padding:18px 20px; }}
.stat-label {{ font-size:13px; color:{MUTED}; font-weight:500; }}
.stat-value {{ font-family:'Fraunces',serif; font-size:34px; margin-top:6px; color:{INK}; }}
.stat-note {{ font-size:12px; color:{ACCENT}; margin-top:2px; }}
.profile {{ display:flex; align-items:center; gap:16px; }}
.avatar {{ width:56px; height:56px; border-radius:50%; background:{ACCENT_SOFT}; color:{ACCENT};
           display:flex; align-items:center; justify-content:center; font-weight:700; font-size:20px; }}
.profile-name {{ font-size:20px; font-weight:600; }}
.profile-meta {{ color:{MUTED}; font-size:14px; }}
.row-item {{ display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid {LINE}; font-size:14px; }}
.row-item:last-child {{ border-bottom:none; }}
.hint {{ font-size:13px; color:{MUTED}; line-height:1.7; }}
.section-title {{ font-weight:600; font-size:15px; margin-bottom:8px; }}

/* Inputs & buttons */
.stTextInput input, .stNumberInput input {{ border-radius:10px !important; }}
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{
    border-radius:10px; font-weight:600; padding:0.55rem 1.1rem;
}}
button[kind="primary"], button[kind="primaryFormSubmit"] {{ background:{ACCENT} !important; border-color:{ACCENT} !important; }}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {{ background:#115E59 !important; }}

.app-foot {{ text-align:center; color:{MUTED}; font-size:12px; margin-top:48px; padding-top:18px; border-top:1px solid {LINE}; }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def _path(name: str) -> str:
    return requests.utils.quote(name, safe="")


@st.cache_data(ttl=15, show_spinner=False)
def fetch_students():
    r = requests.get(f"{API_URL}/student/all", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json() or []


def refresh_data():
    fetch_students.clear()


def flash(kind: str, msg: str):
    st.session_state["flash"] = (kind, msg)


def show_flash():
    if "flash" in st.session_state:
        kind, msg = st.session_state.pop("flash")
        st.toast(msg, icon="✅" if kind == "success" else "⚠️")


def page_header(eyebrow: str, title: str, subtitle: str):
    today = datetime.now().strftime("%a, %d %b %Y")
    st.markdown(f"""
    <div class="page-head">
      <div>
        <div class="eyebrow">{eyebrow}</div>
        <div class="page-title">{title}</div>
        <p class="page-sub">{subtitle}</p>
      </div>
      <div class="date-chip">📅 {today}</div>
    </div>""", unsafe_allow_html=True)


def stat(label, value, note=""):
    st.markdown(f"""
    <div class="stat">
      <div class="stat-label">{label}</div>
      <div class="stat-value">{value}</div>
      <div class="stat-note">{note}&nbsp;</div>
    </div>""", unsafe_allow_html=True)


def initials(name: str) -> str:
    parts = [p for p in str(name).split() if p]
    return html.escape("".join(p[0] for p in parts[:2]).upper() or "?")


def style_fig(fig, height=330):
    fig.update_layout(
        template="simple_white", height=height,
        margin=dict(l=10, r=10, t=46, b=10),
        font=dict(family="Inter, sans-serif", color="#44403C", size=12),
        title_font=dict(size=15, color=INK),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, linecolor=LINE)
    fig.update_yaxes(showgrid=True, gridcolor="#EEECE7", linecolor=LINE)
    return fig


# ---------------------------------------------------------------------------
# Data load (once per run)
# ---------------------------------------------------------------------------
try:
    students = fetch_students()
    online, load_error = True, None
except requests.exceptions.RequestException as e:
    students, online, load_error = [], False, str(e)

df_all = pd.DataFrame(students) if students else pd.DataFrame(columns=["name", "age"])
if "age" in df_all:
    df_all["age"] = pd.to_numeric(df_all["age"], errors="coerce")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-mark">E</div>
      <div><div class="brand-name">EduTrack</div><div class="brand-tag">Student records</div></div>
    </div>""", unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["Add student", "Find & remove", "Directory", "Edit record", "Insights"],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    dot = "#16A34A" if online else "#DC2626"
    state = f"Connected · {len(students)} records" if online else "Backend unreachable"
    st.markdown(f'<div class="status"><span class="dot" style="background:{dot}"></span>{state}</div>',
                unsafe_allow_html=True)
    st.caption(f"API: `{API_URL}`")
    if st.button("↻ Refresh data", use_container_width=True):
        refresh_data()
        st.rerun()

show_flash()

if not online:
    st.error(f"Can't reach the backend at {API_URL}. Check that the Spring Boot service is running.\n\n{load_error}")


# ---------------------------------------------------------------------------
# Page: Add student
# ---------------------------------------------------------------------------
if page == "Add student":
    page_header("Registration", "Add a student", "Create a new record in the student database.")
    left, right = st.columns([3, 2], gap="large")

    with left:
        with st.container(border=True):
            with st.form("add_student_form", clear_on_submit=True, border=False):
                name = st.text_input("Full name", placeholder="e.g. Priya Sharma")
                age = st.number_input("Age", min_value=1, max_value=100, value=18)
                submitted = st.form_submit_button("Add student", type="primary")

            if submitted:
                if not name.strip():
                    st.warning("Please enter the student's name.")
                else:
                    try:
                        r = requests.post(f"{API_URL}/student/post",
                                          json={"name": name.strip(), "age": int(age)}, timeout=TIMEOUT)
                        if r.status_code == 200:
                            refresh_data()
                            flash("success", f"Added {name.strip()}")
                            st.rerun()
                        else:
                            st.error(f"Server returned {r.status_code}: {r.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Connection error: {e}")

    with right:
        with st.container(border=True):
            st.markdown('<div class="section-title">Latest entries</div>', unsafe_allow_html=True)
            if students:
                rows = "".join(
                    f'<div class="row-item"><span>{html.escape(str(s.get("name", "—")))}</span>'
                    f'<span style="color:{MUTED}">{s.get("age", "—")} yrs</span></div>'
                    for s in list(reversed(students))[:5]
                )
                st.markdown(rows, unsafe_allow_html=True)
            else:
                st.markdown('<div class="hint">No students yet. Your first entry will show up here.</div>',
                            unsafe_allow_html=True)
        st.markdown('<div class="hint" style="margin-top:12px">Names are case-sensitive and used as the '
                    'lookup key, so keep them unique. Age must be between 1 and 100.</div>',
                    unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page: Find & remove
# ---------------------------------------------------------------------------
elif page == "Find & remove":
    page_header("Lookup", "Find a student", "Search by exact name to view or remove a record.")
    left, right = st.columns([3, 2], gap="large")

    with left:
        with st.container(border=True):
            search_name = st.text_input("Student name", placeholder="Exact, case-sensitive name")
            confirm = st.checkbox("Allow permanent deletion")
            b1, b2, _ = st.columns([1, 1, 2])
            search_btn = b1.button("Search", type="primary", use_container_width=True)
            delete_btn = b2.button("Delete", use_container_width=True, disabled=not confirm)

        if search_btn:
            if not search_name.strip():
                st.warning("Enter a name to search.")
            else:
                try:
                    r = requests.get(f"{API_URL}/student/get/{_path(search_name.strip())}", timeout=TIMEOUT)
                    student = None
                    if r.status_code == 200 and r.text.strip():
                        try:
                            student = r.json()
                        except ValueError:
                            student = None
                    if student:
                        with st.container(border=True):
                            nm = html.escape(str(student.get("name", "N/A")))
                            st.markdown(f"""
                            <div class="profile">
                              <div class="avatar">{initials(student.get("name", ""))}</div>
                              <div>
                                <div class="profile-name">{nm}</div>
                                <div class="profile-meta">Age {student.get("age", "N/A")} years</div>
                              </div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.warning(f"No student named '{search_name}'. Check spelling and capitalisation.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")

        if delete_btn:
            if not search_name.strip():
                st.warning("Enter the name of the student to delete.")
            else:
                try:
                    r = requests.delete(f"{API_URL}/student/delete/{_path(search_name.strip())}", timeout=TIMEOUT)
                    if r.status_code == 200:
                        refresh_data()
                        flash("success", f"Removed {search_name.strip()}")
                        st.rerun()
                    else:
                        st.error(f"Server returned {r.status_code}: {r.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")

    with right:
        with st.container(border=True):
            st.markdown('<div class="section-title">Good to know</div>', unsafe_allow_html=True)
            st.markdown('<div class="hint">• Names must match exactly, including case.<br>'
                        '• Tick <b>Allow permanent deletion</b> to unlock Delete.<br>'
                        '• Deleted records cannot be recovered.<br>'
                        '• Browse the Directory to see available names.</div>',
                        unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page: Directory
# ---------------------------------------------------------------------------
elif page == "Directory":
    page_header("Records", "Student directory", "Every registered student, filterable and exportable.")

    if df_all.empty:
        with st.container(border=True):
            st.markdown('<div class="hint">No students in the database yet. '
                        'Head to <b>Add student</b> to create the first record.</div>', unsafe_allow_html=True)
    else:
        f1, f2, f3 = st.columns([2, 2, 1], gap="medium")
        query = f1.text_input("Filter by name", placeholder="Type to filter…")
        ages = df_all["age"].dropna()
        lo, hi = (int(ages.min()), int(ages.max())) if not ages.empty else (1, 100)
        age_range = f2.slider("Age range", 1, 100, (lo, hi)) if lo != hi else (lo, hi)

        view = df_all[["name", "age"]].copy()
        if query:
            view = view[view["name"].astype(str).str.contains(query, case=False, na=False)]
        view = view[view["age"].between(age_range[0], age_range[1])]

        f3.markdown(f'<div class="stat" style="padding:10px 14px"><div class="stat-label">Showing</div>'
                    f'<div class="stat-value" style="font-size:24px;margin-top:0">{len(view)} / {len(df_all)}</div></div>',
                    unsafe_allow_html=True)

        st.dataframe(
            view,
            use_container_width=True,
            hide_index=True,
            height=440,
            column_config={
                "name": st.column_config.TextColumn("Name"),
                "age": st.column_config.NumberColumn("Age", format="%d yrs"),
            },
        )

        st.download_button(
            "Export CSV",
            data=view.rename(columns={"name": "Name", "age": "Age"}).to_csv(index=False).encode("utf-8"),
            file_name=f"students_{datetime.now():%Y%m%d_%H%M%S}.csv",
            mime="text/csv",
        )


# ---------------------------------------------------------------------------
# Page: Edit record
# ---------------------------------------------------------------------------
elif page == "Edit record":
    page_header("Maintenance", "Edit a record", "Change a student's name, age, or both.")
    left, right = st.columns([3, 2], gap="large")

    with left:
        with st.container(border=True):
            names = sorted(df_all["name"].dropna().astype(str).unique()) if not df_all.empty else []
            if names:
                old_name = st.selectbox("Student to edit", names)
                current = df_all[df_all["name"] == old_name].iloc[0]
                cur_age = int(current["age"]) if pd.notna(current["age"]) else 18
            else:
                old_name = st.text_input("Current name", placeholder="Existing student name")
                cur_age = 18

            with st.form("update_student_form", border=False):
                st.markdown(f'<div class="hint" style="margin:6px 0 4px">New details</div>', unsafe_allow_html=True)
                new_name = st.text_input("New name", value=old_name or "", key=f"nn_{old_name}")
                new_age = st.number_input("New age", min_value=1, max_value=100,
                                          value=min(max(cur_age, 1), 100), key=f"na_{old_name}")
                update = st.form_submit_button("Save changes", type="primary")

            if update:
                if not (old_name and new_name.strip()):
                    st.warning("Both the current name and the new name are required.")
                else:
                    try:
                        r = requests.put(f"{API_URL}/student/update/{_path(old_name)}",
                                         json={"name": new_name.strip(), "age": int(new_age)}, timeout=TIMEOUT)
                        if r.status_code == 200:
                            refresh_data()
                            flash("success", f"Updated {old_name} → {new_name.strip()} ({int(new_age)})")
                            st.rerun()
                        else:
                            st.error(f"Server returned {r.status_code}: {r.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Connection error: {e}")

    with right:
        with st.container(border=True):
            st.markdown('<div class="section-title">How it works</div>', unsafe_allow_html=True)
            st.markdown('<div class="hint">1. Pick the student you want to change.<br>'
                        '2. The form fills with their current details.<br>'
                        '3. Edit the name, the age, or both.<br>'
                        '4. Save — changes apply immediately.</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page: Insights
# ---------------------------------------------------------------------------
elif page == "Insights":
    page_header("Analytics", "Insights", "A quick read on who is enrolled.")

    df = df_all.dropna(subset=["age"]) if not df_all.empty else df_all
    if df.empty:
        with st.container(border=True):
            st.markdown('<div class="hint">Nothing to analyse yet. Once students are added you\'ll see '
                        'age distribution, age groups, the oldest students and summary statistics here.</div>',
                        unsafe_allow_html=True)
    else:
        mode = df["age"].mode()
        mode_val = int(mode.iloc[0]) if not mode.empty else "—"

        c1, c2, c3, c4 = st.columns(4)
        with c1: stat("Total students", len(df_all), "records in database")
        with c2: stat("Average age", f"{df['age'].mean():.1f}", f"median {df['age'].median():.0f}")
        with c3: stat("Youngest", int(df["age"].min()), "years")
        with c4: stat("Oldest", int(df["age"].max()), "years")

        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2 = st.columns([3, 2], gap="medium")

        with g1:
            with st.container(border=True):
                fig = px.histogram(df, x="age", nbins=20, title="Age distribution",
                                   color_discrete_sequence=[ACCENT], labels={"age": "Age (years)"})
                fig.update_traces(marker_line_color="#FFFFFF", marker_line_width=1)
                fig.update_yaxes(title="Students")
                st.plotly_chart(style_fig(fig), use_container_width=True)

        with g2:
            with st.container(border=True):
                groups = pd.cut(df["age"], bins=[0, 18, 25, 35, 50, 100],
                                labels=["≤18", "19–25", "26–35", "36–50", "51+"])
                counts = groups.value_counts().sort_index()
                counts = counts[counts > 0]
                fig2 = px.pie(values=counts.values, names=counts.index.astype(str), hole=0.55,
                              title="Age groups",
                              color_discrete_sequence=["#0F766E", "#14B8A6", "#5EEAD4", "#F59E0B", "#FCD34D"])
                fig2.update_traces(textinfo="percent", textfont_color="#FFFFFF", sort=False)
                st.plotly_chart(style_fig(fig2), use_container_width=True)

        g3, g4 = st.columns([3, 2], gap="medium")
        with g3:
            with st.container(border=True):
                top = df.nlargest(10, "age")[["name", "age"]].sort_values("age")
                fig3 = px.bar(top, x="age", y="name", orientation="h", title="Ten oldest students",
                              color_discrete_sequence=[ACCENT], labels={"age": "Age (years)", "name": ""},
                              text="age")
                fig3.update_traces(textposition="outside", cliponaxis=False)
                st.plotly_chart(style_fig(fig3, height=360), use_container_width=True)

        with g4:
            with st.container(border=True):
                st.markdown('<div class="section-title">Summary statistics</div>', unsafe_allow_html=True)
                rows = [
                    ("Mean", f"{df['age'].mean():.2f}"),
                    ("Median", f"{df['age'].median():.2f}"),
                    ("Mode", f"{mode_val}"),
                    ("Std deviation", f"{df['age'].std():.2f}" if len(df) > 1 else "—"),
                    ("Age range", f"{int(df['age'].min())} – {int(df['age'].max())} yrs"),
                    ("Records", f"{len(df_all)}"),
                ]
                st.markdown("".join(
                    f'<div class="row-item"><span style="color:{MUTED}">{k}</span><b>{v}</b></div>'
                    for k, v in rows), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    f'<div class="app-foot">EduTrack · Student Records · Spring Boot + Streamlit · {datetime.now():%Y}</div>',
    unsafe_allow_html=True,
)
