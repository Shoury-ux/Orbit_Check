# Orbit Check 🚀

**Astronaut health monitoring software, built for the 2026 NASA Space Apps Challenge.**

> ⚠️ Prototype: simulated vitals, replayed against real NASA space-weather data. Not medical advice.

## Challenge

Create Health Monitoring Software for Astronauts on Space Missions

## What It Does

Orbit Check lets an astronaut log daily health readings, tracks them over a mission, and flags early warning signs. It learns each astronaut's personal baseline and explains every flag in plain English.

## Features

**Built around the challenge brief:**

| Brief asks for | Where it is in Orbit Check |
|---|---|
| Health insights in different environments | Space station, deep-space spacecraft, lunar rover, Moon base and Mars base. Each changes gravity, signal delay to Earth, typical radiation (published measurements) and its radiation limits, routine, risks and shelter advice |
| Prompts to measure or act as part of the routine | A daily routine on the mission clock (UTC). The banner shows what's due now or overdue, and each task has how-to steps |
| Gamification | XP, 6 levels, a routine streak, 10 badges, a daily quiz and a crew leaderboard. XP rewards habits, never health values |
| Dynamic charts | A color-coded mission overview, an interactive trend chart with time windows, a zoom slider and a compare overlay, plus cumulative radiation |
| Color coding | Green/amber/red with matching words everywhere: readings, timeline, routine, overview chart, badges |
| Simple instructions and explanations | Step-by-step measuring guides, a "learn more" under every flag, "what it is / why it matters in space" for every indicator, and the quiz |

**Everything in detail:**


- **Daily Check-In:** heart rate, blood pressure, blood sugar, temperature, sleep, mood, radiation dose, plus a notes field
- **Saved every day:** each check-in is stored in a local SQLite database (`data/orbit_check.db`), so it's still there after a refresh or restart. Edit any saved day, or delete the most recent one
- **Crew members:** add astronauts, each with their own log, mission start date and personal baseline. Start a new mission empty or with demo data
- **Dashboard:** green/yellow/red status for each indicator, your personal "normal" next to every reading, and a color-coded mission timeline
- **Trend Charts:** safe/caution/urgent zones, your personal 14-day baseline, and flagged days marked on the line
- **Smart Flags (three checks):**
  1. Fixed safety thresholds from AHA, CDC and ADA (see [thresholds.md](thresholds.md))
  2. Personal baseline: a reading 3+ standard deviations from your own last 14 days
  3. Whole-picture anomaly detection: an Isolation Forest flags unusual *combinations* of readings
- **Multi-day patterns:** 3 nights of short sleep, 3 days of low mood, and blood pressure crisis (180/120+)
- **"Why Flagged" Panel:** explains each flag and links it to one of NASA's five hazards (isolation, gravity, radiation, closed environment, distance from Earth)
- **Action Guidance:** next steps, with a "Contact flight surgeon" alert for serious issues
- **Radiation tracking:** cumulative mission dose against the 600 mSv career limit
- **Real NASA space weather:** each mission is replayed on real calendar dates, and solar particle events recorded by NASA DONKI become urgent radiation alerts. Pick any 90-day window from 2021 to 2025
- **NASA Data tab:** 2021-2025 solar particle events, plus real SpaceX Inspiration4 crew blood tests (NASA OSDR) run through Orbit Check's ranges
- **Simulated Mission Data:** a 90-day generator with injected problems for demos; download the log as CSV

## How to Run

```bash
git clone https://github.com/nayanikav-spec/Orbit_Check.git
cd Orbit_Check
pip install -r requirements.txt
streamlit run app.py
```

Run the tests with `pip install pytest && python -m pytest`.

The database file `data/orbit_check.db` is created on first run with one demo astronaut, and it isn't committed to Git. To start over, delete the file. On free Streamlit Community Cloud the file lasts while the app is running but is reset when the app restarts or redeploys; for permanent hosted storage, swap `storage.py` for a hosted database.

The NASA data is already saved in `data/`, so the app runs offline. To download it again, get a free key at [api.nasa.gov](https://api.nasa.gov) and run:

```bash
NASA_API_KEY=your_key python nasa_data.py
```

## Project Layout

| File | What it does |
|---|---|
| `app.py` | Streamlit app: check-in form, dashboard, trends, guide |
| `rules.py` | Safe ranges, personal baseline, patterns, anomaly model, plain-English explanations |
| `simulate.py` | 90-day simulated mission with injected problems, on real calendar dates |
| `storage.py` | Saves each crew member's daily check-ins in SQLite |
| `environments.py` | The five mission environments: gravity, signal delay, radiation, risks |
| `routine.py` | The daily routine on the mission clock, and what's due next |
| `game.py` | XP, levels, streaks and badges |
| `learn.py` | Plain-language measuring guides and the quiz |
| `nasa.py` | Loads the saved NASA data (solar particle events, Inspiration4 bloodwork) |
| `nasa_data.py` | Downloads the NASA data into `data/` |
| `data/` | Saved NASA datasets (CSV) |
| `thresholds.md` | Research notes behind every range (kept in sync with `rules.py`) |
| `tests/test_rules.py` | Checks every threshold boundary and each type of flag |

## Tech Stack

- Python
- Streamlit (web app)
- Plotly (charts)
- pandas and NumPy (data and simulated mission generator)
- scikit-learn (Isolation Forest anomaly detection)


## Data Sources

- Simulated 90-day mission vitals generated by our own Python script
- Typical radiation per environment: Curiosity RAD deep-space cruise, 1.84 mSv/day (Zeitlin et al., *Science*, 2013); Curiosity RAD Mars surface, 0.64 mSv/day (Hassler et al., *Science*, 2014); Chang'e 4 lander Moon surface, 1.37 mSv/day (Zhang et al., *Science Advances*, 2020)
- [NASA DONKI](https://ccmc.gsfc.nasa.gov/tools/DONKI/) (Space Weather Database Of Notifications, Knowledge, Information): solar energetic particle events, 2021-2025
- [NASA Open Science Data Repository](https://osdr.nasa.gov): SpaceX Inspiration4 crew blood tests, studies OSD-575 (metabolic panel) and OSD-569 (blood count)
- NASA Human Research Program (five hazards of human spaceflight)
- American Heart Association, CDC, and American Diabetes Association (reference ranges for safety thresholds)

## Team

- **SaiNayanika Vakkalanka**: Coding and development (app, data generator, flag logic, AI model)
- **Shoury Vasishta**: Research (health thresholds, NASA hazard links, data sources, documentation, pitch)

## Disclaimer

This is a hackathon prototype using simulated health data. It is not a medical device and does not provide medical advice.
