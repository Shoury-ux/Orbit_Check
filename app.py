"""SECTION 3: The Streamlit app. Run with:  streamlit run app.py"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from rules import (BASELINE_DAYS, CAREER_LIMIT_MSV, HAZARD, INDICATORS, LABELS, LIMITS,
                   MIN_BASELINE, UNITS, evaluate, fmt, needs_flight_surgeon, overall, status)
from simulate import generate_mission

st.set_page_config(page_title="Orbit Check", page_icon="🪐", layout="wide")

INK, PAPER, ACCENT, LEMON = "#0b1f3a", "#e3f0f7", "#3f8fd2", "#f6e75a"
COLORS = {"ok": "#1b7a4b", "warn": "#a96b00", "alert": "#c1272d"}
BANDS = {"ok": "rgba(27,122,75,.20)", "warn": "rgba(169,107,0,.28)", "alert": "rgba(193,39,45,.26)"}
WORDS = {"ok": "NORMAL", "warn": "CAUTION", "alert": "URGENT"}
OVERALL = {"ok": "ALL CLEAR", "warn": "CAUTION", "alert": "URGENT"}

# ---------------- LOOK AND FEEL: flight-log / paper-and-ink ----------------
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
#MainMenu, footer {visibility: hidden;}
.stApp {background: #e3f0f7;}
.block-container {max-width: 1500px; padding-top: 1rem;}
.stApp, .stApp p, .stApp label, .stApp input, .stApp button, .stApp li, .stApp td, .stApp th,
div[data-testid="stMarkdownContainer"], .stTabs [data-baseweb="tab"] {
  font-family: 'Bricolage Grotesque', sans-serif; color: #0b1f3a;}
.mono {font-family: 'IBM Plex Mono', monospace;}

/* ---- banner ---- */
.banner {background: #0b1f3a; border-bottom: 6px solid #f6e75a;
  padding: 10px 28px 16px; margin-bottom: 18px;}
.banner-top {display: flex; justify-content: space-between; flex-wrap: wrap; gap: 6px;
  font-family: 'IBM Plex Mono', monospace; font-size: .72rem; letter-spacing: .08em; color: #bcd6e8;
  border-bottom: 1px solid rgba(188,214,232,.45); padding-bottom: 8px;}
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
.strip {display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px;
  border-top: 6px solid #0b1f3a; border-bottom: 2px solid #0b1f3a; padding: 10px 2px; margin: 10px 0 6px;
  font-family: 'IBM Plex Mono', monospace;}
.strip .d {font-size: 1.3rem; font-weight: 600; background: #f6e75a; padding: 2px 12px;}
.strip .s {font-size: clamp(2rem, 4vw, 3rem); font-weight: 600; letter-spacing: -.02em; line-height: 1;}
.strip .f {font-size: 1.3rem; font-weight: 600;}

/* ---- mission timeline ---- */
.tl {display: grid; gap: 2px; margin: 4px 0 2px;}
.tl span {height: 18px; min-width: 0; opacity: .85;}
.tl span.on {outline: 3px solid #0b1f3a; outline-offset: 1px; opacity: 1;}
.tlcap {font-family: 'IBM Plex Mono', monospace; font-size: .72rem; opacity: .7; display: flex;
  justify-content: space-between;}

/* ---- ledger rows ---- */
.row {display: grid; grid-template-columns: 1fr auto 135px; align-items: baseline; gap: 14px;
  border-bottom: 1px solid rgba(11,31,58,.3); padding: 12px 2px;}
.row .rl {font-size: 1.1rem; font-weight: 600;}
.row .rl small {display: block; font-family: 'IBM Plex Mono', monospace; font-size: .72rem;
  font-weight: 400; opacity: .6;}
.row .rv {font-family: 'IBM Plex Mono', monospace; font-size: 2.1rem; font-weight: 600; text-align: right;}
.row .rv small {font-size: .9rem; font-weight: 400; opacity: .65;}
.row .rs {font-family: 'IBM Plex Mono', monospace; font-size: .8rem; font-weight: 600; letter-spacing: .06em;
  display: flex; align-items: center; gap: 9px;}
.dot {width: 11px; height: 11px; border-radius: 50%; display: inline-block; animation: blink 1.4s ease-in-out infinite;}
.dot.ok {animation: none;}
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

/* ---- stat tiles ---- */
.stat {border-top: 4px solid #0b1f3a; padding-top: 6px;}
.stat .k {font-family: 'IBM Plex Mono', monospace; font-size: .72rem; letter-spacing: .1em; opacity: .7;}
.stat .v {font-family: 'IBM Plex Mono', monospace; font-size: 1.9rem; font-weight: 600; line-height: 1.1;}
.stat .v small {font-size: .85rem; font-weight: 400; opacity: .65;}
.bar {height: 8px; background: rgba(11,31,58,.12); margin-top: 6px;}
.bar span {display: block; height: 100%; background: #0b1f3a;}

/* ---- ranges table ---- */
table.rng {width: 100%; border-collapse: collapse; font-size: .95rem;}
table.rng th {text-align: left; font-family: 'IBM Plex Mono', monospace; font-size: .75rem;
  letter-spacing: .08em; border-bottom: 2px solid #0b1f3a; padding: 6px 8px;}
table.rng td {border-bottom: 1px solid rgba(11,31,58,.25); padding: 8px; vertical-align: top;}
table.rng td.m {font-family: 'IBM Plex Mono', monospace; font-weight: 600; white-space: nowrap;}

/* ---- inputs + buttons: square, no rounded cards ---- */
div[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 0 !important; border: 2px solid #0b1f3a !important;
  background: #f4fafd;}
.stNumberInput input {background: #e3f0f7 !important; color: #0b1f3a !important; border-radius: 0 !important;
  font-family: 'IBM Plex Mono', monospace !important;}
.stButton button, .stDownloadButton button {border-radius: 0 !important; border: 2px solid #0b1f3a !important;
  background: #e3f0f7 !important; font-weight: 600;}
.stButton button p, .stDownloadButton button p {color: #0b1f3a !important;}
.stButton button[kind="primary"], .stButton button[data-testid="stBaseButton-primary"] {background: #0b1f3a !important;}
.stButton button[kind="primary"] p, .stButton button[data-testid="stBaseButton-primary"] p {color: #f6e75a !important;}
@media (max-width: 640px) {
  .row {grid-template-columns: 1fr auto; }
  .row .rs {grid-column: 1 / -1;}
  .row .rv {font-size: 1.6rem;}
}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

# ---------------- DATA + INPUT DEFAULTS ----------------
if "data" not in st.session_state:
    st.session_state.data = generate_mission()
df = st.session_state.data

TYPICAL = dict(in_hr=66, in_sys=110, in_dia=70, in_glu=87, in_temp=36.7,
               in_sleep=7.5, in_rad=0.35, in_mood=4)
ROUGH = dict(in_hr=112, in_sys=146, in_dia=92, in_glu=118, in_temp=37.6,
             in_sleep=4.5, in_rad=0.40, in_mood=2)
for k, v in TYPICAL.items():
    st.session_state.setdefault(k, v)
st.session_state.setdefault("view_day", len(df))


def flags_for(data, i):
    """evaluate() for day i, cached: a day's flags only depend on that day and the days before it."""
    key = (i, int(pd.util.hash_pandas_object(data.iloc[:i + 1], index=False).sum()))
    cache = st.session_state.setdefault("flag_cache", {})
    if key not in cache:
        cache[key] = evaluate(data, i)
    return cache[key]


