"""
Listing 3: Computing whole-home power for an SNM building from
per-phase voltage/current/power-factor, and resampling to one minute.

The SNM raw site-meter file does not store power directly; it stores
RMS voltage, RMS current, and power factor for each of the three phases
(L1, L2, L3). Real power is computed per the dataset paper's own
definition, P = V * I * cos(phi), summed across phases.

Input:  cii-adapter.h5           (raw SNM per-building mains export)
Output: snm_bXX_mains_1min.csv   (one-minute average power, W)

Run once per building (b10, b11, b15, b17), adjusting the input/output
filenames accordingly.
"""

import pandas as pd

df = pd.read_hdf("cii-adapter.h5", "data")  # columns: Voltage/Current/Power Factor L1..L3
df.index = pd.to_datetime(df.index)

P = 0.0
for ph in ["L1", "L2", "L3"]:  # real power = V * I * cos(phi), summed over phases
    P = P + df["Voltage " + ph] * df["Current " + ph] * df["Power Factor " + ph]

P = P.clip(lower=0, upper=P.quantile(0.999))  # drop negatives and rare measurement spikes

out = P.resample("1min").mean().dropna()
out.to_csv("snm_bXX_mains_1min.csv", header=["power_w"])
