# Ethical Aspects of Synthetic Data in Smart Meter Datasets

Smart Grid Research Project (700.288), University of Klagenfurt
Supervisor: Prof. Wilfried Elmenreich · Co-supervisor: Fabian Schober
Author: Ikechukwu (igwe) Ucho

## Research Question

Does synthetic smart meter data carry lower privacy risk than real smart meter data,
and can that difference be quantified using feature-based re-identification metrics
and a composite Privacy Risk Score (PRS)?

## Datasets

Two datasets are compared. **Raw data files are not included in this repository** —
see [Reproducing the Results](#reproducing-the-results) below for download instructions.

| | SynD | SmartNIALMeter (SNM) |
|---|---|---|
| Type | Synthetic | Real |
| Scope | 1 simulated Austrian household | Multiple real Swiss households |
| Format | CSV archive | HDF5 (`.h5`), per-phase V/I/PF |

## Method

1. **Load & preprocess** each dataset independently. SNM does not store direct power
   readings — whole-home power is derived per phase as `P = V · I · cos(φ)` and summed
   across phases, with spike clipping applied to remove sensor artifacts.
2. **Extract features** from each dataset's load profile (e.g. daily/weekly consumption
   patterns, peak timing, statistical descriptors) suitable for a single-day
   re-identification attack.
3. **Re-identification attack**: attempt to match a single day of consumption back to
   its household/source using the extracted features, run separately on SynD and SNM.
4. **Composite Privacy Risk Score (PRS)**: combine re-identification accuracy with
   supporting privacy-relevant metrics into one score per dataset, so the two datasets
   can be compared on the same scale.
5. **Qualitative bias review**: check whether patterns/biases present in the real data
   are reproduced (or "laundered") in the synthetic data.

Note: metrics are computed independently per dataset rather than jointly (e.g. no
cross-dataset NNDR), since SynD and SNM are not structurally comparable at the
record level.

## Results

| Metric | SNM (real) | SynD (synthetic) |
|---|---|---|
| Single-day re-identification accuracy | ~77% | ~0% |
| Composite Privacy Risk Score (PRS) | ~0.889 | ~0.291 |

Real smart meter data carries substantially higher re-identification risk than the
synthetic data evaluated here. Full methodology, figures, and discussion are in
[`report/Final_Report_Ucho_Ikechukwu_Igwe_12349300.pdf`](./report/).

## Repository Structure

```
├── report/           Final report (.pdf)
├── code/             Analysis scripts (7 stages: load → preprocess → feature
│                     extraction → re-identification → PRS → bias review → figures)
├── docs/             Supporting/additional documents
├── README.md
└── LICENSE
```

> Adjust the folder/file names above to match what you actually upload.

## Reproducing the Results

### 1. Download the datasets (not included in this repo)

**SynD** (synthetic, single Austrian household):
- Source: https://github.com/klemenjak/SynD
- Cite as: Klemenjak, C., Kovatsch, C., Herold, M. & Elmenreich, W. (2020). *A synthetic
  energy dataset for non-intrusive load monitoring in households.* Scientific Data, 7,
  108. https://doi.org/10.1038/s41597-020-0434-6

**SmartNIALMeter (SNM)** (real, multiple Swiss households):
- Source: https://zenodo.org/records/10875988 (download `preprocessed.7z` or `raw.7z`,
  extract with 7-Zip)
- Instructions: https://github.com/ihomelab/snm-dataset
- Cite as: Vogel, M., Friedli, M., Camenzind, M., Kniesel, G., Klemenjak, C., Gugolz, G.,
  Huber, P., Calatroni, A., Kaufmann, L., Rumsch, A., Paice, A. (2024). *The
  'SmartNIALMeter' electrical appliance disaggregation dataset.* Data in Brief.
  https://doi.org/10.5281/zenodo.10875988

### 2. Set up the environment

```bash
pip install pandas numpy h5py matplotlib scikit-learn
```

(Adjust to the exact packages your scripts import.)

### 3. Point the scripts at your local data

Place the downloaded/extracted files in a local `data/` folder (already `.gitignore`d)
and update the file paths at the top of the loading scripts to match.

### 4. Run the pipeline

Run the scripts in `code/` in order (load → preprocess → feature extraction →
re-identification attack → PRS computation → bias review → figures). See in-code
comments for details on each stage.

## License

See [LICENSE](./LICENSE).