def load_values(vals):
    st.session_state.update(vals)


def save_checkin():
    s = st.session_state
    new = dict(day=len(s.data) + 1, heart_rate=s.in_hr, systolic=s.in_sys, diastolic=s.in_dia,
               glucose=s.in_glu, temp_c=round(s.in_temp, 1), sleep_hrs=s.in_sleep, mood=int(s.in_mood),
               radiation_msv=round(s.in_rad, 2))
    s.data = pd.concat([s.data, pd.DataFrame([new])], ignore_index=True)
    s.view_day = new["day"]
    s.update(TYPICAL)


def reset_mission():
    st.session_state.data = generate_mission()
    st.session_state.view_day = len(st.session_state.data)
    st.session_state.update(TYPICAL)


def stat(label, value, unit="", bar=None):
    b = f'<div class="bar"><span style="width:{min(bar, 1) * 100:.1f}%"></span></div>' if bar is not None else ""
    return f'<div class="stat"><div class="k">{label}</div><div class="v">{value}<small> {unit}</small></div>{b}</div>'


def chart_layout(fig, height, ytitle=""):
    fig.update_layout(template="simple_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=INK, family="IBM Plex Mono, monospace"), height=height,
                      xaxis_title="Mission day", yaxis_title=ytitle, hovermode="x unified",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                      margin=dict(l=10, r=10, t=30, b=10))
    return fig


