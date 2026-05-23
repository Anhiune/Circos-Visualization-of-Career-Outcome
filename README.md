# Career Outcome Visualization — Reproducible Package

This package lets you open the three published dashboards immediately, and also gives you everything needed to regenerate them from scratch if you receive new data next year.

**If you just want to view the dashboards right now, skip to [Quick Start](#quick-start).**

---

## What This Package Is

Three interactive Circos chord-diagram dashboards showing how Gonzaga University graduates moved from their incoming major to their career outcome (Class of 2026, approximately 925–2,682 students depending on the dashboard):

| Dashboard | File | What it shows |
|-----------|------|---------------|
| Career Outcomes | `site/index.html` | Incoming major → career cluster (2,682 graduates) |
| Industry Mobility | `site/incoming_grad_grouped.html` | Incoming major group → graduating major group (925 students) |
| College Mobility | `site/incoming_grad_grouped_college.html` | Incoming college → graduating college (same 925 students, by college) |

Each dashboard is a **static HTML file** — it loads pre-rendered SVG images. Nothing needs to be running in the background. Open the file, click the thumbnails on the left to filter the diagram.

---

## Quick Start

### To View the Dashboards (No Installation Required)

1. Download or clone this repository.
2. Open `site/index.html` in any modern browser (Chrome, Firefox, Edge, Safari).
3. Open the other two dashboards the same way.

> **Important:** Open the file directly — do not double-click from Windows Explorer if it opens in a restricted mode. Right-click → "Open with" → your browser, or drag the file into the browser window.

---

## To Regenerate the Dashboards From New Data

This is a multi-step process. Read these documents **in order** before running anything:

1. **`CIRCOS_SETUP.md`** — Install Circos (a Perl-based diagram renderer). Required before any pipeline step that renders SVGs.
2. **`PIPELINE_OVERVIEW.md`** — Understand what each script does and why, and see the full data flow diagram.
3. **`DATA_CLEANING_DECISIONS.md`** — Understand every data filtering and clustering decision so you can make informed choices when new data arrives.
4. **`VISUALIZATION_RULES.md`** — Color palette, layout ordering, label rules, and SVG post-processing decisions.

### Step-by-Step Instructions

#### Prerequisites

- Python 3.10 or newer
- Circos installed (see `CIRCOS_SETUP.md`)
- The `CIRCOS_ROOT` environment variable set to your Circos install folder (e.g., `C:/Users/yourname/circos`)

#### Install Python dependencies

```bash
pip install -r requirements.txt
```

#### Prepare your input data

| File location | Description | Required for |
|---------------|-------------|--------------|
| `career_survey_data.xlsx` (package root) | Annual career survey Excel export — must have `Program Name/Major` and `Job Title` columns | Career dashboard (`index.html`) |
| `site/incomingmajor_fall2022_csv/Class_of_2026_CPF_vs_SP26.csv` | Enrollment transition data — must have columns for incoming and graduating major | Both mobility dashboards |
| `site/incomingmajor_fall2022_csv/major.csv` | Major-to-group mapping — must have `Major`, `Group`, `School` columns | Both mobility dashboards |
| `inputs/Major_Job_Cluster_Lookup_Rebuilt_Full_baseline.csv` | Baseline major cluster reference | Career dashboard Step 2 |
| `inputs/job_title_categorized.csv` | Manually reviewed job-title overrides | Career dashboard Step 3 |

> See `DATA_CLEANING_DECISIONS.md` for the column format requirements and what each file means.

#### Run the full pipeline

```bash
python run_pipeline.py
```

This runs all 10 steps in order. If you only need to regenerate one dashboard, see the individual step instructions in `PIPELINE_OVERVIEW.md`.

---

## Package Contents

```
reproducible_package/
├── README.md                                   ← This file
├── PIPELINE_OVERVIEW.md                        ← Full pipeline with data flow diagram
├── DATA_CLEANING_DECISIONS.md                  ← Every data decision documented
├── VISUALIZATION_RULES.md                      ← Color, layout, and SVG rules
├── CIRCOS_SETUP.md                             ← How to install Circos
├── requirements.txt                            ← Python package list
├── run_pipeline.py                             ← Master runner (runs all 10 steps)
├── career_survey_data.xlsx                     ← Raw career survey (input for Step 1)
│
├── inputs/                                     ← Baseline reference CSVs
│   ├── Major_Job_Cluster_Lookup_Filtered_baseline.csv
│   ├── Major_Job_Cluster_Lookup_Rebuilt_Full_baseline.csv
│   └── job_title_categorized.csv               ← Manual job-title overrides (~87 entries)
│
├── outputs/                                    ← Created by the pipeline (empty at start)
│   ├── lookup/                                 ← Intermediate + final lookup CSVs
│   │   └── Major_Job_Cluster_Lookup_v2_filtered_career_merged.csv  ← pre-built final lookup
│   ├── renders/                                ← Circos config files + raw SVGs
│   └── reports/                                ← Cluster count reports and notes
│
├── scripts/                                    ← 10 numbered production scripts
│   ├── 01_rebuild_cluster_lookup.py            ← Excel → raw lookup table
│   ├── 02_remap_major_clusters.py              ← Consolidate major cluster names
│   ├── 03_remap_career_clusters.py             ← Consolidate career cluster names
│   ├── 04_generate_circos_data_career.py       ← Build Circos config for career dashboard
│   ├── 05_taper_ribbon_svg.py                  ← Post-process SVG (tapered ribbons + fonts)
│   ├── 06_generate_career_focus_svgs.py        ← Extract per-major/career focus SVGs
│   ├── 07_generate_circos_data_industry.py     ← Build Circos config for industry mobility
│   ├── 08_generate_industry_focus_svgs.py      ← Extract per-group focus SVGs
│   ├── 09_generate_circos_data_college.py      ← Build Circos config for college mobility
│   └── 10_generate_college_focus_svgs.py       ← Extract per-college focus SVGs
│
└── site/                                       ← The finished dashboards (open in browser)
    ├── index.html
    ├── incoming_grad_grouped.html
    ├── incoming_grad_grouped_college.html
    ├── dashboard_docs.css
    ├── dashboard_docs.js
    ├── dashboard_docs_data.js
    ├── v3_ordered_images/                      ← 22 SVGs for index.html
    ├── incoming_grad_grouped_dashboard_images/ ← 27 SVGs for industry dashboard
    ├── incoming_grad_grouped_college_dashboard_images/ ← 38 SVGs for college dashboard
    └── incomingmajor_fall2022_csv/             ← Mobility source data (input for Steps 7+9)
        ├── Class_of_2026_CPF_vs_SP26.csv
        └── major.csv
```

---

## Background: How This Was Built

This project was developed over 4 months (January–May 2026) by a graduate student working with Gonzaga University's career services data. The process involved:

- Multiple rounds of cluster naming consolidation (documented in `DATA_CLEANING_DECISIONS.md`)
- Extensive layout experimentation to find an ordering that minimizes ribbon crossings (7 layout experiments: v1–v7)
- SVG post-processing to achieve tapered ribbon aesthetics that Circos does not natively support
- Manual review and override of ~87 ambiguous job titles
- Color palette iteration to achieve colorblind-friendly contrast

Only the final production pipeline is included here. The experimental files, prototype dashboards, and intermediate renders are in the original `circos_refresh_v2/` workspace and are not needed to reproduce the final product.

---

## Who to Contact

If you are picking this up as a new student and something is unclear, start with `PIPELINE_OVERVIEW.md`. If a script fails, the most common cause is either a missing Circos install or a column name mismatch in your input data — `DATA_CLEANING_DECISIONS.md` documents the expected column names in full.
