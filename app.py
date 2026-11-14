"""SECTION 3: The Streamlit app (widescreen dark design). Run with:  streamlit run app.py"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from rules import (RANGES, LABELS, UNITS, evaluate, status, overall,
                   needs_flight_surgeon)
from simulate import generate_mission

st.set_page_config(page_title="Orbit Check", page_icon="🪐", layout="wide")

COLORS = {"ok": "#2ecc71", "warn": "#f5b942", "alert": "#ff5c5c"}
WORDS = {"ok": "NORMAL", "warn": "CAUTION", "alert": "URGENT"}
ICON = {"ok": "🟢", "warn": "🟡", "alert": "🔴"}

# ---------------- LOOK AND FEEL (all the CSS lives here) ----------------
STYLE = """
<style>
#MainMenu, footer {visibility: hidden;}
.stApp {background: radial-gradient(ellipse at top, #0d1b3d 0%, #050b1a 55%, #02050d 100%); color: #e8eefc;}
.block-container {max-width: 1350px; padding-top: 1.2rem;}

.hero {
  position: relative; text-align: center; padding: 70px 24px 56px; margin-bottom: 22px;
  border-radius: 22px; border: 1px solid rgba(120,170,255,.28); overflow: hidden;
  background:
    radial-gradient(1.5px 1.5px at 12% 25%, #fff, transparent),
    radial-gradient(1px 1px at 28% 70%, #cfe3ff, transparent),
    radial-gradient(1.5px 1.5px at 45% 20%, #fff, transparent),
    radial-gradient(1px 1px at 63% 78%, #fff, transparent),
    radial-gradient(1.5px 1.5px at 78% 30%, #cfe3ff, transparent),
    radial-gradient(1px 1px at 90% 65%, #fff, transparent),
    radial-gradient(1px 1px at 5% 60%, #fff, transparent),
    radial-gradient(circle at 85% 15%, rgba(77,163,255,.42), transparent 38%),
    radial-gradient(circle at 10% 95%, rgba(140,90,255,.34), transparent 42%),
    linear-gradient(135deg, #06112b, #0a1e48);
}
.hero-title {font-size: 4.8rem; font-weight: 800; letter-spacing: .32em; padding-left: .32em;
  color: #fff; line-height: 1.1; text-shadow: 0 0 34px rgba(77,163,255,.65);}
.hero-sub {font-size: 1.25rem; color: #b9cdf5; margin-top: 14px; letter-spacing: .06em;}
.chip {display: inline-block; margin: 20px 6px 0; padding: 6px 16px; border-radius: 999px;
  font-size: .78rem; letter-spacing: .14em; color: #9fc2ff; border: 1px solid rgba(120,170,255,.4);
  background: rgba(77,163,255,.08);}

.stTabs [data-baseweb="tab-list"] {gap: 6px;}
.stTabs [data-baseweb="tab"] {font-size: 1.05rem; padding: 10px 24px;}

.sec {font-size: 1.05rem; font-weight: 700; letter-spacing: .18em; text-transform: uppercase;
  color: #8fb4ff; margin: 26px 0 10px;}
.status {margin-top: 1.7rem; padding: 14px 18px; border-radius: 14px; border: 1px solid;
  text-align: center; font-weight: 800; letter-spacing: .14em; font-size: 1.05rem;}
.card {background: rgba(255,255,255,.045); border: 1px solid rgba(255,255,255,.10);
  border-left: 6px solid #2ecc71; border-radius: 14px; padding: 18px 20px; margin-bottom: 14px;}
.card .lab {font-size: .8rem; letter-spacing: .16em; text-transform: uppercase; color: #9db3dd;}
.card .val {font-size: 2.3rem; font-weight: 700; color: #fff; line-height: 1.25;}
.card .val span {font-size: 1rem; font-weight: 400; color: #9db3dd;}
.card .st {font-size: .78rem; font-weight: 700; letter-spacing: .14em;}
.alertbar {background: rgba(255,92,92,.14); border: 1px solid #ff5c5c; color: #ffb3b3;
  border-radius: 12px; padding: 14px 20px; font-weight: 700; letter-spacing: .05em; margin: 14px 0 4px;}
.hz {background: rgba(255,255,255,.045); border: 1px solid rgba(255,255,255,.10);
  border-radius: 14px; padding: 16px 18px; height: 100%;}
.hz b {color: #8fb4ff; letter-spacing: .06em;}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

# ---------------- DATA (lives in session state so check-ins get added) ----------------
if "data" not in st.session_state:
    st.session_state.data = generate_mission()
df = st.session_state.data

# ---------------- BANNER ----------------
st.markdown("""
<div class="hero">
  <div class="hero-title">ORBIT CHECK</div>
  <div class="hero-sub">Explainable health monitoring for deep-space crews</div>
  <span class="chip">SIMULATED DATA</span><span class="chip">PROTOTYPE</span><span class="chip">NOT MEDICAL ADVICE</span>
</div>
""", unsafe_allow_html=True)

tab_dash, tab_in, tab_trends, tab_guide, tab_about = st.tabs(
    ["Dashboard", "Daily Check-In", "Trends", "Guide", "About"])

# ---------------- DASHBOARD ----------------
with tab_dash:
    top = st.columns([3, 1])
    day = top[0].slider("Mission day  (try day 48 or day 90)", 1, len(df), len(df))
    idx = day - 1
    row = df.iloc[idx]
    flags = evaluate(df, idx)
    lvl = overall(flags)
    c = COLORS[lvl]
    top[1].markdown(
        f'<div class="status" style="color:{c};border-color:{c};background:{c}22">'
        f'DAY {day} · {WORDS[lvl]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec">Vitals</div>', unsafe_allow_html=True)
    names = list(RANGES)
    for group in (names[:4], names[4:]):
        cols = st.columns(4)
        for col, ind in zip(cols, group):
            s = status(ind, row[ind])
            col.markdown(
                f'<div class="card" style="border-left-color:{COLORS[s]}">'
                f'<div class="lab">{LABELS[ind]}</div>'
                f'<div class="val">{row[ind]:.1f}<span> {UNITS[ind]}</span></div>'
                f'<div class="st" style="color:{COLORS[s]}">● {WORDS[s]}</div></div>',
                unsafe_allow_html=True)

    if needs_flight_surgeon(flags):
        st.markdown('<div class="alertbar">⚠ CONTACT YOUR FLIGHT SURGEON. '
                    'Help from Earth is delayed, so do not wait.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec">Why flagged</div>', unsafe_allow_html=True)
    if not flags:
        st.success("No flags today. Keep logging.")
    else:
        cols = st.columns(2)
        for i, f in enumerate(flags):
            with cols[i % 2]:
                with st.expander(f"{ICON[f['level']]} {f['title']}", expanded=f["level"] == "alert"):
                    st.write(f["why"])
                    st.write(f"**Linked NASA hazard:** {f['hazard']}")
                    st.write(f"**NASA risk:** {f['risk']}")
                    st.write(f"**What to do:** {f['action']}")

# ---------------- CHECK-IN ----------------
with tab_in:
    st.markdown('<div class="sec">Log today\'s readings</div>', unsafe_allow_html=True)
    with st.form("checkin"):
        c1, c2, c3, c4 = st.columns(4)
        hr = c1.number_input("Heart rate (bpm)", 30, 220, 64)
        sys_ = c2.number_input("Systolic BP (mmHg)", 60, 250, 118)
        dia = c3.number_input("Diastolic BP (mmHg)", 30, 150, 76)
        glu = c4.number_input("Blood sugar (mg/dL)", 30, 400, 92)
        temp = c1.number_input("Body temp (C)", 33.0, 42.0, 36.7, step=0.1)
        sleep = c2.number_input("Sleep last night (hrs)", 0.0, 14.0, 7.0, step=0.5)
        rad = c3.number_input("Radiation dose today (mSv)", 0.0, 10.0, 0.6, step=0.1)
        mood = c4.slider("Mood (1 low - 5 great)", 1, 5, 4)
        if st.form_submit_button("Save check-in"):
            new = dict(day=len(df) + 1, heart_rate=hr, systolic=sys_, diastolic=dia, glucose=glu,
                       temp_c=temp, sleep_hrs=sleep, mood=mood, radiation_msv=rad)
            st.session_state.data = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            st.success(f"Saved as day {new['day']}. Move the slider on the Dashboard to see it.")

# ---------------- TRENDS ----------------
with tab_trends:
    left, right = st.columns([1, 3])
    ind = left.selectbox("Indicator", list(RANGES), format_func=lambda k: LABELS[k])
    left.caption("Solid line: your readings. Dotted: your own 14-day baseline. "
                 "Orange and red dashed lines: caution and urgent limits.")
    fig = go.Figure()
    fig.add_scatter(x=df["day"], y=df[ind], mode="lines", name=LABELS[ind], line=dict(color="#4da3ff", width=3))
    fig.add_scatter(x=df["day"], y=df[ind].rolling(14, min_periods=7).mean(),
                    mode="lines", name="Your 14-day baseline", line=dict(dash="dot", color="#cfe3ff"))
    wl, wh, al, ah = RANGES[ind]
    for v, color in [(wl, "orange"), (wh, "orange"), (al, "red"), (ah, "red")]:
        if v is not None:
            fig.add_hline(y=v, line_dash="dash", line_color=color)
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Mission day", yaxis_title=UNITS[ind], height=420,
                      margin=dict(l=10, r=10, t=10, b=10))
    right.plotly_chart(fig)

    st.markdown('<div class="sec">Cumulative radiation dose (mSv)</div>', unsafe_allow_html=True)
    st.area_chart(df.set_index("day")["radiation_msv"].cumsum(), height=240)

# ---------------- GUIDE ----------------
with tab_guide:
    st.markdown('<div class="sec">The five hazards of spaceflight</div>', unsafe_allow_html=True)
    hazards = [
        ("Space radiation", "Invisible, and one of the most hazardous parts of spaceflight."),
        ("Isolation and confinement", "Long stretches in a small space, far from home, affect behavior and mood."),
        ("Distance from Earth", "Medical care and supplies get harder to receive the farther you go."),
        ("Gravity fields", "Muscles, bones, inner ear and organs must adjust to new gravity."),
        ("Hostile/closed environments", "The spacecraft itself: temperature, pressure, noise, microbes."),
    ]
    for col, (name, text) in zip(st.columns(5), hazards):
        col.markdown(f'<div class="hz"><b>{name}</b><br>{text}</div>', unsafe_allow_html=True)

    a, b = st.columns(2)
    a.markdown('<div class="sec">How the app thinks</div>', unsafe_allow_html=True)
    a.write("Each reading is checked against a safe range AND against your own recent normal. "
            "Flags are explained and linked to a NASA hazard. Because you are far from Earth, "
            "urgent flags tell you when to contact your flight surgeon.")
    b.markdown('<div class="sec">Measuring tips</div>', unsafe_allow_html=True)
    b.write("- **Heart rate and BP:** sit quietly for 5 minutes first.\n"
            "- **Blood sugar:** note when you last ate.\n"
            "- **Temperature:** wait 15 minutes after exercise.\n"
            "- **Sleep and mood:** log them honestly. Small changes matter over time.")

# ---------------- ABOUT ----------------
with tab_about:
    st.markdown('<div class="sec">About this prototype</div>', unsafe_allow_html=True)
    st.write("**Simulated data.** No real astronaut data is used. Safe ranges are general placeholders.")
    st.write("**Sources:** NASA Human Research Program (5 Hazards, Risks of Human Spaceflight); "
             "CSA article on monitoring radiation for astronaut health.")
    st.write("**Not medical advice.** This is a hackathon prototype.")