all_flags = [flags_for(df, i) for i in range(len(df))]
day_level = [overall(f) for f in all_flags]

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
            b.number_input("Sleep (hrs)", 0.0, 14.0, step=0.5, format="%.1f", key="in_sleep")
            a.number_input("Systolic BP (mmHg)", 60, 250, key="in_sys")
            b.number_input("Diastolic BP (mmHg)", 30, 150, key="in_dia")
            a.number_input("Blood sugar (mg/dL)", 30, 400, key="in_glu",
                           help="Fasting reading: ranges assume you haven't eaten for 8 hours.")
            b.number_input("Body temp (°C)", 33.0, 42.0, step=0.1, format="%.1f", key="in_temp")
            a.number_input("Radiation (mSv)", 0.0, 10.0, step=0.05, format="%.2f", key="in_rad",
                           help="Today's dose from your personal dosimeter.")
            b.slider("Mood (1-5)", 1, 5, key="in_mood", help="1 = very low, 5 = great")
            st.button(f"Save day {len(df) + 1}", type="primary", on_click=save_checkin, width="stretch")
            p1, p2 = st.columns(2)
            p1.button("Typical day", on_click=load_values, args=(TYPICAL,), width="stretch")
            p2.button("Rough day (demo)", on_click=load_values, args=(ROUGH,), width="stretch")

        cum = df["radiation_msv"].sum()
        s1, s2 = st.columns(2)
        s1.markdown(stat("MISSION DOSE", f"{cum:.1f}", "mSv", cum / CAREER_LIMIT_MSV)
                    + f'<div class="tlcap"><span>{cum / CAREER_LIMIT_MSV:.1%} of {CAREER_LIMIT_MSV} mSv career limit</span></div>',
                    unsafe_allow_html=True)
        s2.markdown(stat("DAYS FLAGGED", f"{sum(lv != 'ok' for lv in day_level)}", f"/ {len(df)}"),
                    unsafe_allow_html=True)

    # ----- right: readout for the selected day -----
    with right:
        day = st.slider("Viewing mission day", 1, len(df), key="view_day")
        idx = day - 1
        row = df.iloc[idx]
        flags = all_flags[idx]
        lvl = day_level[idx]

        cells = "".join(f'<span class="{"on" if i == idx else ""}" title="Day {i + 1}: {WORDS[lv]}" '
                        f'style="background:{COLORS[lv]}"></span>' for i, lv in enumerate(day_level))
        st.markdown(f'<div class="tl" style="grid-template-columns:repeat({len(df)},1fr)">{cells}</div><div class="tlcap"><span>DAY 1</span>'
                    f'<span>MISSION TIMELINE</span><span>DAY {len(df)}</span></div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="strip"><span class="d">DAY {day}</span>'
            f'<span class="s" style="color:{COLORS[lvl]}">{OVERALL[lvl]}</span>'
            f'<span class="f">{len(flags)} FLAG{"" if len(flags) == 1 else "S"}</span></div>',
            unsafe_allow_html=True)

        flagged = {f["indicator"]: f["level"] for f in flags}
        c1, c2 = st.columns(2, gap="large")
        for col, group in ((c1, INDICATORS[:4]), (c2, INDICATORS[4:])):
            html = ""
            for ind in group:
                s = flagged.get(ind, status(ind, row[ind]))
                prev = df[ind].iloc[max(0, idx - BASELINE_DAYS):idx]
                base = (f"your normal {fmt(ind, prev.mean())}" if len(prev) >= MIN_BASELINE
                        else "building baseline")
                html += (f'<div class="row"><span class="rl">{LABELS[ind]}<small>{base}</small></span>'
                         f'<span class="rv">{fmt(ind, row[ind])}<small> {UNITS[ind]}</small></span>'
                         f'<span class="rs" style="color:{COLORS[s]}"><span class="dot {s}" '
                         f'style="background:{COLORS[s]};box-shadow:0 0 8px {COLORS[s]}"></span>{WORDS[s]}</span></div>')
            col.markdown(html, unsafe_allow_html=True)

        if needs_flight_surgeon(flags):
            st.markdown('<div class="alertbar">CONTACT YOUR FLIGHT SURGEON. '
                        'Help from Earth is delayed, so do not wait.</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec">WHY FLAGGED</div>', unsafe_allow_html=True)
        if not flags:
            st.markdown("**Nothing flagged.** Every reading is inside its safe range and close to your own normal.")
        for f in sorted(flags, key=lambda f: f["level"] != "alert"):
            st.markdown(
                f'<div class="flag" style="border-left-color:{COLORS[f["level"]]}">'
                f'<div class="ft">{f["title"]}</div><div>{f["why"]}</div>'
                f'<div class="fm">HAZARD: {f["hazard"]} / RISK: {f["risk"]}</div>'
                f'<div class="fa">&rarr; {f["action"]}</div></div>', unsafe_allow_html=True)

