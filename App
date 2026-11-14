"""SECTION 3: The Streamlit app. Run with:  streamlit run app.py"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
 
from rules import (RANGES, LABELS, UNITS, evaluate, status, overall,
                   needs_flight_surgeon)
from simulate import generate_mission
 
st.set_page_config(page_title="Orbit Check", page_icon="🛰️", layout="wide")
ICON = {"ok": "🟢", "warn": "🟡", "alert": "🔴"}
 
# --- data lives in session state so new check-ins get added to it ---
if "data" not in st.session_state:
    st.session_state.data = generate_mission()
df = st.session_state.data
 
st.title("🛰️ Orbit Check")
st.caption("Prototype using SIMULATED data. Not medical advice.")
 
tab_dash, tab_in, tab_trends, tab_guide, tab_about = st.tabs(
    ["Dashboard", "Daily Check-In", "Trends", "Guide", "About"])
 
# ---------------- DASHBOARD ----------------
with tab_dash:
    day = st.slider("Mission day (try day 48 or day 90)", 1, len(df), len(df))
    idx = day - 1
    row = df.iloc[idx]
    flags = evaluate(df, idx)
 
    st.subheader(f"Day {day}: {ICON[overall(flags)]} overall status")
    cols = st.columns(4)
    for i, ind in enumerate(RANGES):
        with cols[i % 4]:
            st.metric(f"{ICON[status(ind, row[ind])]} {LABELS[ind]}", f"{row[ind]:.1f} {UNITS[ind]}")
 
    if not flags:
        st.success("No flags today. Keep logging.")
    else:
        if needs_flight_surgeon(flags):
            st.error("Contact your flight surgeon. Help from Earth is delayed, so don't wait.")
        st.subheader("Why flagged")
        for f in flags:
            with st.expander(f"{ICON[f['level']]} {f['title']}", expanded=f["level"] == "alert"):
                st.write(f["why"])
                st.write(f"**Linked NASA hazard:** {f['hazard']}")
                st.write(f"**NASA risk:** {f['risk']}")
                st.write(f"**What to do:** {f['action']}")
 
# ---------------- CHECK-IN ----------------
with tab_in:
    st.write("Log today's readings.")
    with st.form("checkin"):
        c1, c2 = st.columns(2)
        hr = c1.number_input("Heart rate (bpm)", 30, 220, 64)
        sys_ = c1.number_input("Systolic BP (mmHg)", 60, 250, 118)
        dia = c1.number_input("Diastolic BP (mmHg)", 30, 150, 76)
        glu = c1.number_input("Blood sugar (mg/dL)", 30, 400, 92)
        temp = c2.number_input("Body temp (C)", 33.0, 42.0, 36.7, step=0.1)
        sleep = c2.number_input("Sleep last night (hrs)", 0.0, 14.0, 7.0, step=0.5)
        mood = c2.slider("Mood (1 low - 5 great)", 1, 5, 4)
        rad = c2.number_input("Radiation dose today (mSv)", 0.0, 10.0, 0.6, step=0.1)
        if st.form_submit_button("Save check-in"):
            new = dict(day=len(df) + 1, heart_rate=hr, systolic=sys_, diastolic=dia, glucose=glu,
                       temp_c=temp, sleep_hrs=sleep, mood=mood, radiation_msv=rad)
            st.session_state.data = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            st.success(f"Saved as day {new['day']}. Move the slider on the Dashboard to see it.")
 
# ---------------- TRENDS ----------------
with tab_trends:
    ind = st.selectbox("Indicator", list(RANGES), format_func=lambda k: LABELS[k])
    fig = go.Figure()
    fig.add_scatter(x=df["day"], y=df[ind], mode="lines", name=LABELS[ind])
    fig.add_scatter(x=df["day"], y=df[ind].rolling(14, min_periods=7).mean(),
                    mode="lines", name="Your 14-day baseline", line=dict(dash="dot"))
    wl, wh, al, ah = RANGES[ind]
    for v, color in [(wl, "orange"), (wh, "orange"), (al, "red"), (ah, "red")]:
        if v is not None:
            fig.add_hline(y=v, line_dash="dash", line_color=color)
    fig.update_layout(xaxis_title="Mission day", yaxis_title=UNITS[ind], height=380)
    st.plotly_chart(fig)
 
    st.subheader("Cumulative radiation dose (mSv)")
    st.line_chart(df.set_index("day")["radiation_msv"].cumsum())
 
# ---------------- GUIDE ----------------
with tab_guide:
    st.subheader("How the app thinks")
    st.write("Each reading is checked against a safe range AND against your own recent normal. "
             "Flags are explained and linked to one of NASA's five hazards of spaceflight: "
             "space radiation, isolation and confinement, distance from Earth, gravity fields, "
             "and hostile/closed environments. Because you're far from Earth, urgent flags tell you "
             "when to contact your flight surgeon.")
    st.subheader("Measuring tips")
    st.write("- **Heart rate and BP:** sit quietly for 5 minutes first.\n"
             "- **Blood sugar:** note when you last ate.\n"
             "- **Temperature:** wait 15 minutes after exercise.\n"
             "- **Sleep and mood:** log them honestly. Small changes matter over time.")
 
# ---------------- ABOUT ----------------
with tab_about:
    st.write("**Simulated data.** No real astronaut data is used. Safe ranges are general placeholders.")
    st.write("**Sources:** NASA Human Research Program (5 Hazards, Risks of Human Spaceflight); "
             "CSA article on monitoring radiation for astronaut health.")
    st.write("**Not medical advice.** This is a hackathon prototype.")
