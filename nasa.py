"""Loaders for the real NASA data saved in data/ by nasa_data.py.

Every loader returns an empty table if its file is missing, so the app still runs
(on purely simulated data) without the downloads.
"""
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA = Path(__file__).parent / "data"

# Inspiration4 sample times: L = days before launch, R = days after return.
TIMEPOINTS = ["L-92", "L-44", "L-3", "R+1", "R+45", "R+82", "R+194"]
TP_DAY = {tp: int(tp[1:]) for tp in TIMEPOINTS}          # "L-92" -> -92, "R+45" -> 45
CREW = {"C001": "Crew 1", "C002": "Crew 2", "C003": "Crew 3", "C004": "Crew 4"}

# How strongly a DONKI event reaches a crew near Earth.
# STEREO-A sits far from Earth, so an event seen only there never reached us.
SEVERITY_WORDS = {2: "strong (>100 MeV protons)", 1: "moderate (>10 MeV protons)"}


def _severity(instruments):
    if "SEISS >100 MeV" in instruments:
        return 2
    if "GOES" in instruments or "SOHO" in instruments:
        return 1
    return 0


@lru_cache(maxsize=1)
def sep_events():
    """One row per day with an observed solar energetic particle event (NASA DONKI, 2021-2025)."""
    f = DATA / "donki_sep_events.csv"
    if not f.exists():
        return pd.DataFrame(columns=["date", "instruments", "detections", "link", "severity"])
    df = pd.read_csv(f, parse_dates=["date"])
    df["severity"] = df["instruments"].map(_severity)
    return df


def sep_on(day):
    """The near-Earth solar particle event on a calendar day, or None."""
    ev = sep_events()
    hit = ev[(ev["date"] == pd.Timestamp(day).normalize()) & (ev["severity"] > 0)]
    return None if hit.empty else hit.iloc[0]


def sep_label(row):
    return f"{row['date']:%d %b %Y}: {SEVERITY_WORDS[row['severity']]}"


def data_range():
    ev = sep_events()
    return (ev["date"].min(), ev["date"].max()) if len(ev) else (None, None)


@lru_cache(maxsize=1)
def crew_glucose():
    """Inspiration4 crew blood sugar at each sample time (NASA OSDR OSD-575)."""
    f = DATA / "inspiration4_cmp.csv"
    if not f.exists():
        return pd.DataFrame(columns=["crew", "timepoint", "day", "value"])
    df = pd.read_csv(f)
    g = df[df["ANALYTE"] == "GLUCOSE"].rename(columns={"VALUE": "value", "timepoint": "timepoint"})
    g = g.assign(crew=g["SUBJECT_ID"].map(CREW), day=g["timepoint"].map(TP_DAY))
    return g[["crew", "timepoint", "day", "value"]].sort_values(["crew", "day"]).reset_index(drop=True)


@lru_cache(maxsize=1)
def crew_wbc():
    """Inspiration4 crew white blood cell count, thousand cells/uL (NASA OSDR OSD-569)."""
    f = DATA / "inspiration4_cbc.csv"
    if not f.exists():
        return pd.DataFrame(columns=["crew", "timepoint", "day", "value", "lo", "hi"])
    df = pd.read_csv(f)
    parts = df["Sample Name"].str.split("_", expand=True)      # C001_whole-blood_L-3_cbc
    out = pd.DataFrame({
        "crew": parts[0].map(CREW), "timepoint": parts[2], "day": parts[2].map(TP_DAY),
        "value": df["white_blood_cell_count_value_thousand_per_microliter"],
        "lo": df["white_blood_cell_count_range_min_thousand_per_microliter"],
        "hi": df["white_blood_cell_count_range_max_thousand_per_microliter"],
    })
    return out.sort_values(["crew", "day"]).reset_index(drop=True)