# ---------------- TRENDS ----------------
with tab_trends:
    l, r = st.columns([1, 3], gap="large")
    ind = l.selectbox("Indicator", INDICATORS, format_func=lambda k: LABELS[k])
    l.caption("Navy line: your readings, with flagged days marked in amber (caution) and red (urgent). "
              f"Dotted blue: your own {BASELINE_DAYS}-day baseline. "
              "Background bands: safe, caution and urgent zones.")
    l.markdown(f"**Hazard:** {HAZARD[ind][0]}  \n**Risk:** {HAZARD[ind][1]}")
    l.download_button("Download mission log (CSV)", df.to_csv(index=False), "orbit_check_log.csv",
                      "text/csv", width="stretch")
    l.button("Reset to demo mission", on_click=reset_mission, width="stretch")

    lim = LIMITS[ind]
    cuts = [v for v in (lim.alert_lo, lim.warn_lo, lim.warn_hi, lim.alert_hi) if v is not None]
    pad = (max(cuts + [df[ind].max()]) - min(cuts + [df[ind].min()])) * 0.12 or 1
    y0, y1 = min(cuts + [df[ind].min()]) - pad, max(cuts + [df[ind].max()]) + pad
    if ind in ("mood", "radiation_msv", "sleep_hrs"):
        y0 = max(y0, 0)
    edges = [y0, lim.alert_lo, lim.warn_lo, lim.warn_hi, lim.alert_hi, y1]
    zones = ["alert", "warn", "ok", "warn", "alert"]

    fig = go.Figure()
    lo = y0
    for z, hi in zip(zones, edges[1:]):
        if hi is None:
            continue
        hi = min(max(hi, y0), y1)
        if hi > lo:
            fig.add_hrect(y0=lo, y1=hi, fillcolor=BANDS[z], line_width=0, layer="below")
        lo = hi

    levels = [next((f["level"] for f in fl if f["indicator"] == ind), "ok") for fl in all_flags]
    fig.add_scatter(x=df["day"], y=df[ind], mode="lines", name=LABELS[ind],
                    line=dict(color=INK, width=2.5), hovertemplate="%{y}")
    fig.add_scatter(x=df["day"], y=df[ind].rolling(BASELINE_DAYS, min_periods=MIN_BASELINE).mean(),
                    mode="lines", name=f"Your {BASELINE_DAYS}-day baseline",
                    line=dict(dash="dot", color=ACCENT, width=3), hovertemplate="%{y:.1f}")
    for lv in ("warn", "alert"):
        m = [x == lv for x in levels]
        if any(m):
            fig.add_scatter(x=df["day"][m], y=df[ind][m], mode="markers", name=f"Flagged: {WORDS[lv].lower()}",
                            marker=dict(color=COLORS[lv], size=10, line=dict(color="white", width=1.5)),
                            hoverinfo="skip")
    fig.update_yaxes(range=[y0, y1])
    r.plotly_chart(chart_layout(fig, 440, UNITS[ind]), width="stretch", config={"displayModeBar": False})

    st.markdown('<div class="sec">CUMULATIVE RADIATION DOSE (mSv)</div>', unsafe_allow_html=True)
    cumfig = go.Figure(go.Scatter(x=df["day"], y=df["radiation_msv"].cumsum(), fill="tozeroy", name="Mission dose",
                                  line=dict(color=INK, width=2), fillcolor="rgba(246,231,90,.75)",
                                  hovertemplate="%{y:.1f} mSv"))
    spikes = df[[status("radiation_msv", v) == "alert" for v in df["radiation_msv"]]]
    for d in spikes["day"]:
        cumfig.add_vline(x=d, line_dash="dot", line_color=COLORS["alert"],
                         annotation_text=f"Day {d} spike", annotation_position="top left")
    st.plotly_chart(chart_layout(cumfig, 260, "mSv"), width="stretch", config={"displayModeBar": False})
    st.caption(f"Career limit: {CAREER_LIMIT_MSV} mSv. This mission so far: "
               f"{df['radiation_msv'].sum():.1f} mSv ({df['radiation_msv'].sum() / CAREER_LIMIT_MSV:.1%}).")

