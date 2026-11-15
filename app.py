"""SECTION 3: The Streamlit app. Run with:  streamlit run app.py"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
 
from rules import (RANGES, LABELS, UNITS, evaluate, status, overall,
                   needs_flight_surgeon)
from simulate import generate_mission
 
st.set_page_config(page_title="Orbit Check", page_icon="🪐", layout="wide")
 
INK, PAPER, ACCENT, LEMON = "#0b1f3a", "#e3f0f7", "#3f8fd2", "#f6e75a"
COLORS = {"ok": "#1b7a4b", "warn": "#a96b00", "alert": "#c1272d"}
WORDS = {"ok": "NORMAL", "warn": "CAUTION", "alert": "URGENT"}
OVERALL = {"ok": "ALL CLEAR", "warn": "CAUTION", "alert": "URGENT"}
 
# ---------------- LOOK AND FEEL: flight-log / paper-and-ink ----------------
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
#MainMenu, footer {visibility: hidden;}
.stApp {background: #e3f0f7;}
.block-container {max-width: 1500px; padding-top: 1rem;}
.stApp, .stApp p, .stApp label, .stApp input, .stApp button, .stApp li,
div[data-testid="stMarkdownContainer"], .stTabs [data-baseweb="tab"] {
  font-family: 'Bricolage Grotesque', sans-serif; color: #0b1f3a;}
.mono {font-family: 'IBM Plex Mono', monospace;}
 
/* ---- banner ---- */
.banner {background: #0b1f3a; border-bottom: 6px solid #f6e75a;
  padding: 10px 28px 16px; margin-bottom: 18px;}
.banner-top {display: flex; justify-content: space-between; font-family: 'IBM Plex Mono', monospace;
  font-size: .72rem; letter-spacing: .08em; color: #bcd6e8; border-bottom: 1px solid rgba(188,214,232,.45); padding-bottom: 8px;}
.banner-top span:first-child {color: #f6e75a; font-weight: 600;}
.banner-title {font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  font-size: clamp(2.4rem, 5vw, 4.2rem); line-height: 1; letter-spacing: -.03em;
  margin: 12px 0 4px -.03em; color: #f4fafd;}
.banner-sub {font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.05rem; font-weight: 600;
  line-height: 1.2; color: #bcd6e8;}
 
/* ---- tabs ---- */
.stTabs [data-baseweb="tab-list"] {gap: 28px; border-bottom: 2px solid #0b1f3a;}
.stTabs [data-baseweb="tab"] {font-size: 1.15rem; font-weight: 600; padding: 8px 0;}
.stTabs [data-baseweb="tab-highlight"] {background: #0b1f3a; height: 5px;}
 
/* ---- status strip ---- */
.strip {display: flex; justify-content: space-between; align-items: baseline;
  border-top: 6px solid #0b1f3a; border-bottom: 2px solid #0b1f3a; padding: 10px 2px; margin: 10px 0 6px;
  font-family: 'IBM Plex Mono', monospace;}
.strip .d {font-size: 1.3rem; font-weight: 600; background: #f6e75a; padding: 2px 12px;}
.strip .s {font-size: 3rem; font-weight: 600; letter-spacing: -.02em; line-height: 1;}
.strip .f {font-size: 1.3rem; font-weight: 600;}
 
/* ---- ledger rows ---- */
.row {display: grid; grid-template-columns: 1fr auto 135px; align-items: baseline; gap: 14px;
  border-bottom: 1px solid rgba(11,31,58,.3); padding: 12px 2px;}
.row .rl {font-size: 1.1rem; font-weight: 600;}
.row .rv {font-family: 'IBM Plex Mono', monospace; font-size: 2.1rem; font-weight: 600; text-align: right;}
.row .rv small {font-size: .9rem; font-weight: 400; opacity: .65;}
.row .rs {font-family: 'IBM Plex Mono', monospace; font-size: .8rem; font-weight: 600; letter-spacing: .06em;
  display: flex; align-items: center; gap: 9px;}
.dot {width: 11px; height: 11px; border-radius: 50%; display: inline-block; animation: blink 1.4s ease-in-out infinite;}
.dot.alert {animation-duration: .6s;}
.dot.warn {animation-duration: 1s;}
@keyframes blink {0%, 100% {opacity: 1; transform: scale(1);} 50% {opacity: .15; transform: scale(.7);}}
@media (prefers-reduced-motion: reduce) {.dot {animation: none;}}
 
.sec {font-family: 'IBM Plex Mono', monospace; font-size: .85rem; font-weight: 600;
  letter-spacing: .12em; margin: 26px 0 6px; padding-bottom: 6px; border-bottom: 2px solid #0b1f3a;}
.alertbar {background: #c1272d; color: #e3f0f7 !important; padding: 16px 20px; margin: 18px 0 4px;
  font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 1.05rem;}
.flag {border-left: 6px solid #b7791f; padding: 6px 0 6px 16px; margin: 16px 0;}
.flag .ft {font-size: 1.25rem; font-weight: 800;}
.flag .fm {font-family: 'IBM Plex Mono', monospace; font-size: .78rem; margin: 6px 0; opacity: .75;}
.flag .fa {font-weight: 600;}
.logtitle {font-weight: 800; font-size: 2.4rem; letter-spacing: -.03em; line-height: 1;}
.logsub {font-family: 'IBM Plex Mono', monospace; font-size: .8rem; margin: 6px 0 12px; opacity: .75;}
.hz {border-top: 4px solid #0b1f3a; padding-top: 8px; height: 100%;}
.hz .n {font-family: 'IBM Plex Mono', monospace; font-size: 1.4rem; font-weight: 600; background: #f6e75a; display: inline-block; padding: 0 10px; margin-bottom: 6px;}
.hz b {font-size: 1.1rem;}
 
/* ---- inputs + buttons: square, no rounded cards ---- */
div[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 0 !important; border: 2px solid #0b1f3a !important;
  background: #f4fafd;}
.stNumberInput input {background: #e3f0f7 !important; color: #0b1f3a !important; border-radius: 0 !important;
  font-family: 'IBM Plex Mono', monospace !important;}
.stButton button {border-radius: 0 !important; border: 2px solid #0b1f3a !important;
  background: #e3f0f7 !important; font-weight: 600;}
.stButton button p {color: #0b1f3a !important;}
.stButton button[kind="primary"], .stButton button[data-testid="stBaseButton-primary"] {background: #0b1f3a !important;}
.stButton button[kind="primary"] p, .stButton button[data-testid="stBaseButton-primary"] p {color: #f6e75a !important;}
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
<div class="banner">
  <div class="banner-top"><span>CREW HEALTH LOG</span><span>SIMULATED DATA / PROTOTYPE / NOT MEDICAL ADVICE</span></div>
  <div class="banner-title">ORBIT CHECK</div>
  <div class="banner-sub">Know what your body is telling you, and why, when help is far away.</div>
</div>
""", unsafe_allow_html=True)
 
