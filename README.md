# Orbit Check 🚀
# 🪐 Orbit Check

**Astronaut health monitoring software, built for the 2026 NASA Space Apps Challenge.**
**A friendly daily health check-in for astronauts, built for the 2026 NASA Space Apps Challenge.**

> ⚠️ Prototype using simulated data. Not medical advice.
> ⚠️ This is a hackathon prototype. The demo astronaut's health readings are simulated, while the space weather, astronaut blood tests and radiation levels come from real NASA data and published studies. It isn't a medical device, and it doesn't give medical advice.

## Challenge
---

Create Health Monitoring Software for Astronauts on Space Missions
## Why we built this
We built this for the NASA Space Apps Challenge; our project turns open NASA data into something people can explore and act on.
## What It Does
Picture yourself on Mars. You've slept badly three nights running, your head hurts, and you can't tell if it's just a rough week or the start of something serious. The doctor is on Earth, and a message takes up to 24 minutes to get there and the same again to come back.

Orbit Check lets an astronaut log daily health readings, tracks them over a mission, and flags early warning signs. It learns each astronaut's personal baseline and explains every flag in plain English.
That's the problem we wanted to solve. Astronauts are brilliant, but they aren't all doctors, and far from Earth they need to spot trouble early on their own. Orbit Check is the crewmate who quietly keeps track, explains what the numbers mean in plain words, and tells you when it's time to call for help.

## Features
**The challenge:** *Create Health Monitoring Software for Astronauts on Space Missions.*

- **Daily Check-In:** heart rate, blood pressure, blood sugar, temperature, sleep, mood, radiation dose
- **Dashboard:** green/yellow/red status for each indicator and a mission day counter
- **Trend Charts:** personal baseline, safe range, and flagged days
- **Smart Flags:** fixed safety thresholds, personal baseline comparison, and multi-day patterns
- **"Why Flagged" Panel:** explains each flag and links it to one of NASA's five hazards (isolation, gravity, radiation, closed environment, distance from Earth)
- **Action Guidance:** next steps, with a "Contact flight surgeon" alert for serious issues
- **Simulated Mission Data:** a 90-day generator with injected problems for demos
## What it does

## How to Run
Every day, the astronaut spends a couple of minutes logging a few simple things:

- heart rate and blood pressure
- blood sugar and temperature
- how long they slept and how they're feeling
- their radiation dose for the day

Orbit Check then gives each reading a color:
- 🟢 **All good:** in the safe range and close to your usual.
- 🟠 **Heads up:** worth a second look.
- 🔴 **Act now:** follow the advice shown and contact your flight surgeon.

Every flag comes with a short, human explanation, the NASA hazard it relates to, and one clear next step.

## How it fits the challenge

| The challenge asked for… | What Orbit Check does |
|---|---|
| **Insights for different environments** | Pick a space station, a deep-space spacecraft, a lunar rover, a Moon base or a Mars base. Each one changes the gravity, how long messages to Earth take, how much radiation is normal, what counts as too much, the daily routine and the risks we talk about. |
| **Prompts to measure or act** | A daily routine runs on the mission clock (UTC, like the space station). A banner tells you what's due now, what's overdue and what's coming up, with simple how-to steps for each task. |
| **Gamification** | Earn XP, level up from Cadet to Mission Legend, keep a routine streak going, collect 10 badges, answer a daily space-health question and climb the crew leaderboard. Points only come from good habits, never from your health numbers, so nobody is ever tempted to fudge a reading. |
| **Dynamic charts** | A "whole mission at a glance" grid with one colored square per reading, plus a detailed chart for any measurement. It has zoom, time windows, your personal average line, and a second measurement you can lay on top to compare. |
| **Color coding** | Green, amber and red everywhere: on readings, the mission timeline, the routine and the charts. Each color is always paired with words, so it works for people who find colors hard to tell apart. |
| **Simple instructions** | Step-by-step "how to measure" guides, a "learn more" under every flag, a "what it is and why it matters in space" note for every measurement, and a daily quiz. |

## The whole tour

- **Dashboard:** log today's check-in, add a note, and see how any day looks. You can edit a saved day, or delete the latest one if you made a mistake.
- **Routine & Rewards:** today's checklist on the mission clock, your level, streak and badges, the question of the day, and the crew leaderboard.
- **Trends:** the whole mission at a glance, a closer look at any measurement, and your running radiation total against the 600 mSv career limit.
- **NASA Data:**
  - Every real solar storm NASA recorded from 2021 to 2025. Your mission replays them on its calendar dates, so a real storm becomes a real alert.
  - Real blood tests from the four SpaceX Inspiration4 astronauts.
- **Guide:** what the colors mean, how to take each measurement, how the five environments differ, and the exact safe ranges we use.
- **Crew members:** everyone gets their own log, personal baseline and mission setting. Add a profile photo by taking one with your camera or uploading one.
- **Saved every day:** check-ins are stored in a small database, so they're still there when you come back.

### How it decides something's wrong

Each reading gets three checks:

1. **Is it outside a medical safe range?** Ranges come from the American Heart Association, the CDC and the American Diabetes Association, plus a few bands our team set (see [thresholds.md](thresholds.md)).
2. **Is it unusual *for you*?** A heart rate of 85 is normal for lots of people, but if yours is usually 62, that's worth noticing. We compare each reading to your own last 14 days.
3. **Does today look odd overall?** A small machine-learning model (an Isolation Forest) notices days when the readings *together* look unlike the rest of your mission.