# ---------------- GUIDE ----------------


def describe(lim):
    """Plain-text green / caution / urgent ranges for the Guide table."""
    hi_op, hi_not = ("≥", "<") if lim.hi_inclusive else (">", "≤")
    lo = lim.warn_lo if lim.warn_lo is not None else lim.alert_lo
    hi = lim.warn_hi if lim.warn_hi is not None else lim.alert_hi
    green = " and ".join(p for p in (f"≥ {lo}" if lo is not None else "",
                                     f"{hi_not} {hi}" if hi is not None else "") if p)
    caution = " or ".join(p for p in (f"< {lim.warn_lo}" if lim.warn_lo is not None else "",
                                      f"{hi_op} {lim.warn_hi}" if lim.warn_hi is not None else "") if p)
    urgent = " or ".join(p for p in (f"< {lim.alert_lo}" if lim.alert_lo is not None else "",
                                     f"{hi_op} {lim.alert_hi}" if lim.alert_hi is not None else "") if p)
    return green, caution or "–", urgent or "–"


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

    st.markdown('<div class="sec">SAFE RANGES WE USE</div>', unsafe_allow_html=True)
    rows = ""
    for ind in INDICATORS:
        g, c, u = describe(LIMITS[ind])
        rows += (f'<tr><td><b>{LABELS[ind]}</b> <span class="mono">({UNITS[ind]})</span></td>'
                 f'<td class="m" style="color:{COLORS["ok"]}">{g}</td>'
                 f'<td class="m" style="color:{COLORS["warn"]}">{c}</td>'
                 f'<td class="m" style="color:{COLORS["alert"]}">{u}</td>'
                 f'<td>{LIMITS[ind].source}</td><td>{HAZARD[ind][0]}</td></tr>')
    st.markdown('<div style="overflow-x:auto"><table class="rng"><tr><th>MEASUREMENT</th><th>NORMAL</th>'
                f'<th>CAUTION</th><th>URGENT</th><th>SOURCE</th><th>HAZARD</th></tr>{rows}</table></div>',
                unsafe_allow_html=True)
    st.caption("Also urgent: blood pressure of 180/120 or higher, 3 nights in a row under 6 hours of sleep, "
               "and 3 days in a row with mood at 2 or lower.")

    a, b = st.columns([1.3, 1], gap="large")
    a.markdown('<div class="sec">HOW THE APP THINKS</div>', unsafe_allow_html=True)
    a.write("Every reading goes through three checks:\n"
            "1. **Safe range.** Is it inside the medical range above?\n"
            f"2. **Your own normal.** Is it far (3+ standard deviations) from your last {BASELINE_DAYS} days? "
            "A change can matter even inside the safe range.\n"
            "3. **The whole picture.** An Isolation Forest model compares today's full set of readings with "
            "every earlier day of the mission and flags unusual combinations.\n\n"
            "Each flag is explained and linked to a NASA hazard. Because you are far from Earth, "
            "any urgent flag (or 3+ cautions) tells you to contact your flight surgeon.")
    b.markdown('<div class="sec">MEASURING TIPS</div>', unsafe_allow_html=True)
    b.write("- **Heart rate and BP:** sit quietly for 5 minutes first.\n"
            "- **Blood sugar:** measure fasting, before breakfast.\n"
            "- **Temperature:** wait 15 minutes after exercise.\n"
            "- **Sleep and mood:** log them honestly. Small changes matter over time.")

# ---------------- ABOUT ----------------
with tab_about:
    st.markdown('<div class="sec">ABOUT THIS PROTOTYPE</div>', unsafe_allow_html=True)
    st.write("**Simulated data.** The 90-day mission is generated by our own script, with problems injected "
             "on purpose (a sleep-loss stretch, a solar particle event, rising blood pressure, a blood sugar bump) "
             "so every kind of flag can be demonstrated. No real astronaut data is used.")
    st.write("**Safe ranges** come from the American Heart Association, CDC and American Diabetes Association, "
             "with some caution/urgent bands set by our team. See the Guide tab for the full table.")
    st.write("**Sources:** NASA Human Research Program (5 Hazards, Risks of Human Spaceflight); "
             "CSA article on monitoring radiation for astronaut health.")
    st.write("**Not medical advice.** This is a hackathon prototype for the 2026 NASA Space Apps Challenge.")
