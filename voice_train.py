"""Train the voice mood model and save it to data/voice_mood_model.json.

    1. Download Audio_Speech_Actors_01-24.zip from https://zenodo.org/records/1188976 (RAVDESS,
       CC BY-NC-SA 4.0) and unzip it.
    2. python voice_train.py path/to/unzipped/folder

RAVDESS file names encode the emotion (third number): 01 neutral, 02 calm, 03 happy, 04 sad,
05 angry, 06 fearful, 07 disgust, 08 surprised. We group them into four moods that matter for a
daily check-in and leave out "surprised", which can be good or bad.

Each recording is also used with fan-like background noise and with a slightly higher and lower
voice, so the model copes with a noisy cabin and with voices it hasn't heard. Accuracy is always
measured on actors the model never trained on.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.signal import lfilter, resample_poly
from sklearn.metrics import confusion_matrix, recall_score
from sklearn.model_selection import GroupKFold
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

import voice

GROUPS = {"01": "calm", "02": "calm", "03": "happy", "04": "sad_low",
          "05": "stressed", "06": "stressed", "07": "stressed"}
NAME = {"sad_low": "low"}
VARIANTS = ["clean", "noisy", "higher", "lower"]


def _noise(n, rng):
    """Pink-ish noise, a bit like a ventilation fan."""
    white = rng.standard_normal(n)
    return lfilter([0.049922, -0.095993, 0.050613, -0.004408], [1, -2.494956, 2.017265, -0.522189], white)


def _variant(x, kind, rng):
    if kind == "noisy":
        n = _noise(len(x), rng)
        snr = rng.uniform(10, 25)
        n *= np.sqrt(np.mean(x ** 2) / (np.mean(n ** 2) * 10 ** (snr / 10)))
        return x + n
    if kind in ("higher", "lower"):                      # resampling shifts pitch and speed together
        up, down = (25, 27) if kind == "higher" else (27, 25)
        return resample_poly(x, up, down) * rng.uniform(0.5, 1.0)
    return x


def _one(args):
    path, kind, seed = args
    x = voice.load_wav(path)
    return voice.features(_variant(x, kind, np.random.default_rng(seed)))


def load(folder):
    rows = []
    for p in sorted(Path(folder).rglob("*.wav")):
        parts = p.stem.split("-")
        if len(parts) == 7 and parts[2] in GROUPS:
            rows.append((p, NAME.get(GROUPS[parts[2]], GROUPS[parts[2]]), int(parts[6])))
    jobs = [(str(p), k, i * 10 + j) for i, (p, _, _) in enumerate(rows) for j, k in enumerate(VARIANTS)]
    with ProcessPoolExecutor() as pool:
        feats = list(pool.map(_one, jobs, chunksize=16))
    X = np.array(feats).reshape(len(rows), len(VARIANTS), -1)
    y = np.array([r[1] for r in rows])
    actors = np.array([r[2] for r in rows])
    return X, y, actors


def _balanced(X, y, rng):
    """Repeat the rarer moods so every mood is equally common in training."""
    classes, counts = np.unique(y, return_counts=True)
    idx = np.concatenate([rng.choice(np.where(y == c)[0], counts.max(), replace=True) for c in classes])
    return X[idx], y[idx]


def _fit(X, y, seed=0):
    scaler = StandardScaler().fit(X)
    Xb, yb = _balanced(scaler.transform(X), y, np.random.default_rng(seed))
    net = MLPClassifier(hidden_layer_sizes=(64,), alpha=0.01, max_iter=600, early_stopping=True,
                        random_state=seed).fit(Xb, yb)
    return scaler, net


def evaluate(X, y, actors):
    """Hold out whole actors: the model is scored only on voices it never heard."""
    pred_clean, pred_noisy = np.empty(len(y), dtype=object), np.empty(len(y), dtype=object)
    for train, test in GroupKFold(n_splits=6).split(X, y, actors):
        scaler, net = _fit(X[train].reshape(-1, X.shape[2]), np.repeat(y[train], len(VARIANTS)))
        pred_clean[test] = net.predict(scaler.transform(X[test, 0]))
        pred_noisy[test] = net.predict(scaler.transform(X[test, 1]))
    classes = sorted(set(y))
    return dict(
        accuracy_clean=float((pred_clean == y).mean()),
        accuracy_noisy=float((pred_noisy == y).mean()),
        balanced_accuracy_clean=float(recall_score(y, pred_clean.astype(str), average="macro")),
        chance=1 / len(classes),
        recall_by_mood={c: float(r) for c, r in zip(classes, recall_score(y, pred_clean.astype(str),
                                                                          labels=classes, average=None))},
        confusion=dict(labels=classes, matrix=confusion_matrix(y, pred_clean.astype(str), labels=classes).tolist()),
    )


def main(folder):
    X, y, actors = load(folder)
    print(f"{len(y)} recordings from {len(set(actors))} actors, {X.shape[2]} voice features each")
    metrics = evaluate(X, y, actors)
    print(json.dumps(metrics, indent=2))
    scaler, net = _fit(X.reshape(-1, X.shape[2]), np.repeat(y, len(VARIANTS)))
    out = dict(
        classes=[str(c) for c in net.classes_],
        mean=scaler.mean_.tolist(), scale=scaler.scale_.tolist(),
        layers=[(w.round(6).tolist(), b.round(6).tolist()) for w, b in zip(net.coefs_, net.intercepts_)],
        metrics=metrics, n_recordings=int(len(y)), n_actors=int(len(set(actors))),
        source="RAVDESS (Livingstone & Russo, 2018), CC BY-NC-SA 4.0, https://zenodo.org/records/1188976",
    )
    voice.MODEL.write_text(json.dumps(out, separators=(",", ":")) + "\n")
    print(f"Saved {voice.MODEL} ({voice.MODEL.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ravdess")