It also watches for patterns over several days: three short nights in a row, three low-mood days in a row, a blood pressure emergency, or a real solar storm on that date.

## Try it yourself

You'll need Python 3.11 or newer.

```bash
git clone https://github.com/nayanikav-spec/Orbit_Check.git
cd Orbit_Check
pip install -r requirements.txt
streamlit run app.py
```

Your browser opens with a demo astronaut who already has 90 days of data. Have a look around, then try logging day 91.

A few handy things:
- **Run the tests:** `pip install pytest && python -m pytest`
- **Start fresh:** delete `data/orbit_check.db`. It's recreated with the demo astronaut next time.
- **Refresh the NASA data:** get a free key at [api.nasa.gov](https://api.nasa.gov), then run `NASA_API_KEY=your_key python nasa_data.py`. You don't need to; the data is already saved in `data/`.

### Putting it online

The easiest way is [Streamlit Community Cloud](https://share.streamlit.io), which is free:

1. Sign in with GitHub and click **Create app**.
2. Pick this repo, the `main` branch and `app.py`, and choose Python 3.11 or newer.
3. Click **Deploy**. A few minutes later you'll have a link anyone can open.

Good to know: on the free plan, saved check-ins and photos are cleared whenever the site restarts or updates. That's perfect for a demo; a real mission would need a permanent database.

## What's inside

| File | What it does |
|---|---|
| `app.py` | The web app itself: every tab, chart and button |
| `rules.py` | The health checks and the plain-English explanations |
| `environments.py` | The five mission settings: gravity, signal delay, radiation, risks and photos |
| `routine.py` | The daily routine and what's due next |
| `game.py` | XP, levels, streaks and badges |
| `learn.py` | The how-to guides and quiz questions |
| `storage.py` | Saves each crew member's days, routine and photo |
| `simulate.py` | Makes the demo astronaut's 90-day mission |
| `nasa.py` and `nasa_data.py` | Load and download the real NASA data |
| `data/` | The saved NASA datasets |
| `thresholds.md` | Our research notes behind every safe range |
| `tests/` | 53 checks that keep everything working |

**Built with:** Python, Streamlit, Plotly, pandas, NumPy, scikit-learn and Pillow.

## Where the information comes from

## Tech Stack
**Real NASA data**
- [NASA DONKI](https://ccmc.gsfc.nasa.gov/tools/DONKI/): solar storms (solar energetic particle events) from 2021 to 2025.
- [NASA Open Science Data Repository](https://osdr.nasa.gov): SpaceX Inspiration4 crew blood tests, studies OSD-575 (metabolic panel) and OSD-569 (blood count).
- NASA Human Research Program: the five hazards of human spaceflight and NASA's named health risks.

- Python
- Streamlit (web app)
- Plotly (charts)
- pandas and NumPy (data and simulated mission generator)
- scikit-learn (Isolation Forest anomaly detection)
**How much radiation is normal in each place** (published measurements)
- Deep space: 1.84 mSv a day, measured by Curiosity's RAD instrument on the way to Mars (Zeitlin et al., *Science*, 2013).
- Mars surface: 0.64 mSv a day, also by Curiosity's RAD (Hassler et al., *Science*, 2014).
- Moon surface: 1.37 mSv a day, measured by the Chang'e 4 lander (Zhang et al., *Science Advances*, 2020).

**Safe ranges**
- American Heart Association, CDC and American Diabetes Association, plus team-set bands (all in [thresholds.md](thresholds.md)).

## Data Sources
**Photos** (NASA Image and Video Library, public domain; they don't imply NASA endorsement)
- The space station over Earth (s97e5104)
- Orion on Artemis I (orion_earth_moon_20221121)
- The Apollo 15 lunar rover (as15-86-11603)
- Earth setting over the Moon on Artemis II (art002e021278)
- A sunset on Mars seen by Curiosity (PIA19400, NASA/JPL-Caltech/MSSS)
- A spacewalk outside the space station (iss059e002710)

- Simulated 90-day mission data generated by our own Python script
- NASA Human Research Program (five hazards of human spaceflight)
- NASA Open Science Data Repository
- American Heart Association, CDC, and American Diabetes Association (reference ranges for safety thresholds)
**What's simulated:** the demo astronaut's daily health readings, the extra radiation added on solar storm days, and the demo routine history.

## Team
## The team

- **SaiNayanika Vakkalanka**: Coding and development (app, data generator, flag logic, AI model)
- **Shoury Vasishta**: Research (health thresholds, NASA hazard links, data sources, documentation, pitch)
- **SaiNayanika Vakkalanka:** coding and development (the app, the data generator, the flag logic and the AI model).
- **Shoury Vasishta:** research (health thresholds, NASA hazard links, data sources, documentation and the pitch).

## Disclaimer
## One last thing

This is a hackathon prototype using simulated data. It is not a medical device and does not provide medical advice.
Orbit Check is a student prototype, not a medical device. Please don't use it to make real health decisions. If something feels wrong, talk to a real doctor. 💛
