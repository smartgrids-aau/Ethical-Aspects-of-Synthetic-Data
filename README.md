# Ethical Aspects of Synthetic Data in Smart Meter Datasets

Smart Grid Research Project (700.288), University of Klagenfurt
Supervisor: Prof. Wilfried Elmenreich · Co-supervisor: Fabian Schober
Author: Ikechukwu (Igwe) Ucho

## Research Question

Does synthetic smart meter data carry lower privacy risk than real smart meter data,
and can that difference be quantified using feature-based re-identification metrics
and a composite Privacy Risk Score (PRS)?

## Datasets

Two datasets are compared. **Raw data files are not included in this repository**
(see [Reproducing the Results](#reproducing-the-results) for how to obtain them).

| | SynD | SmartNIALMeter (SNM) |
|---|---|---|
| Type | Synthetic | Real |
| Scope | 1 simulated Austrian household | 4 real Swiss households (b10, b11, b15, b17) |
| Raw format | Tab-separated mains CSV | HDF5 (`.h5`), per-phase voltage/current/power factor |

## Method

1. **Extract & downsample** (`code/01_extract_snm_archive.bat`, `code/02_downsample_synd.py`,
   `code/03_compute_snm_power.py`). SNM does not store direct power readings — whole-home
   power is derived per phase as `P = V · I · cos(φ)` and summed across phases, with
   spike clipping applied. Both datasets are downsampled to one-minute resolution.
2. **Feature extraction** (`code/04_privacy_analysis.py`, `day_features`): each day of
   one-minute mains power is reduced to 8 behavioural features (`total_kwh`, `peak_w`,
   `mean_w`, `load_factor`, `morning_rise_h`, `evening_peak_h`, `night_day_ratio`,
   `n_peaks`).
3. **Privacy metrics** (same file, `uniqueness_entropy_k`): quasi-identifier uniqueness,
   normalized entropy, and k-anonymity, computed across the 4 real households (each
   reduced to its mean feature profile) and, separately, across SynD's 180 days.
4. **Single-day re-identification** (`single_day_reid`): leave-one-day-out test — hold
   out one day, build each household's profile from its remaining days, and check
   whether the held-out day's nearest profile (in standardised feature space) is its
   own household. Score is top-1 accuracy; random chance is 1/(number of homes).
5. **Composite Privacy Risk Score** (`prs`): combines re-identification accuracy,
   uniqueness, k-anonymity, and entropy into one 0–1 score per dataset, weighting
   re-identification and uniqueness most heavily.

Metrics are computed independently per dataset (not jointly, e.g. no cross-dataset
NNDR), since SynD and SNM are not structurally comparable at the record level.

## Results

| Metric | SNM (real) | SynD (synthetic) |
|---|---|---|
| Single-day re-identification accuracy | ~77% (chance: 25%) | 0% (single household) |
| Composite Privacy Risk Score (PRS) | ~0.889 | ~0.291 |

Real smart meter data carries substantially higher re-identification risk than the
synthetic data evaluated here. Full methodology, figures, and discussion are in
[https://github.com/smartgrids-aau/Ethical-Aspects-of-Synthetic-Data/blob/651438cef594f5e7eccdffc52b3e1d8f33178bc7/Final_Report_Ucho_Ikechukwu_Igwe_12349300.pdf](./report/).

## Repository Structure

```
├── report/
│   └── Final_Report_Ucho_Ikechukwu_Igwe_12349300.pdf   Final report
├── code/
│   ├── 01_extract_snm_archive.bat    7-Zip commands: selective extraction of SNM mains files
│   ├── 02_downsample_synd.py         Chunked downsampling of SynD mains to 1-min resolution
│   ├── 03_compute_snm_power.py       Whole-home power from per-phase V/I/PF (per SNM building)
│   └── 04_privacy_analysis.py        Feature extraction, privacy metrics, PRS (main analysis)
├── data_sample/
│   ├── synd_day_features.csv         Extracted per-day features for SynD (output of step 2-4)
│   ├── snm_all_features.csv          Extracted per-day features for all 4 SNM homes
│   └── snm_home_summary.csv          Per-household summary statistics (Table in report Sec. 4.1)
├── README.md
└── LICENSE
```

`data_sample/` contains the small, already-extracted per-day *feature* tables (outputs
of the pipeline), **not** the raw smart meter datasets, so that `04_privacy_analysis.py`
can be run and checked end-to-end without first downloading and reprocessing the full
raw archives.

## Reproducing the Results

### Option A — run the main analysis directly on the included feature tables

```bash
pip install pandas numpy
```

Open `code/04_privacy_analysis.py` and, instead of calling `extract(...)` on raw mains
CSVs, load the feature tables already provided in `data_sample/` directly (they have
the same column layout the pipeline produces). This lets you check the privacy metrics
and PRS computation immediately, without downloading the raw datasets.

### Option B — full reproduction from raw data if you have good memory storage.

**1. Download the datasets**

- **SynD** (synthetic, single Austrian household)
  Source: https://github.com/klemenjak/SynD
  Cite as: Klemenjak, C., Kovatsch, C., Herold, M. & Elmenreich, W. (2020). *A synthetic
  energy dataset for non-intrusive load monitoring in households.* Scientific Data, 7,
  108. https://doi.org/10.1038/s41597-020-0434-6

- **SmartNIALMeter (SNM)** (real, multiple Swiss households)
  Source: https://zenodo.org/records/10875988 — download the raw archive (`raw.7z`) and
  extract with 7-Zip
  Cite as: Vogel, M., Friedli, M., Camenzind, M., Kniesel, G., Klemenjak, C., Gugolz, G.,
  Huber, P., Calatroni, A., Kaufmann, L., Rumsch, A., Paice, A. (2024). *The
  'SmartNIALMeter' electrical appliance disaggregation dataset.* Data in Brief.
  https://doi.org/10.5281/zenodo.10875988

**2. Set up the environment**

```bash
pip install pandas numpy
```

**3. Run the pipeline in order**

```bash
# a) Extract only the mains (site-meter) .h5 files needed from the SNM archive
code/01_extract_snm_archive.bat

# b) Downsample SynD's raw mains export (1.csv) to 1-minute resolution
python code/02_downsample_synd.py
# -> produces synd_mains_1min.csv

# c) Compute whole-home power for each SNM building (run once per building,
#    editing the input/output filenames inside the script for b10, b11, b15, b17)
python code/03_compute_snm_power.py
# -> produces snm_bXX_mains_1min.csv per building

# d) Run the full privacy analysis: feature extraction, uniqueness/entropy/
#    k-anonymity, single-day re-identification, and PRS
python code/04_privacy_analysis.py
```

Step (d) expects `synd_mains_1min.csv` and `snm_b10_mains_1min.csv` /
`snm_b11_mains_1min.csv` / `snm_b15_mains_1min.csv` / `snm_b17_mains_1min.csv` in the
working directory, and prints the same PRS and re-identification numbers reported
above and in Section 4 of the report.

All processing was done using Python 3.12 on Windows 10.

## License

See [LICENSE](./LICENSE).
