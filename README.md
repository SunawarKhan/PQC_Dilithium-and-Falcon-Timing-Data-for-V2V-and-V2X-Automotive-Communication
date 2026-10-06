# Descriptive Secondary Analysis of Kyber, Dilithium and Falcon Timing Data for V2V and V2X Automotive Communication

Reproducible companion code for the manuscript of the same name. The notebook performs a **descriptive secondary analysis** of reported timing measurements for the NIST post-quantum primitives **ML-KEM (Kyber)**, **ML-DSA (Dilithium)** and **Falcon** under two automotive communication scenarios — **V2V (rural)** and **V2X (urban)** — and regenerates every figure, table and headline number used in the paper.

**Authors / maintainers:** Sunawar Khan and Habib Hamam

---

## Scope and non-claims

This repository analyzes **reported timing values** from a public dataset. Read the following before citing any result:

- It is a **secondary descriptive analysis**, not an automotive testbed study. It does **not** validate a real-time deadline, a hardware platform, sustained throughput, or FIPS compliance of the underlying implementations.
- The source dataset describes an OMNeT++/Veins simulation, but the **host hardware, library versions, instrumentation, and the distinction between simulated time and host elapsed time are unverified**. The notebook marks these explicitly as `NOT_VERIFIED` in its validation report.
- Aggregate "primitive-operation cost" figures are a **bookkeeping sum of per-operation means**, not a measured end-to-end handshake.
- Several cells have **small sample sizes (n = 3 to 81)**; percentile, tail and jitter estimates from small cells are indicative only. The notebook reports exact one-sided upper confidence bounds for zero-failure cells to make this explicit.

The design goal is that **the paper and the code cannot silently diverge**: headline claims are computed from the data and asserted at runtime.

---

## Data source

