""SECTION 1: Simulated mission data (all values are fake, for the prototype only)."""
import numpy as np
import pandas as pd
 
 
def generate_mission(days=90, seed=42):
    rng = np.random.default_rng(seed)
    d = np.arange(1, days + 1)
    df = pd.DataFrame({"day": d})
 
    # Normal "healthy astronaut" values with small daily noise
    df["heart_rate"] = rng.normal(64, 3, days)
    df["systolic"] = rng.normal(118, 4, days)
    df["diastolic"] = rng.normal(76, 3, days)
    df["glucose"] = rng.normal(92, 5, days)
    df["temp_c"] = rng.normal(36.7, 0.15, days)
    df["sleep_hrs"] = rng.normal(7.2, 0.5, days)
    df["mood"] = rng.normal(4.0, 0.4, days)
    df["radiation_msv"] = rng.normal(0.6, 0.05, days)
 
    # Injected problems so the demo has something to catch
    dip = (d >= 40) & (d <= 55)                      # sleep loss + low mood + higher HR
    df.loc[dip, "sleep_hrs"] -= 2.2
    df.loc[dip, "mood"] -= 1.3
    df.loc[dip, "heart_rate"] += 11
 
    late = d >= 65                                   # blood pressure slowly climbs
    df.loc[late, "systolic"] += np.linspace(0, 20, late.sum())
 
    df.loc[(d >= 75) & (d <= 80), "glucose"] += 50   # blood sugar bump
    df.loc[d == 60, "radiation_msv"] += 1.5          # radiation spike (solar event)
 
    df["mood"] = df["mood"].clip(1, 5)
    return df.round(2)
