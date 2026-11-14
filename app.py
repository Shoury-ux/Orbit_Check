"""SECTION 3: The Streamlit app. Run with:  streamlit run app.py"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
 
from rules import (RANGES, LABELS, UNITS, evaluate, status, overall,
                   needs_flight_surgeon)
from simulate import generate_mission
 
st.set_page_config(page_title="Orbit Check", page_icon="🪐", layout="wide")
 
COLORS = {"ok": "#34d399", "warn": "#fbbf24", "alert": "#ff5d5d"}
WORDS = {"ok": "NORMAL", "warn": "CAUTION", "alert": "URGENT"}
OVERALL = {"ok": "ALL CLEAR", "warn": "CAUTION", "alert": "URGENT"}
ICON = {"ok": "🟢", "warn": "🟡", "alert": "🔴"}
 
# ---------------- LOOK AND FEEL ----------------
STYLE = """
<style>
#MainMenu, footer {visibility: hidden;}
.stApp {background: #03060f;}
.block-container {max-width: 1500px; padding-top: 1rem;}
 
.hero {
  position: relative; text-align: center; padding: 90px 24px 120px; margin-bottom: 26px;
  border-radius: 28px; border: 1px solid rgba(120,170,255,.25); overflow: hidden; min-height: 380px;
  background:
    radial-gradient(1.5px 1.5px at 8% 20%, #fff, transparent),
    radial-gradient(1px 1px at 18% 55%, #cfe3ff, transparent),
    radial-gradient(1.5px 1.5px at 30% 15%, #fff, transparent),
    radial-gradient(1px 1px at 42% 40%, #fff, transparent),
    radial-gradient(1.5px 1.5px at 58% 18%, #cfe3ff, transparent),
    radial-gradient(1px 1px at 70% 50%, #fff, transparent),
    radial-gradient(1.5px 1.5px at 82% 22%, #fff, transparent),
    radial-gradient(1px 1px at 93% 45%, #cfe3ff, transparent),
    radial-gradient(ellipse 130% 55% at 50% 140%, #5db4ff 0%, #1f6bde 22%, rgba(8,24,70,0) 52%),
    radial-gradient(circle at 15% 10%, rgba(140,90,255,.30), transparent 40%),
    linear-gradient(180deg, #02040c, #06122e);
}
.hero-kicker {font-size: 1rem; letter-spacing: .5em; color: #8fb4ff; font-weight: 700; margin-bottom: 10px;}
.hero-title {
  font-size: clamp(3.6rem, 10vw, 8.5rem); font-weight: 900; letter-spacing: .1em; line-height: 1;
  background: linear-gradient(90deg, #ffffff 0%, #9fd0ff 50%, #ffffff 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
  filter: drop-shadow(0 0 28px rgba(93,180,255,.55));
}
.hero-sub {font-size: 1.5rem; color: #cfe0ff; margin-top: 18px; letter-spacing: .04em;}
.chip {display: inline-block; margin: 24px 6px 0; padding: 7px 18px; border-radius: 999px;
  font-size: .8rem; letter-spacing: .16em; color: #cfe3ff; border: 1px solid rgba(160,200,255,.45);
  background: rgba(10,30,80,.55);}
 
.stTabs [data-baseweb="tab-list"] {gap: 8px;}
.stTabs [data-baseweb="tab"] {font-size: 1.1rem; padding: 12px 28px;}
 
.sec {font-size: 1rem; font-weight: 800; letter-spacing: .2em; text-transform: uppercase;
  color: #7fa8ff; margin: 22px 0 10px;}
.tile {background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.11);
  border-radius: 16px; padding: 16px 22px;}
.tile .k {font-size: .75rem; letter-spacing: .2em; color: #9db3dd; text-transform: uppercase;}
.tile .v {font-size: 2.2rem; font-weight: 800; line-height: 1.2;}
.card {background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.11);
  border-top: 5px solid #34d399; border-radius: 16px; padding: 16px 20px; margin-bottom: 14px;}
.card .lab {font-size: .78rem; letter-spacing: .16em; text-transform: uppercase; color: #9db3dd;}
.card .val {font-size: 2.4rem; font-weight: 800; color: #fff; line-height: 1.2;}
.card .val span {font-size: 1rem; font-weight: 400; color: #9db3dd;}
.card .st {font-size: .75rem; font-weight: 800; letter-spacing: .14em;}
.alertbar {background: rgba(255,93,93,.15); border: 1px solid #ff5d5d; color: #ffb8b8;
  border-radius: 14px; padding: 16px 22px; font-weight: 800; letter-spacing: .06em; margin: 8px 0 4px;}
.logtitle {font-size: 1.6rem; font-weight: 800; color: #fff;}
.logsub {color: #9db3dd; font-size: .9rem; margin-bottom: 6px;}
.hz {background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.11);
  border-radius: 14px; padding: 16px 18px; height: 100%;}
.hz b {color: #8fb4ff;}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)
 
# ---------------- DATA + INPUT DEFAULTS ----------------
if "data" not in st.session_state:
    st.session_state.data = generate_mission()
df = st.session_state.data
 
TYPICAL = dict(in_hr=64, in_sys=118, in_dia=76, in_glu=92, in_temp=36.7,
               in_sleep=7.0, in_rad=0.6, in_mood=4)
ROUGH = dict(in_hr=112, in_sys=146, in_dia=92, in_glu=118, in_temp=37.2,
             in_sleep=4.2, in_rad=0.7, in_mood=2)
for k, v in TYPICAL.items():
    st.session_state.setdefault(k, v)
st.session_state.setdefault("view_day", len(df))
 
 
def load_values(vals):
    st.session_state.update(vals)
 
 
def save_checkin():
    s = st.session_state
    new = dict(day=len(s.data) + 1, heart_rate=s.in_hr, systolic=s.in_sys, diastolic=s.in_dia,
               glucose=s.in_glu, temp_c=s.in_temp, sleep_hrs=s.in_sleep, mood=s.in_mood,
               radiation_msv=s.in_rad)
    s.data = pd.concat([s.data, pd.DataFrame([new])], ignore_index=True)
    s.view_day = new["day"]
    s.update(TYPICAL)
 
 
# ---------------- BANNER ----------------
st.markdown("""
<div class="hero">
  <div class="hero-kicker">DEEP-SPACE CREW HEALTH</div>
  <div class="hero-title">ORBIT CHECK</div>
  <div class="hero-sub">Know what your body is telling you, and why, when help is far away.</div>
  <span class="chip">SIMULATED DATA</span><span class="chip">PROTOTYPE</span><span class="chip">NOT MEDICAL ADVICE</span>
</div>
""", unsafe_allow_html=True)
 
tab_dash, tab_trends, tab_guide, tab_about = st.tabs(["Dashboard", "Trends", "Guide", "About"])
 
# ---------------- DASHBOARD ----------------
with tab_dash:
    left, right = st.columns([2.3, 1], gap="large")
 
    with left:
        day = st.slider("Viewing mission day", 1, len(df), key="view_day")
        idx = day - 1
        row = df.iloc[idx]
        flags = evaluate(df, idx)
        lvl = overall(flags)
        c = COLORS[lvl]
 
        t1, t2, t3 = st.columns(3)
        t1.markdown(f'<div class="tile"><div class="k">Mission day</div><div class="v">{day}</div></div>',
                    unsafe_allow_html=True)
        t2.markdown(f'<div class="tile"><div class="k">Status</div>'
                    f'<div class="v" style="color:{c}">{OVERALL[lvl]}</div></div>', unsafe_allow_html=True)
        t3.markdown(f'<div class="tile"><div class="k">Active flags</div><div class="v">{len(flags)}</div></div>',
                    unsafe_allow_html=True)
 
        st.markdown('<div class="sec">Vitals</div>', unsafe_allow_html=True)
        names = list(RANGES)
        for group in (names[:4], names[4:]):
            cols = st.columns(4)
            for col, ind in zip(cols, group):
                s = status(ind, row[ind])
                col.markdown(
                    f'<div class="card" style="border-top-color:{COLORS[s]}">'
                    f'<div class="lab">{LABELS[ind]}</div>'
                    f'<div class="val">{row[ind]:.1f}<span> {UNITS[ind]}</span></div>'
                    f'<div class="st" style="color:{COLORS[s]}">● {WORDS[s]}</div></div>',
                    unsafe_allow_html=True)
 
        if needs_flight_surgeon(flags):
            st.markdown('<div class="alertbar">⚠ CONTACT YOUR FLIGHT SURGEON. '
                        'Help from Earth is delayed, so do not wait.</div>', unsafe_allow_html=True)
 
        st.markdown('<div class="sec">Why flagged</div>', unsafe_allow_html=True)
        if not flags:
            st.success("Everything looks normal today. Keep logging.")
        else:
            cols = st.columns(2)
            for i, f in enumerate(flags):
                with cols[i % 2]:
                    with st.expander(f"{ICON[f['level']]} {f['title']}", expanded=f["level"] == "alert"):
                        st.write(f["why"])
                        st.write(f"**Linked NASA hazard:** {f['hazard']}")
                        st.write(f"**NASA risk:** {f['risk']}")
                        st.write(f"**What to do:** {f['action']}")
 
    with right:
        with st.container(border=True):
            st.markdown(f'<div class="logtitle">Log Day {len(df) + 1}</div>'
                        f'<div class="logsub">Not logged yet. Enter today\'s readings.</div>',
                        unsafe_allow_html=True)
            a, b = st.columns(2)
            a.number_input("Heart rate (bpm)", 30, 220, key="in_hr")
            b.number_input("Sleep (hrs)", 0.0, 14.0, step=0.5, key="in_sleep")
            a.number_input("Systolic BP", 60, 250, key="in_sys")
            b.number_input("Diastolic BP", 30, 150, key="in_dia")
            a.number_input("Blood sugar (mg/dL)", 30, 400, key="in_glu")
            b.number_input("Body temp (C)", 33.0, 42.0, step=0.1, key="in_temp")
            a.number_input("Radiation (mSv)", 0.0, 10.0, step=0.1, key="in_rad")
            b.slider("Mood (1-5)", 1, 5, key="in_mood")
            st.button(f"Save Day {len(df) + 1}", type="primary", on_click=save_checkin,
                      use_container_width=True)
            p1, p2 = st.columns(2)
            p1.button("Typical day", on_click=load_values, args=(TYPICAL,), use_container_width=True)
            p2.button("Rough day (demo)", on_click=load_values, args=(ROUGH,), use_container_width=True)
 
# ---------------- TRENDS ----------------
with tab_trends:
    l, r = st.columns([1, 3])
    ind = l.selectbox("Indicator", list(RANGES), format_func=lambda k: LABELS[k])
    l.caption("Solid line: your readings. Dotted: your own 14-day baseline. "
              "Orange and red dashed lines: caution and urgent limits.")
    fig = go.Figure()
    fig.add_scatter(x=df["day"], y=df[ind], mode="lines+markers", name=LABELS[ind],
                    line=dict(color="#5db4ff", width=3))
    fig.add_scatter(x=df["day"], y=df[ind].rolling(14, min_periods=7).mean(),
                    mode="lines", name="Your 14-day baseline", line=dict(dash="dot", color="#cfe3ff"))
    wl, wh, al, ah = RANGES[ind]
    for v, color in [(wl, "orange"), (wh, "orange"), (al, "red"), (ah, "red")]:
        if v is not None:
            fig.add_hline(y=v, line_dash="dash", line_color=color)
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Mission day", yaxis_title=UNITS[ind], height=430,
                      margin=dict(l=10, r=10, t=10, b=10))
    r.plotly_chart(fig)
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
 
Claude finished the response
