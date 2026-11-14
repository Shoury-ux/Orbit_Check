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
  <span class="chip">SIMULATED DATA</span><span class="chip">PROTOTYPE</span><span
