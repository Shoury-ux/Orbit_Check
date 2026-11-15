"""Mission environments: where the astronaut is changes gravity, signal delay to Earth,
radiation, and which risks matter most.

Expected daily radiation doses are published measurements:
- Space station: our ISS-like baseline (thresholds.md green range is 0.5 mSv/day or less).
- Deep-space spacecraft: 1.84 mSv/day, measured by Curiosity's RAD instrument during its
  cruise to Mars (Zeitlin et al., Science, 2013).
- Moon surface: 1.37 mSv/day, measured by the Chang'e 4 lander (Zhang et al., Science Advances, 2020).
- Mars surface: 0.64 mSv/day, measured by Curiosity's RAD on Mars (Hassler et al., Science, 2014).
Caution and urgent cut-offs above the expected dose, and how much a solar particle event
adds in each place, are team-set and illustrative.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Environment:
    key: str
    name: str
    short: str
    gravity_g: float
    gravity_text: str
    delay_text: str            # one-way signal delay to Earth
    help_text: str             # what "contact your flight surgeon" means here
    expected_msv: float        # typical daily dose
    rad_warn: float            # daily dose above this = caution
    rad_alert: float           # daily dose above this = urgent
    sep_multiplier: float      # how hard a solar particle event hits here (1 = station)
    shelter: str               # where to go during a solar particle event
    risks: list = field(default_factory=list)   # (title, plain explanation)
    exercise: str = ""


ENVIRONMENTS = {
    "station": Environment(
        "station", "Space station (low Earth orbit)", "Space station", 0.0, "Microgravity (0 g)",
        "Live voice and video", "Ground medical support can join a call within minutes.",
        0.35, 0.5, 1.0, 1.0, "the most shielded crew quarters",
        [("Fluid shift", "Without gravity, fluids move toward your head: puffy face, stuffy nose, headaches."),
         ("Bone and muscle loss", "Bones can lose about 1% of their mass a month without daily exercise."),
         ("Noise and CO2", "Fans run all the time and CO2 is higher than on Earth, which can cause headaches.")],
        "2.5 hours: treadmill, bike and resistance machine"),
    "spacecraft": Environment(
        "spacecraft", "Deep-space spacecraft (transit)", "Spacecraft", 0.0, "Microgravity (0 g)",
        "Delayed: up to about 20 minutes each way", "Messages to Earth are delayed, so the crew must act first.",
        1.84, 2.5, 4.0, 3.0, "the storm shelter (water walls around the sleep area)",
        [("Galactic cosmic rays", "Outside Earth's magnetic field, radiation is about 5 times the station's."),
         ("Isolation", "Earth shrinks to a dot and calls home are delayed. Mood needs extra care."),
         ("No quick return", "There's no turning back mid-trip, so small problems must be caught early.")],
        "2 hours on the compact flywheel trainer"),
    "rover": Environment(
        "rover", "Pressurized rover (Moon)", "Lunar rover", 0.16, "Moon gravity (0.16 g)",
        "About 1.3 seconds each way", "Help is close by radio, but the rover may be hours from base.",
        1.37, 1.9, 3.0, 3.0, "the rover's shielded aft cabin, then drive back to base",
        [("Cramped cabin", "Days in a car-sized cabin: back pain, poor sleep and stuck circulation."),
         ("Little shielding", "The rover has thin walls, and the nearest storm shelter may be far away."),
         ("Lunar dust", "Sharp dust gets in with every suit entry and irritates eyes and lungs.")],
        "45 minutes of resistance bands and stretching"),
    "moon": Environment(
        "moon", "Moon base", "Moon base", 0.16, "Moon gravity (0.16 g)",
        "About 1.3 seconds each way", "Ground medical support is a short delay away.",
        1.37, 1.9, 3.0, 2.0, "the regolith-covered shelter module",
        [("Lunar dust", "Sharp, clingy dust irritates eyes, skin and lungs. Keep it out of the habitat."),
         ("Partial gravity", "One-sixth gravity still weakens bones and muscles over months."),
         ("Two-week nights", "The Sun stays down for about 14 days, which can confuse your body clock.")],
        "1.5 hours: treadmill and resistance training"),
    "mars": Environment(
        "mars", "Mars base", "Mars base", 0.38, "Mars gravity (0.38 g)",
        "4 to 24 minutes each way", "A question to Earth can take up to 48 minutes to get answered.",
        0.64, 0.9, 1.6, 0.8, "the shielded core of the habitat",
        [("Distance from Earth", "No resupply for months and slow messages: the crew is its own clinic."),
         ("Toxic dust", "Martian dust contains perchlorates, which can harm the thyroid. Keep it in the airlock."),
         ("Isolation", "Months away from family and Earth in a small crew can wear on mood and teamwork.")],
        "1.5 hours: treadmill and resistance training"),
}
DEFAULT_ENV = "station"


def env(key):
    return ENVIRONMENTS.get(key, ENVIRONMENTS[DEFAULT_ENV])
