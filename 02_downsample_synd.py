"""
Listing 2: Chunked downsampling of the SynD mains signal to
one-minute resolution.

SynD's raw mains file (1.csv) is a ~78-million-row, ~3 GB, tab-separated
CSV with no header. It is too large to load into memory at once, so it
is read and resampled in chunks.

Input:  1.csv               (raw SynD mains export)
Output: synd_mains_1min.csv (one-minute average power, W)
"""

import pandas as pd

# SynD mains: tab-separated, no header -> 1-minute averages
parts = []

for chunk in pd.read_csv(
    "1.csv",
    sep="\t",
    header=None,
    names=["time", "power_w"],
    chunksize=2_000_000,
):
    chunk["time"] = pd.to_datetime(chunk["time"], errors="coerce")
    chunk = chunk.dropna(subset=["time"]).set_index("time")
    parts.append(chunk["power_w"].resample("1min").mean())

s = pd.concat(parts).groupby(level=0).mean()
s.to_csv("synd_mains_1min.csv", header=["power_w"])
