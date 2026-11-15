"""Voice mood check: estimates how someone sounds (happy, calm, low or stressed) from a short
recording of them talking about their day.

It listens to HOW you speak (pitch, loudness, speed, voice quality), not WHAT you say, and only
ever SUGGESTS a mood score: the astronaut always confirms or changes it. Recordings are analysed
in memory and never saved.

The model was trained by voice_train.py on RAVDESS, the Ryerson Audio-Visual Database of
Emotional Speech and Song (Livingstone & Russo, PLoS ONE, 2018; CC BY-NC-SA 4.0): 1,440
recordings of 24 professional actors. Only numpy and scipy are needed to run it.
"""
import io
import json
import warnings
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.fft import dct, irfft, rfft
from scipy.io import wavfile
from scipy.signal import resample_poly

MODEL = Path(__file__).parent / "data" / "voice_mood_model.json"
SR = 16000                       # everything is analysed at 16 kHz
FRAME, HOP = 400, 160            # 25 ms frames every 10 ms
N_FFT, N_MELS, N_MFCC = 512, 40, 20
MIN_SECONDS = 1.0

MOODS = ["happy", "calm", "low", "stressed"]
MOOD_WORDS = {"happy": "upbeat", "calm": "calm", "low": "low or tired", "stressed": "tense or stressed"}
MOOD_SCORE = {"happy": 4.6, "calm": 3.9, "low": 2.0, "stressed": 2.2}    # on Orbit Check's 1-5 scale