tab_dash, tab_trends, tab_guide, tab_about = st.tabs(["Dashboard", "Trends", "Guide", "About"])
 
# ---------------- DASHBOARD ----------------
with tab_dash:
    left, right = st.columns([1, 2.2], gap="large")
 
    # ----- left: the blank day to fill in -----
    with left:
        with st.container(border=True):
            st.markdown(f'<div class="logtitle">Log day {len(df) + 1}</div>'
                        f'<div class="logsub">NOT LOGGED YET</div>', unsafe_allow_html=True)
            a, b = st.columns(2)
            a.number_input("Heart rate (bpm)", 30, 220, key="in_hr")
            b.number_input("Sleep (hrs)", 0.0, 14.0, step=0.5, key="in_sleep")
            a.number_input("Systolic BP", 60, 250, key="in_sys")
            b.number_input("Diastolic BP", 30, 150, key="in_dia")
            a.number_input("Blood sugar (mg/dL)", 30, 400, key="in_glu")
            b.number_input("Body temp (C)", 33.0, 42.0, step=0.1, key="in_temp")
            a.number_input("Radiation (mSv)", 0.0, 10.0, step=0.1, key="in_rad")
            b.slider("Mood (1-5)", 1, 5, key="in_mood")
            st.button(f"Save day {len(df) + 1}", type="primary", on_click=save_checkin,
                      use_container_width=True)
            p1, p2 = st.columns(2)
            p1.button("Typical day", on_click=load_values, args=(TYPICAL,), use_container_width=True)
            p2.button("Rough day (demo)", on_click=load_values, args=(ROUGH,), use_container_width=True)
 
    # ----- right: readout for the selected day -----
    with right:
        day = st.slider("Viewing mission day", 1, len(df), key="view_day")
        idx = day - 1
        row = df.iloc[idx]
        flags = evaluate(df, idx)
        lvl = overall(flags)
 
        st.markdown(
            f'<div class="strip"><span class="d">DAY {day}</span>'
            f'<span class="s" style="color:{COLORS[lvl]}">{OVERALL[lvl]}</span>'
            f'<span class="f">{len(flags)} FLAG{"" if len(flags) == 1 else "S"}</span></div>',
            unsafe_allow_html=True)
 
        names = list(RANGES)
        c1, c2 = st.columns(2, gap="large")
        for col, group in ((c1, names[:4]), (c2, names[4:])):
            html = ""
            for ind in group:
                s = status(ind, row[ind])
                html += (f'<div class="row"><span class="rl">{LABELS[ind]}</span>'
                         f'<span class="rv">{row[ind]:.1f}<small> {UNITS[ind]}</small></span>'
                         f'<span class="rs" style="color:{COLORS[s]}"><span class="dot {s}" '
                         f'style="background:{COLORS[s]};box-shadow:0 0 8px {COLORS[s]}"></span>{WORDS[s]}</span></div>')
            col.markdown(html, unsafe_allow_html=True)
 
        if needs_flight_surgeon(flags):
            st.markdown('<div class="alertbar">CONTACT YOUR FLIGHT SURGEON. '
                        'Help from Earth is delayed, so do not wait.</div>', unsafe_allow_html=True)
 
        st.markdown('<div class="sec">WHY FLAGGED</div>', unsafe_allow_html=True)
        if not flags:
            st.markdown("**Nothing flagged.** Every reading is inside its safe range and close to your own normal.")
        for f in flags:
            st.markdown(
                f'<div class="flag" style="border-left-color:{COLORS[f["level"]]}">'
                f'<div class="ft">{f["title"]}</div><div>{f["why"]}</div>'
                f'<div class="fm">HAZARD: {f["hazard"]} / RISK: {f["risk"]}</div>'
                f'<div class="fa">&rarr; {f["action"]}</div></div>', unsafe_allow_html=True)
 
