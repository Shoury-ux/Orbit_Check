"""Plain-language help: how to take each measurement, what the number means,
why it matters in space, and a small quiz bank. Written for people who are not medics."""

GUIDE = {
    "heart_rate": dict(
        what="How many times your heart beats in one minute while you're resting.",
        how=["Rest quietly for 5 minutes first (no exercise, coffee or talking).",
             "Put two fingers on the thumb side of your wrist, or wear the chest strap.",
             "Count the beats for 30 seconds, then double it.",
             "Log the number. Same time every morning gives the fairest comparison."],
        space="Without gravity your heart doesn't have to pump as hard, so it can slowly weaken. "
              "A fit astronaut may run below 60, which is why the app also compares you to your own normal.",
        tip="A sudden rise of 10+ beats over your normal can be the first sign of illness, stress or poor sleep."),
    "systolic": dict(
        what="Blood pressure is two numbers. The top one (systolic) is the pressure while your heart beats.",
        how=["Sit or strap in with your back supported for 5 minutes.",
             "Wrap the cuff on your bare upper arm, at the same height as your heart.",
             "Keep still and don't talk while it measures.",
             "Take two readings a minute apart and log the second one."],
        space="Fluids shift toward your head in low gravity, which changes how your blood vessels behave. "
              "Rising pressure over weeks is worth catching early.",
        tip="One high reading isn't a diagnosis. A steady climb over days is what to watch."),
    "diastolic": dict(
        what="The bottom blood pressure number: the pressure while your heart rests between beats.",
        how=["It comes from the same cuff reading as the top number. Log both together."],
        space="See systolic: both numbers can change as your body adapts to low gravity.",
        tip="If the bottom number is 90 or more, or the reading is 180/120 or higher, tell your flight surgeon."),
    "glucose": dict(
        what="How much sugar is in your blood. Your body's main fuel.",
        how=["Measure before breakfast, at least 8 hours after your last meal.",
             "Wash and dry your hands (sugar on your fingers skews the reading).",
             "Prick the side of a fingertip with the lancet; it hurts less than the pad.",
             "Touch the drop to the test strip and log the meter's number."],
        space="Stress, a changed routine, and different food and exercise can all nudge blood sugar. "
              "Spaceflight can also make your body respond less well to insulin.",
        tip="If you forgot and already ate, note it in today's notes: the ranges assume fasting."),
    "temp_c": dict(
        what="Your body temperature. A fever is a sign your body is fighting an infection.",
        how=["Wait 15 minutes after exercise, a hot drink or a shower.",
             "Put the thermometer under your tongue and close your lips.",
             "Wait for the beep and log the number in °C."],
        space="Heat doesn't rise away from your body in microgravity, and in a small shared cabin "
              "an infection can spread to the whole crew.",
        tip="38.0 °C or higher is a fever: tell your flight surgeon and limit close contact."),
    "sleep_hrs": dict(
        what="How many hours you actually slept last night, not time spent in your bunk.",
        how=["Check your sleep watch, or estimate when you fell asleep and woke up.",
             "Subtract long wake-ups in the night.",
             "Log it as soon as you're up, before you forget."],
        space="On a station the Sun rises 16 times a day. On the Moon a night lasts two weeks. "
              "Noise, light and stress make good sleep harder everywhere.",
        tip="Three short nights in a row adds up: your reaction time can drop as if you'd been drinking."),
    "mood": dict(
        what="How you feel overall today, from 1 (very low) to 5 (great).",
        how=["Take a breath and ask: how am I really doing today?",
             "Pick the number that fits best. There's no wrong answer and nobody grades it.",
             "If something's on your mind, add a note."],
        space="Months in a small space, far from family and friends, can wear on anyone. "
              "A low mood is a signal, not a weakness.",
        tip="Two or three low days in a row is a good reason to talk to someone you trust."),
    "radiation_msv": dict(
        what="The radiation dose your body received in the last 24 hours, in millisieverts (mSv).",
        how=["Wear your personal dosimeter (crew badge) at all times, even while sleeping.",
             "Each morning, read the last-24-hours value on its display.",
             "Log it. The app keeps your running total against the 600 mSv career limit."],
        space="Outside Earth's thick atmosphere you're hit by particles from the Sun and from deep space. "
              "Over a career this raises cancer risk, which is why the total is capped.",
        tip="During a solar particle event alert, go to the storm shelter first and log later."),
}

QUIZ = [
    dict(q="When should you measure your blood sugar for Orbit Check?",
         options=["Right after a meal", "Before breakfast, after 8 hours without food", "Just before bed"],
         answer=1, explain="The ranges assume a fasting reading, so measure before breakfast."),
    dict(q="Where should the blood pressure cuff be?",
         options=["On your wrist, held above your head", "On your bare upper arm, level with your heart",
                  "Over your sleeve, anywhere on the arm"],
         answer=1, explain="Upper arm, bare skin, heart height. Anything else skews the reading."),
    dict(q="What body temperature counts as a fever?",
         options=["37.0 °C", "37.5 °C", "38.0 °C or higher"],
         answer=2, explain="38.0 °C (100.4 °F) or higher is a fever, per the CDC."),
    dict(q="Why does the app compare you to your OWN normal, not just a standard range?",
         options=["Because standard ranges are wrong", "A big change for you can matter even inside the normal range",
                  "To save battery"],
         answer=1, explain="A heart rate of 85 is normal for many people, but it's a big jump if yours is usually 62."),
    dict(q="What is the career radiation limit used by NASA for astronauts?",
         options=["60 mSv", "600 mSv", "6,000 mSv"],
         answer=1, explain="600 mSv over a whole career. A 90-day deep-space trip can use nearly a third of it."),
    dict(q="A solar particle event alert comes in. What do you do first?",
         options=["Finish your task, then check", "Go to the storm shelter", "Take your temperature"],
         answer=1, explain="Shelter first. Bursts of fast protons can raise your dose within hours."),
    dict(q="Why is sleep harder on a space station?",
         options=["The Sun rises about 16 times a day", "There are no beds", "Gravity keeps you awake"],
         answer=0, explain="Constant sunrises, noise and stress all break up sleep, so protect your sleep window."),
    dict(q="Why do astronauts on a station exercise about 2.5 hours a day?",
         options=["For fun", "To stop bone and muscle loss in microgravity", "To stay warm"],
         answer=1, explain="Without gravity, bones can lose about 1% of their mass a month without exercise."),
    dict(q="Why does lunar or Martian dust matter for health?",
         options=["It's sharp and irritates eyes and lungs; Martian dust can be toxic", "It's harmless",
                  "It only affects the rover"],
         answer=0, explain="Keep dust in the airlock: clean suit seals and watch for eye or breathing problems."),
    dict(q="Your mood has been 2 out of 5 for three days. What's the best step?",
         options=["Ignore it, it'll pass", "Talk to a crewmate or ground support", "Skip logging it"],
         answer=1, explain="Three low days in a row is a signal worth sharing. That's what support is for."),
    dict(q="Why can't a Mars crew just call the doctor when something goes wrong?",
         options=["No phones on Mars", "Signals take 4 to 24 minutes each way", "Doctors don't work weekends"],
         answer=1, explain="A question and answer can take up to 48 minutes, so the crew must spot problems early."),
    dict(q="How should you take your resting heart rate?",
         options=["Right after exercise", "After 5 minutes resting, counting for 30 seconds and doubling",
                  "While talking"],
         answer=1, explain="Rest first and measure the same way each morning so days are comparable."),
]


def quiz_for(day):
    """One question per mission day, cycling through the bank."""
    return QUIZ[(day - 1) % len(QUIZ)]
