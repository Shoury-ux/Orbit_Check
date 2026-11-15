"""SECTION 1: Simulated mission data (all values are fake, for the prototype only)."""
import numpy as np
import pandas as pd


def generate_mission(days=90, seed=42):
    rng = np.random.default_rng(seed)
    d = np.arange(1, days + 1)
    df = pd.DataFrame({"day": d})

    # Normal "healthy astronaut" values with small daily noise
    df["heart_rate"] = rng.normal(66, 3, days)
    df["systolic"] = rng.normal(110, 3.5, days)
    df["diastolic"] = rng.normal(70, 2.5, days)
    df["glucose"] = rng.normal(87, 3.5, days)
    df["temp_c"] = rng.normal(36.7, 0.12, days)
    df["sleep_hrs"] = rng.normal(7.7, 0.3, days)
    df["mood"] = rng.normal(4.2, 0.4, days)
    df["radiation_msv"] = rng.normal(0.35, 0.03, days)   # typical ISS-like daily dose

    # Injected problems so the demo has something to catch
    dip = (d >= 40) & (d <= 55)                      # sleep loss + low mood + higher HR
    df.loc[dip, "sleep_hrs"] -= 2.3
    df.loc[dip, "mood"] -= 1.6
    df.loc[dip, "heart_rate"] += 14

    late = d >= 65                                   # blood pressure slowly climbs
    df.loc[late, "systolic"] += np.linspace(0, 34, late.sum())
    df.loc[late, "diastolic"] += np.linspace(0, 16, late.sum())

    df.loc[(d >= 75) & (d <= 80), "glucose"] += 45   # blood sugar bump
    df.loc[d == 60, "radiation_msv"] += 1.4          # radiation spike (solar particle event)

    df["mood"] = df["mood"].round().clip(1, 5).astype(int)
    df["radiation_msv"] = df["radiation_msv"].clip(lower=0)
    return df.round({"heart_rate": 0, "systolic": 0, "diastolic": 0, "glucose": 0,
                     "temp_c": 1, "sleep_hrs": 1, "radiation_msv": 2})
