""SECTION 2: The rules. Compares readings to safe ranges AND the person's own baseline,
then explains every flag in plain English and ties it to a NASA hazard/risk."""
 
# (warn_low, warn_high, alert_low, alert_high). None = no limit on that side.
# PLACEHOLDER general ranges - replace/confirm with a cited medical source before submitting.
RANGES = {
    "heart_rate":    (50, 100, 40, 120),
    "systolic":      (95, 130, 85, 140),
    "diastolic":     (60, 85, 50, 90),
    "glucose":       (70, 125, 54, 180),
    "temp_c":        (36.0, 37.5, 35.0, 38.0),
    "sleep_hrs":     (6, None, 4.5, None),
    "mood":          (3, None, 2, None),
    "radiation_msv": (None, 1.2, None, 2.5),
}
 
LABELS = {"heart_rate": "Heart rate", "systolic": "Systolic BP", "diastolic": "Diastolic BP",
          "glucose": "Blood sugar", "temp_c": "Body temp", "sleep_hrs": "Sleep",
          "mood": "Mood", "radiation_msv": "Radiation (daily)"}
 
UNITS = {"heart_rate": "bpm", "systolic": "mmHg", "diastolic": "mmHg", "glucose": "mg/dL",
         "temp_c": "C", "sleep_hrs": "hrs", "mood": "/5", "radiation_msv": "mSv"}
 
# indicator -> (NASA hazard, NASA risk). Risk names come from NASA's Risks page;
# the hazard assignment is our own mapping.
HAZARD = {
    "heart_rate":    ("Gravity fields", "Risk of Cardiovascular Adaptations"),
    "systolic":      ("Gravity fields", "Risk of Cardiovascular Adaptations"),
    "diastolic":     ("Gravity fields", "Risk of Cardiovascular Adaptations"),
    "glucose":       ("Hostile/closed environments", "Risk of Inadequate Food and Nutrition"),
    "temp_c":        ("Hostile/closed environments", "Risk of Altered Immune System Responses"),
    "sleep_hrs":     ("Isolation and confinement", "Risk of Inadequate Sleep and Irregular Schedules"),
    "mood":          ("Isolation and confinement", "Risk of Behavioral Changes and Psychiatric Disorders"),
    "radiation_msv": ("Space radiation", "Risk of Radiation-Induced Cancers"),
}
 
ACTIONS = {
    "heart_rate": "Rest, hydrate, and retake the reading in 30 minutes. Keep up your exercise routine.",
    "systolic": "Sit quietly for 5 minutes, then retake it. Log it again tomorrow.",
    "diastolic": "Sit quietly for 5 minutes, then retake it. Log it again tomorrow.",
    "glucose": "Think about your last meal, then retest. Log what you ate.",
    "temp_c": "Retake after 15 minutes and watch for other symptoms.",
    "sleep_hrs": "Protect your sleep window and wind down before bed.",
    "mood": "Talk with a crewmate or schedule a private call with ground support.",
    "radiation_msv": "Follow your mission radiation protocol and check in with ground control.",
}
 
Z_LIMIT = 3.0   # how many "standard deviations from your own normal" counts as a shift
 
 
def status(ind, v):
    wl, wh, al, ah = RANGES[ind]
    if (al is not None and v < al) or (ah is not None and v > ah):
        return "alert"
    if (wl is not None and v < wl) or (wh is not None and v > wh):
        return "warn"
    return "ok"
 
 
def baseline(df, ind, idx, window=14):
    """The person's own recent normal: mean and spread of the previous 14 days."""
    prev = df[ind].iloc[max(0, idx - window):idx]
    if len(prev) < 7:
        return None
    return prev.mean(), prev.std()
 
 
def evaluate(df, idx=None):
    """Return a list of flags for one mission day."""
    idx = len(df) - 1 if idx is None else idx
    row = df.iloc[idx]
    flags = []
 
    for ind in RANGES:
        v, s, b = row[ind], status(ind, row[ind]), baseline(df, ind, idx)
        hazard, risk = HAZARD[ind]
        if s != "ok":
            level = s
            why = (f"{LABELS[ind]} is {v:.1f} {UNITS[ind]}, outside the "
                   f"{'urgent' if s == 'alert' else 'caution'} range.")
            if b:
                why += f" Your own 14-day average is {b[0]:.1f}."
        elif b and b[1] > 0 and abs(v - b[0]) / b[1] >= Z_LIMIT:
            level = "warn"
            why = (f"{LABELS[ind]} is {v:.1f} {UNITS[ind]}. That's in the normal range, but far from "
                   f"YOUR 14-day average of {b[0]:.1f}, so it's a real change for you.")
        else:
            continue
        action = ACTIONS[ind] if level == "warn" else "Contact your flight surgeon. " + ACTIONS[ind]
        flags.append(dict(indicator=ind, level=level, title=f"{LABELS[ind]}: {v:.1f} {UNITS[ind]}",
                          why=why, hazard=hazard, risk=risk, action=action))
 
    # Multi-day pattern: 3 short nights in a row (worse if mood is also low)
    recent = df.iloc[max(0, idx - 2):idx + 1]
    if len(recent) == 3 and (recent["sleep_hrs"] < 6).all():
        low_mood = row["mood"] < 3
        flags.append(dict(
            indicator="pattern", level="alert" if low_mood else "warn",
            title="Sleep-loss pattern (3 nights in a row)",
            why="You've slept under 6 hours three nights running"
                + (" and your mood is low" if low_mood else "")
                + ". Hazards can feed off each other: isolation and chronic sleep loss can make each other worse.",
            hazard="Isolation and confinement", risk="Risk of Inadequate Sleep and Irregular Schedules",
            action=("Contact your flight surgeon. " if low_mood else "") + ACTIONS["sleep_hrs"]))
    return flags
 
 
def overall(flags):
    levels = {f["level"] for f in flags}
    return "alert" if "alert" in levels else "warn" if "warn" in levels else "ok"
 
 
def needs_flight_surgeon(flags):
    """Far from Earth, help is delayed: escalate on any urgent flag or 3+ cautions."""
    return any(f["level"] == "alert" for f in flags) or sum(f["level"] == "warn" for f in flags) >= 3
 
Claude finished the response