# ---------------- TRENDS ----------------
with tab_trends:
    l, r = st.columns([1, 3], gap="large")
    ind = l.selectbox("Indicator", list(RANGES), format_func=lambda k: LABELS[k])
    l.caption("Black line: your readings. Dotted blue: your own 14-day baseline. "
              "Amber and red dashed lines: caution and urgent limits.")
    fig = go.Figure()
    fig.add_scatter(x=df["day"], y=df[ind], mode="lines+markers", name=LABELS[ind],
                    line=dict(color=INK, width=3))
    fig.add_scatter(x=df["day"], y=df[ind].rolling(14, min_periods=7).mean(),
                    mode="lines", name="Your 14-day baseline", line=dict(dash="dot", color=ACCENT, width=3))
    wl, wh, al, ah = RANGES[ind]
    for v, color in [(wl, "#a96b00"), (wh, "#a96b00"), (al, "#c1272d"), (ah, "#c1272d")]:
        if v is not None:
            fig.add_hline(y=v, line_dash="dash", line_color=color)
    fig.update_layout(template="simple_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=INK), xaxis_title="Mission day", yaxis_title=UNITS[ind], height=430,
                      margin=dict(l=10, r=10, t=10, b=10))
    r.plotly_chart(fig)
 
    st.markdown('<div class="sec">CUMULATIVE RADIATION DOSE (mSv)</div>', unsafe_allow_html=True)
    cum = go.Figure(go.Scatter(x=df["day"], y=df["radiation_msv"].cumsum(), fill="tozeroy",
                               line=dict(color=INK, width=2), fillcolor="rgba(246,231,90,.75)"))
    cum.update_layout(template="simple_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=INK), xaxis_title="Mission day", height=260,
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(cum)
 
# ---------------- GUIDE ----------------
with tab_guide:
    st.markdown('<div class="sec">THE FIVE HAZARDS OF SPACEFLIGHT</div>', unsafe_allow_html=True)
    hazards = [
        ("Space radiation", "Invisible, and one of the most hazardous parts of spaceflight."),
        ("Isolation and confinement", "Long stretches in a small space, far from home, affect behavior and mood."),
        ("Distance from Earth", "Medical care and supplies get harder to receive the farther you go."),
        ("Gravity fields", "Muscles, bones, inner ear and organs must adjust to new gravity."),
        ("Hostile/closed environments", "The spacecraft itself: temperature, pressure, noise, microbes."),
    ]
    for i, (col, (name, text)) in enumerate(zip(st.columns(5, gap="large"), hazards), 1):
        col.markdown(f'<div class="hz"><div class="n">0{i}</div><b>{name}</b><br>{text}</div>',
                     unsafe_allow_html=True)
    a, b = st.columns([1.3, 1], gap="large")
    a.markdown('<div class="sec">HOW THE APP THINKS</div>', unsafe_allow_html=True)
    a.write("Each reading is checked against a safe range AND against your own recent normal. "
            "Flags are explained and linked to a NASA hazard. Because you are far from Earth, "
            "urgent flags tell you when to contact your flight surgeon.")
    b.markdown('<div class="sec">MEASURING TIPS</div>', unsafe_allow_html=True)
    b.write("- **Heart rate and BP:** sit quietly for 5 minutes first.\n"
            "- **Blood sugar:** note when you last ate.\n"
            "- **Temperature:** wait 15 minutes after exercise.\n"
            "- **Sleep and mood:** log them honestly. Small changes matter over time.")
 
# ---------------- ABOUT ----------------
with tab_about:
    st.markdown('<div class="sec">ABOUT THIS PROTOTYPE</div>', unsafe_allow_html=True)
    st.write("**Simulated data.** No real astronaut data is used. Safe ranges are general placeholders.")
    st.write("**Sources:** NASA Human Research Program (5 Hazards, Risks of Human Spaceflight); "
             "CSA article on monitoring radiation for astronaut health.")
    st.write("**Not medical advice.** This is a hackathon prototype.")