Gonçalves and Reis Quietinho Leithardt (2026), *Mendeley Data*, V1.
DOI: [10.17632/czx6vk5hsr.1](https://data.mendeley.com/datasets/czx6vk5hsr/1)

The dataset landing page describes an OMNeT++ simulation using Veins-Inet and Veins. No original raw files are bundled with this repository or claimed to have been re-executed. The analysis runs against a tidy CSV derived from the reported values, with integrity checks described below.

---

## Repository contents

| Path | Description |
|------|-------------|
| `PQC_Automotive_Analysis_revised.ipynb` | Source notebook (code only) — run this. |
| `PQC_Automotive_Analysis_executed.ipynb` | A fully executed copy with outputs, for reference. |
| `pqc_tidy_timings.csv` | Default tidy input: 1,376 measurements in long format. |
| `input_manifest.json` | Declares the tidy file and its expected SHA-256 checksum. |
| `raw_manifest.json` | *(Optional)* Schema for reconstructing the tidy table from raw files. |
| `requirements.txt` | Pinned Python dependencies. |
| `analysis_outputs/` | Generated on run (see **Outputs**). |

### Input schema (`pqc_tidy_timings.csv`)

One measurement per row, columns:

| Column | Values |
|--------|--------|
| `scenario` | `V2V`, `V2X` |
| `algorithm` | `Kyber`, `Dilithium`, `Falcon` |
| `operation` | Kyber: `KeyGen`, `Encapsulation`, `Decapsulation` · Dilithium/Falcon: `KeyGen`, `Signing`, `Verification` |
| `variant` | Kyber-512/768/1024 · Dilithium-44/65/87 · Falcon-512/1024 |
| `time_us` | Finite, positive microseconds |

---

## Requirements

- Python **3.12**
- `numpy`, `pandas`, `matplotlib` (pinned in `requirements.txt`)

The executed reference copy was produced with Python 3.12.14, NumPy 2.5.3, pandas 2.2.3, matplotlib 3.11.2. The notebook records the exact versions of each run in `analysis_outputs/environment.json`.

---

## Quick start

Run from the repository directory in a fresh environment:

```sh
python -m venv .venv
# Activate .venv with the command appropriate to your operating system.
python -m pip install -r requirements.txt

python -m jupyter nbconvert --to notebook --execute \
  PQC_Automotive_Analysis_revised.ipynb \
  --output PQC_Automotive_Analysis_executed.ipynb \
  --ExecutePreprocessor.timeout=180
```

The default input is `pqc_tidy_timings.csv`; all artifacts are written under `analysis_outputs/`. A clean `nbconvert` execution is distinct from clicking through cells manually — the validation record states which was performed.

---

## Input modes

The notebook supports two modes, set by `INPUT_MODE` in the setup cell.

**`tidy` (default).** Loads the bundled tidy CSV and verifies its SHA-256 against `input_manifest.json` before parsing.

**`raw`.** Reconstructs the tidy table from raw files listed in `raw_manifest.json` (`schema_version: 1`). Each entry must declare the file path, its SHA-256, scenario, algorithm, operation, and an explicit column-to-variant mapping. No directory-name inference is used. Summary rows (`average`, `mean`, `total`, `std`) are rejected unless excluded by physical line number with a stated reason, and malformed or non-finite/non-positive values fail loudly. On success, the reconstructed record multiset is asserted **exactly equal** to the tidy CSV.

Duplicate timing values are retained in both modes. `source_row` refers to the supplied tidy CSV only; original source-record identifiers cannot be reconstructed.

---

## Outputs (`analysis_outputs/`)

- `figure_01.*` – `figure_15.*` — 15 figures, each exported as **PNG and PDF**.
- `input_with_lineage.csv` — the parsed corpus with per-row lineage columns.
- `environment.json` — exact interpreter and library versions for the run.
- `verification_service_rates.csv` — idealised verification service rates (1 / mean).
- `validation_report.json` — pass/fail record for every integrity gate.
- `raw_exclusions.json` — written in `raw` mode only, logging excluded summary rows.

---

## Validation and reproducibility

The run passes only if every gate below holds, recorded in `validation_report.json`:

- **Input identity** — tidy CSV matches the manifest checksum (and, in `raw` mode, the raw reconstruction matches exactly).
- **Labels** — required columns present; scenarios, algorithms, operations and variants consistent; timings finite and positive.
- **Corpus composition** — counts asserted (V2V = 300, V2X = 1,076, total = 1,376).
- **Cell counts** — all 48 (scenario × algorithm × operation × variant) cells present with expected per-cell `n`.
- **Reference means** — 48 retained summary constants reproduced within an absolute tolerance of 5 × 10⁻⁶ µs (zero relative tolerance). This is a numerical consistency check, not a provenance certificate; the underlying source PDFs were not independently verified.
- **Headline assertions** — every quantitative claim used in the paper is recomputed and asserted.
- **Figure exports** — exactly 15 figures in both formats.

---

## Key findings (computed and asserted)

These are reproduced from the data at runtime, not hard-coded:

- **Verification median** spans **53.0 – 306.5 µs** across all schemes and scenarios.
- **Falcon-512 key generation** is about **131×** the cost of Dilithium-44 key generation (V2V medians: ~14,450 vs 110 µs). Key generation is typically amortised rather than paid per message.
- **Dilithium signing medians rise from V2V to V2X** (e.g. Dilithium-44: 313 → 670 µs; Dilithium-87: 507 → 1,377 µs), while verification medians are comparatively scenario-stable.
- **Tails do not rise uniformly** with scenario: Falcon-512 signing p99 is lower in V2X than V2V (small n = 3/6 — treat as indicative).
- **Urban Dilithium-87 idealised verification rate** (1 / mean) ≈ **2,895 verifications/s**, below an illustrative 300-neighbour × 10 Hz = 3,000 arrivals/s load — before any queueing, certificate checks, or application work. A sustained-load study is required for any capacity claim.
- **Highest-jitter cell:** V2X Falcon-512 verification, CV ≈ 1.14.

---

## How to cite

If you use this code or analysis, please cite the manuscript:

> Khan, S., and Hamam, H. *Descriptive Secondary Analysis of Kyber, Dilithium and Falcon Timing Data for V2V and V2X Automotive Communication.*

and the underlying dataset (Gonçalves and Reis Quietinho Leithardt, 2026, Mendeley Data V1, DOI 10.17632/czx6vk5hsr.1).

---

## License

No license is set yet. Add one (e.g. a code license such as MIT or Apache-2.0 for the notebook, and attribution consistent with the Mendeley dataset's own license for the data) before publishing the repository.

## Contact

Sunawar Khan and Habib Hamam.