def load_wav(data):
    """WAV bytes (or a path) -> mono float signal at 16 kHz, peak-normalised."""
    with warnings.catch_warnings():                         # some recorders add extra WAV chunks
        warnings.simplefilter("ignore", wavfile.WavFileWarning)
        sr, x = wavfile.read(io.BytesIO(data) if isinstance(data, (bytes, bytearray)) else data)
    x = np.asarray(x)
    if x.dtype.kind == "i":
        x = x / float(np.iinfo(x.dtype).max)
    elif x.dtype.kind == "u":
        x = (x - 128) / 128.0
    x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != SR:
        g = np.gcd(int(sr), SR)
        x = resample_poly(x, SR // g, int(sr) // g)
    return x / (np.max(np.abs(x)) + 1e-9)


def _frames(x, size, hop):
    if len(x) < size:
        x = np.pad(x, (0, size - len(x)))
    n = 1 + (len(x) - size) // hop
    idx = np.arange(size)[None, :] + hop * np.arange(n)[:, None]
    return x[idx]


def trim(x):
    """Cut leading and trailing silence."""
    e = (_frames(x, FRAME, HOP) ** 2).mean(axis=1)
    on = np.where(e > e.max() * 10 ** (-3.5))[0]
    if not len(on):
        return x
    return x[on[0] * HOP: on[-1] * HOP + FRAME]


@lru_cache(maxsize=1)
def _mel_filters():
    def hz_to_mel(f):
        return 2595 * np.log10(1 + f / 700)

    def mel_to_hz(m):
        return 700 * (10 ** (m / 2595) - 1)
    mels = np.linspace(hz_to_mel(50), hz_to_mel(SR / 2), N_MELS + 2)
    bins = np.floor((N_FFT + 1) * mel_to_hz(mels) / SR).astype(int)
    fb = np.zeros((N_MELS, N_FFT // 2 + 1))
    for m in range(1, N_MELS + 1):
        a, b, c = bins[m - 1], bins[m], bins[m + 1]
        fb[m - 1, a:b] = (np.arange(a, b) - a) / max(b - a, 1)
        fb[m - 1, b:c] = (c - np.arange(b, c)) / max(c - b, 1)
    return fb


def _pitch(x):
    """Fundamental frequency of each 40 ms frame by autocorrelation (NaN when unvoiced)."""
    fr = _frames(x, 640, HOP) * np.hanning(640)
    energy = (fr ** 2).sum(axis=1)
    spec = np.abs(rfft(fr, 1280, axis=1)) ** 2
    ac = irfft(spec, axis=1)[:, :640]
    ac = ac / (ac[:, :1] + 1e-12)
    lo, hi = SR // 400, SR // 75                                  # 75-400 Hz
    lag = lo + np.argmax(ac[:, lo:hi], axis=1)
    peak = ac[np.arange(len(ac)), lag]
    voiced = (peak > 0.45) & (energy > energy.max() * 10 ** (-3))
    return np.where(voiced, SR / lag, np.nan)


def features(x):
    """A fixed-length description of how the voice sounds (about 100 numbers)."""
    x = trim(x)
    fr = _frames(x, FRAME, HOP) * np.hamming(FRAME)
    power = np.abs(rfft(fr, N_FFT, axis=1)) ** 2
    freqs = np.linspace(0, SR / 2, power.shape[1])

    logmel = np.log(power @ _mel_filters().T + 1e-10)
    mfcc = dct(logmel, type=2, norm="ortho", axis=1)[:, 1:N_MFCC + 1]
    dmfcc = np.diff(mfcc, axis=0)

    loud = 10 * np.log10(power.sum(axis=1) + 1e-10)
    speech = loud > loud.max() - 35
    zcr = (np.abs(np.diff(np.sign(fr), axis=1)) > 0).mean(axis=1)
    total = power.sum(axis=1) + 1e-10
    centroid = (power * freqs).sum(axis=1) / total
    cum = np.cumsum(power, axis=1) / total[:, None]
    rolloff = freqs[np.argmax(cum >= 0.85, axis=1)]
    flatness = np.exp(np.log(power + 1e-10).mean(axis=1)) / (power.mean(axis=1) + 1e-10)
    hi_ratio = power[:, freqs > 2000].sum(axis=1) / total

    f0 = _pitch(x)
    v = f0[~np.isnan(f0)]
    semis = 12 * np.log2(v / 100) if len(v) else np.zeros(1)
    slope = np.polyfit(np.arange(len(semis)), semis, 1)[0] if len(semis) > 2 else 0.0
    env = np.convolve(loud, np.ones(5) / 5, mode="same")
    peaks = ((env[1:-1] > env[:-2]) & (env[1:-1] > env[2:]) & (env[1:-1] > np.median(env))).sum()
    seconds = len(x) / SR

    def stats(a, w=None):
        a = a[w] if w is not None and w.any() else a
        return [a.mean(), a.std()]

    out = list(mfcc.mean(axis=0)) + list(mfcc.std(axis=0)) + list(dmfcc.std(axis=0))
    out += [loud[speech].mean() - loud.max(), loud[speech].std(), np.percentile(loud, 95) - np.percentile(loud, 20)]
    out += stats(zcr, speech) + stats(centroid / 1000, speech) + stats(rolloff / 1000, speech)
    out += stats(flatness, speech) + stats(hi_ratio, speech)
    out += [semis.mean(), semis.std(), np.percentile(semis, 90) - np.percentile(semis, 10) if len(v) else 0.0,
            slope, len(v) / max(len(f0), 1), peaks / max(seconds, 1e-3), speech.mean()]
    return np.nan_to_num(np.array(out, dtype=np.float64))


@lru_cache(maxsize=1)
def model():
    """The trained network, stored as plain numbers in a JSON file (no pickles)."""
    if not MODEL.exists():
        return None
    m = json.loads(MODEL.read_text())
    m["layers"] = [(np.array(w), np.array(b)) for w, b in m["layers"]]
    m["mean"], m["scale"] = np.array(m["mean"]), np.array(m["scale"])
    return m


def predict(x):
    """Probabilities for each mood, from a 16 kHz signal."""
    m = model()
    if m is None:
        raise RuntimeError("Voice model not found. Run voice_train.py first.")
    h = (features(x) - m["mean"]) / m["scale"]
    for i, (w, b) in enumerate(m["layers"]):
        h = h @ w + b
        if i < len(m["layers"]) - 1:
            h = np.maximum(h, 0)                                     # ReLU
    p = np.exp(h - h.max())
    return dict(zip(m["classes"], p / p.sum()))


def model_card():
    """Accuracy and training details, for showing in the app."""
    m = model()
    return None if m is None else dict(m["metrics"], n_recordings=m["n_recordings"], n_actors=m["n_actors"],
                                       source=m["source"])


def analyse(wav_bytes):
    """Everything the app shows: the probabilities, the top mood, and a suggested 1-5 score."""
    x = load_wav(wav_bytes)
    if len(trim(x)) / SR < MIN_SECONDS:
        raise ValueError("That was a bit short. Try talking for at least 3 seconds.")
    if np.sqrt(np.mean(x ** 2)) < 0.01:
        raise ValueError("I couldn't hear much. Try again a little closer to the microphone.")
    probs = predict(x)
    top = max(probs, key=probs.get)
    score = sum(p * MOOD_SCORE[k] for k, p in probs.items())
    return dict(probs=probs, top=top, confidence=probs[top], suggested=int(np.clip(round(score), 1, 5)))
