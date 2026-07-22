"""
Appendix Listing: consolidated, reproducible analysis pipeline.
(Consolidates Listings 4-7 from the report: feature extraction,
uniqueness/entropy/k-anonymity, single-day re-identification, and the
composite Privacy Risk Score.)

Reproduces every headline result in the report from the prepared
one-minute mains CSVs (one per dataset/household):

    synd_mains_1min.csv        (from 02_downsample_synd.py)
    snm_b10_mains_1min.csv     (from 03_compute_snm_power.py)
    snm_b11_mains_1min.csv
    snm_b15_mains_1min.csv
    snm_b17_mains_1min.csv

Data preparation note: SynD mains was downsampled with Listing 2; each
SNM home's mains was computed from per-phase V/I/PF and downsampled with
Listing 3; archives were handled with the 7-Zip commands in Listing 1.
All processing used Python 3.12 on Windows 10.

Running this script prints the same PRS and re-identification numbers
reported in Section 4 (SynD PRS ~0.291, Real PRS ~0.889, single-day
re-identification accuracy ~77%).
"""

import pandas as pd
import numpy as np

np.random.seed(0)

FEATURES = [
    "total_kwh", "peak_w", "mean_w", "load_factor",
    "morning_rise_h", "evening_peak_h", "night_day_ratio", "n_peaks",
]


def load(path):
    df = pd.read_csv(path)
    df.columns = ["time", "power_w"][:len(df.columns)]
    df["time"] = pd.to_datetime(df["time"])
    return df.set_index("time")["power_w"].clip(lower=0)


def day_features(d):
    """Listing 4: behavioural feature extraction from one day of mains power."""
    if len(d) < 600:
        return None
    p = d.values
    hrs = d.index.hour + d.index.minute / 60
    peak, mean = p.max(), p.mean()
    if peak <= 0:
        return None

    base = np.median(p)
    thr = base + 0.5 * (peak - base)

    above = (p > thr) & (hrs >= 4)
    morning = float(hrs[np.argmax(above)]) if above.any() else np.nan

    ev = hrs >= 16
    evening = float(hrs[ev][np.argmax(p[ev])]) if ev.any() else np.nan

    nmask = (hrs >= 0) & (hrs < 6)
    en, ed = p[nmask].sum(), p[~nmask].sum()

    sig = (p > thr).astype(int)
    npk = int(((sig[1:] - sig[:-1]) == 1).sum())

    return dict(
        total_kwh=p.sum() / 60 / 1000,
        peak_w=peak,
        mean_w=mean,
        load_factor=mean / peak,
        morning_rise_h=morning,
        evening_peak_h=evening if ev.any() else np.nan,
        night_day_ratio=en / ed if ed > 0 else 0,
        n_peaks=npk,
    )


def extract(path, hid):
    s = load(path)
    rows = []
    for day, d in s.groupby(s.index.normalize()):
        f = day_features(d.dropna())
        if f:
            f["household"] = hid
            rows.append(f)
    return pd.DataFrame(rows).dropna(subset=FEATURES)


def qi(frame, cols, bins=4):
    """Quasi-identifier = quantile-binned feature tuple."""
    b = frame[cols].apply(
        lambda c: pd.qcut(c.rank(method="first"), q=min(bins, len(frame)),
                           labels=False, duplicates="drop")
    )
    return b.astype(str).agg("|".join, axis=1)


def uniqueness_entropy_k(frame, household_level):
    """Listing 5: feature uniqueness, normalized entropy and k-anonymity."""
    qc = ["morning_rise_h", "evening_peak_h", "night_day_ratio", "total_kwh"]
    base = (frame.groupby("household")[qc].mean().reset_index()
            if household_level else frame)

    q = qi(base, qc)
    cls = q.value_counts()
    n = len(q)

    u = cls[cls == 1].sum() / n  # share with a one-of-a-kind signature
    pr = cls.values / n
    H = -(pr * np.log2(pr)).sum()

    return u, (H / np.log2(len(cls)) if len(cls) > 1 else 0.0), int(cls.min())


def single_day_reid(frame, cols=FEATURES):
    """Listing 6: single-day household re-identification
    (leave-one-day-out nearest profile). Score is top-1 accuracy;
    random chance is 1/(number of homes)."""
    arr = frame.reset_index(drop=True)
    hh = arr.household.unique()
    X = arr[cols].values
    mu, sd = X.mean(0), X.std(0) + 1e-9
    c = 0

    for i in range(len(arr)):  # leave-one-day-out
        true = arr.household[i]
        prof = {}
        for h in hh:
            m = (arr.household.values == h).copy()
            m[i] = False
            if m.any():
                prof[h] = ((X[m] - mu) / sd).mean(0)  # profile from that home's OTHER days
        q = (X[i] - mu) / sd
        c += (min(prof, key=lambda h: np.linalg.norm(q - prof[h])) == true)

    return c / len(arr), 1 / len(hh)


def prs(u, Hn, k, reid):
    """Listing 7: composite Privacy Risk Score (0-1 scale), weighting
    single-day re-identification and uniqueness most heavily."""
    k_term = 1 - min(k, 10) / 10  # small k -> higher risk
    return float(np.clip(0.40 * reid + 0.30 * u + 0.20 * k_term + 0.10 * Hn, 0, 1))


if __name__ == "__main__":
    # --- run ---
    synd = extract("synd_mains_1min.csv", "SynD")
    real = pd.concat(
        [extract(f"snm_{b}_mains_1min.csv", b) for b in ["b10", "b11", "b15", "b17"]],
        ignore_index=True,
    )

    su, sH, sk = uniqueness_entropy_k(synd, household_level=False)
    ru, rH, rk = uniqueness_entropy_k(real, household_level=True)
    rreid, _ = single_day_reid(real)

    print("SynD PRS:", prs(su, sH, sk, 0.0))
    print("Real PRS:", prs(ru, rH, rk, rreid), " single-day re-id:", rreid)
