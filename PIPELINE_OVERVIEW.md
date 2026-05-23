# Pipeline Overview

This document explains what every script in the pipeline does, what goes in, what comes out, and why each step exists. Read this before running anything.

---

## Big Picture: How the Dashboards Are Made

The dashboards are **static HTML files** that display pre-rendered SVG images. No live database. No server. The SVGs are generated once by the Python + Circos pipeline and then committed alongside the HTML files.

This means:

- Viewing the dashboard requires no Python or Circos — just a browser.
- Regenerating the dashboard (when new data arrives) requires running the full pipeline.
- Changing a cluster name or color requires a full re-render.

---

## Full Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RAW INPUT FILES                              │
│                                                                     │
│  career_survey_data.xlsx          Class_of_2026_CPF_vs_SP26.csv    │
│  (Program Name/Major, Job Title)  (student ID, incoming, graduating │
│                                    major)                           │
│  major.csv                        inputs/job_title_categorized.csv  │
│  (major → group → school)         (manual job-title overrides)      │
│                                                                     │
│  inputs/Major_Job_Cluster_Lookup_Rebuilt_Full_baseline.csv          │
│  (baseline major cluster reference from external analysis)          │
└─────────────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐         ┌────────────────────────────────────────┐
│   CAREER TRACK  │         │           MOBILITY TRACK               │
│   (3 steps)     │         │           (no clustering needed)       │
└─────────────────┘         └────────────────────────────────────────┘
         │                                        │
   Step 01                               Steps 07 + 09
   rebuild_cluster_lookup.py             (read CSV directly, no lookup)
   (Excel → raw row-level lookup)
         │
   Step 02
   remap_major_clusters.py
   (consolidate 24 raw clusters → 13 display clusters)
         │
   Step 03
   remap_career_clusters.py
   (consolidate 14 raw career clusters → 8 display clusters)
         │
         ▼
   data/processed/
   Major_Job_Cluster_Lookup_v2_filtered_career_merged.csv
   (2,682 classified rows — one per graduate with both major + career assigned)
         │
         ▼                                        │
   Step 04                               Steps 07 + 09
   generate_circos_data_career.py        generate_circos_data_industry.py
   (lookup → circos config files)        generate_circos_data_college.py
         │                                        │
         ▼                                        ▼
   outputs/renders/                   outputs/renders/
   order_experiment_v3/overall/       incoming_grad_grouped_latest/
   (circos.conf, links.txt,           incoming_grad_grouped_college_latest/
    karyotype.txt, colors.conf)       (same structure)
         │                                        │
         ▼                                        ▼
   Circos CLI                         Circos CLI
   (renders SVG from config)          (renders SVG from config)
         │                                        │
         ▼                                        ▼
   major_job_circos_v3.svg            main.svg (overall diagram)
         │                                        │
   Step 05                                        │
   taper_ribbon_svg.py                            │
   (reshape ribbon curves +                       │
    apply custom fonts + labels)                  │
         │                                        │
         ▼                                        ▼
   major_job_circos_v3_svg_taper.svg  Steps 08 + 10
                │                    generate_industry_focus_svgs.py
         Step 06                     generate_college_focus_svgs.py
   generate_career_focus_svgs.py     (extract one SVG per group)
   (extract one SVG per major               │
    and one per career)                      ▼
         │                           site/incoming_grad_grouped_dashboard_images/
         ▼                           site/incoming_grad_grouped_college_dashboard_images/
   site/v3_ordered_images/
   ├── main.svg
   ├── majors/accounting_finance.svg
   ├── majors/computer_science_it.svg
   │   ... (13 major SVGs)
   └── careers/software_data.svg
       ... (8 career SVGs)
         │                                        │
         └──────────────────┬─────────────────────┘
                            ▼
              site/index.html  (loads v3_ordered_images/)
              site/incoming_grad_grouped.html  (loads incoming_grad_grouped_*)
              site/incoming_grad_grouped_college.html  (loads *_college_*)
              + shared: dashboard_docs.css, dashboard_docs.js, dashboard_docs_data.js
```

---

## Step-by-Step Script Reference

### Step 01 — `01_rebuild_cluster_lookup.py`

**Input:**
- `data/raw/career_survey_data.xlsx` — raw career survey (columns: `Program Name/Major`, `Job Title`)
- External cluster reference CSVs (see script for current paths; these came from an earlier analysis project)

**Output:**
- `outputs/lookup/Major_Job_Cluster_Lookup_rebuilt.csv` — every row classified (full, including unclassified)
- `outputs/lookup/Major_Job_Cluster_Lookup_rebuilt_filtered.csv` — rows where both major AND career were classified

**What it does:**

1. Loads each row from the Excel file.
2. Looks up the major in the cluster reference table. If no exact match, tries aliases (e.g., `Data Science` → `Computer Science & IT`). If still no match, uses a hardcoded override table.
3. Looks up the job title in the career reference table. First tries exact match, then normalized (lowercased, stripped of punctuation), then applies keyword-based heuristic rules (e.g., anything containing "attorney" → `Legal & Policy`).
4. Rows where the job title is blank are kept in the full output but excluded from filtered output (you cannot infer a career from no information).

**Why this step exists:**

The original lookup table from the external analysis project covered only a fraction of actual job titles in the survey. Rather than manually classifying thousands of titles, this script uses heuristics to automate the 80% case while keeping the decision logic explicit and auditable.

---

### Step 02 — `02_remap_major_clusters.py`

**Input:**
- `inputs/Major_Job_Cluster_Lookup_Rebuilt_Full_baseline.csv`

**Output:**
- `outputs/lookup/Major_Job_Cluster_Lookup_v2_full.csv`
- `outputs/lookup/Major_Job_Cluster_Lookup_v2_filtered.csv`
- `outputs/reports/major_remap_v2_notes.md` (auto-generated rationale)

**What it does:**

Consolidates 24 granular major clusters down to 13 display-level clusters grouped under 4 large academic families. For example:

- `Biological Sciences` + `Health & Wellness` → `Biological & Health Sciences`
- `Physical Sciences` + `Environmental Sciences` → `Physical & Environmental Sciences`
- `Teacher Education` + `Social Work` + `Special Education & Counseling` + `Educational Leadership` → `Education & Social Services`

**Why this step exists:**

The raw rebuild produced too many small clusters to display cleanly on a Circos diagram. The consolidation was specifically designed to:

1. Keep clusters large enough to be visible on the chord diagram.
2. Group academically related fields that a general audience would expect to be together.
3. Separate `Economics` as its own cluster (it belongs in Social Sciences but has enough graduates to merit its own arc).

**The 4 large academic families and their colors:**

| Family | Display name | Color |
|--------|-------------|-------|
| Blue | `BUSINESS & MANAGEMENT` | `#2F6DB3` |
| Green | `ENGINEERING, SCIENCE & TECHNOLOGY` | `#2E8B57` |
| Orange | `SOCIAL SCIENCES & EDUCATION` | `#E68613` |
| Purple | `HUMANITIES & COMMUNICATION` | `#B279A2` |

---

### Step 03 — `03_remap_career_clusters.py`

**Input:**
- `outputs/lookup/Major_Job_Cluster_Lookup_v2_full.csv`
- `inputs/job_title_categorized.csv` (manual overrides for ~87 ambiguous titles)

**Output:**
- `outputs/lookup/Major_Job_Cluster_Lookup_v2_full_career_merged.csv`
- `outputs/lookup/Major_Job_Cluster_Lookup_v2_filtered_career_merged.csv` ← **this is the final production lookup**
- `outputs/reports/career_remap_v2_notes.md`

**What it does:**

Reduces 14 raw career clusters to 8 display clusters. For example:

- `Accounting & Audit` + `Finance & Investment` → `Finance & Accounting`
- `IT & Infrastructure` + `Software & Data` → `Software & Data` (kept as technical, infrastructure folded in)
- `Clinical Care` + `Research & Science` → `Health & Science Research`
- `Education` + `Social Service` → `Education & Social Service`

Also applies manual overrides from `job_title_categorized.csv` for titles like `"server"`, `"associate"`, `"analyst"` that the heuristics could not reliably place.

**Why this step exists:**

Same reason as Step 02 — 14 career arcs would create a cluttered diagram. The merges were approved after reviewing arc sizes: merged groups all had meaningful representation, and the merged names still communicate clearly to a general audience.

---

### Step 04 — `04_generate_circos_data_career.py`

**Input:**
- `outputs/lookup/Major_Job_Cluster_Lookup_v2_filtered_career_merged.csv`

**Output:**
- `outputs/renders/order_experiment_v3/overall/circos.conf`
- `outputs/renders/order_experiment_v3/overall/links.txt`
- `outputs/renders/order_experiment_v3/overall/karyotype.txt`
- `outputs/renders/order_experiment_v3/overall/colors.conf`
- `outputs/renders/order_experiment_v3/overall/layout_order_v3.csv`
- `outputs/renders/order_experiment_v3/overall/summary.csv`

**What it does:**

Converts the lookup CSV into Circos input format:

- `karyotype.txt` — defines each arc segment (major or career cluster) with its size and color
- `links.txt` — defines each ribbon connecting a major arc to a career arc
- `circos.conf` — the master Circos configuration that references the above files and sets spacing, font sizes, label positions, etc.
- `colors.conf` — hexadecimal color definitions referenced by the config

**Ordering logic:** Majors are arranged in a specific visual order (engineering on top, then business, then humanities, then social sciences) to minimize ribbon crossings between adjacent related clusters. Career arcs appear on the opposite half of the circle in a mirrored order to reduce visual clutter.

**Why this step exists (and not a different tool like D3 or Plotly):**

Circos was chosen because it produces publication-quality chord diagrams with precise control over ribbon geometry. D3 chord diagrams are interactive but less visually polished. Circos is the standard tool for this type of visualization in academic and life-sciences contexts.

---

### Step 05 — `05_taper_ribbon_svg.py`

**Input:**
- Raw SVG from Circos: `outputs/renders/order_experiment_v3/overall/major_job_circos_v3.svg`

**Output:**
- `outputs/renders/order_exp_v3_svg_taper/overall/major_job_circos_v3_svg_taper.svg`

**What it does:**

Circos draws ribbons as simple bezier curves — they are the same width at both ends. This script modifies the SVG path geometry so ribbons taper to a narrow point at the midpoint of their arc, then widen again at the other end. It also:

- Replaces Circos's default bitmap font labels with properly rendered vector text using system fonts (Segoe UI)
- Applies bold weight to arc labels
- Wraps long labels over multiple lines

**Why this step exists:**

Tapered ribbons are visually clearer when many ribbons overlap — the taper shows directionality and reduces the visual mass at the center of the diagram. This is a standard practice in scientific chord diagrams but requires SVG post-processing because Circos does not support it natively.

**Key parameters:**

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `--mid-scale` | `0.28` | Ribbon width at midpoint is 28% of endpoint width |
| `--profile-power` | `1.35` | Rate of taper (higher = more aggressive narrowing) |

---

### Step 06 — `06_generate_career_focus_svgs.py`

**Input:**
- Tapered overall SVG: `outputs/renders/order_exp_v3_svg_taper/overall/major_job_circos_v3_svg_taper.svg`
- Layout reference: `outputs/renders/order_exp_v3_blue_up_keep_colors/overall/`

**Output:**
- `site/v3_ordered_images/main.svg` — the overall diagram
- `site/v3_ordered_images/majors/*.svg` — one SVG per major cluster (ribbons for all other majors hidden)
- `site/v3_ordered_images/careers/*.svg` — one SVG per career cluster (ribbons for all other careers hidden)

**What it does:**

For each major cluster, produces a copy of the full diagram where only the ribbons connected to that major are visible (others set to transparent). This is how the "click a thumbnail → filter the diagram" behavior works in the browser — it's not a dynamic filter, it's a pre-rendered set of 22 different SVG files.

**Why pre-rendered instead of dynamic filtering:**

Pre-rendered SVGs load instantly and work in any browser without JavaScript SVG manipulation, which can be slow with hundreds of ribbon paths. This approach also ensures the dashboard works as a simple static file without a server.

---

### Steps 07 + 08 — Industry Mobility Dashboard

**Step 07 — `07_generate_circos_data_industry.py`**

Input: `data/raw/Class_of_2026_CPF_vs_SP26.csv` + `data/raw/major.csv`

Output: `outputs/renders/incoming_grad_grouped_latest/` (Circos config files + raw SVG)

This script groups majors into 14 industry-style groups (e.g., `Acct/Fin/Ops`, `CS/DS/DA/Math/Stat`, `Engineering`) for both the incoming semester and the graduating semester, then draws ribbons from each incoming group to each graduating group. Students who stayed in the same group create self-loops.

**Step 08 — `08_generate_industry_focus_svgs.py`**

Input: `outputs/renders/incoming_grad_grouped_latest/main.svg`

Output: `site/incoming_grad_grouped_dashboard_images/` (27 SVGs)

Same pre-rendering logic as Step 06 — one SVG per incoming group plus one per graduating group.

---

### Steps 09 + 10 — College Mobility Dashboard

Same logic as Steps 07–08 but at the college level (OCB, CAS, EDUC, COH, SOE, Other) rather than industry group level.

**Step 09:** `data/raw/Class_of_2026_CPF_vs_SP26.csv` + `data/raw/major.csv` → `outputs/renders/incoming_grad_grouped_college_latest/`

**Step 10:** College latest SVG → `site/incoming_grad_grouped_college_dashboard_images/` (38 SVGs)

---

## What the HTML Files Actually Do

Each dashboard HTML file is essentially:

1. A `<img>` tag pointing to `main.svg` for the large center diagram.
2. A grid of thumbnail `<img>` tags pointing to each focus SVG.
3. JavaScript that swaps the center image `src` when you click a thumbnail.
4. A panel on the right loaded from `dashboard_docs_data.js` — this is a separate JavaScript file containing the methodology text, cluster descriptions, and counts that appear in the documentation panel.

The `dashboard_docs_data.js` file is **hand-maintained** — it is not generated by any script. If you change cluster names or add new groups, you need to update this file manually to reflect the new names and counts.

---

## How to Update for a New Cohort

When new data arrives (e.g., Class of 2027), the expected process is:

1. Replace `data/raw/career_survey_data.xlsx` with the new Excel export. Verify the column names match (`Program Name/Major`, `Job Title`).
2. Replace `data/raw/Class_of_2026_CPF_vs_SP26.csv` with the new enrollment transition file. Verify columns (`ID`, `Incoming Major`, `Graduating Major` or equivalent).
3. Update `data/raw/major.csv` if the university added new majors or reorganized any college.
4. Run `python run_pipeline.py`.
5. Check the outputs for any new unclassified job titles (they will appear in `outputs/lookup/Unmatched_Job_Titles_Summary.csv`). If many titles are unclassified, add them to `inputs/job_title_categorized.csv`.
6. Update the counts in `site/dashboard_docs_data.js` to reflect the new cohort size.
7. Update the cache-buster query strings in each HTML file (e.g., change `?v=20260507` to `?v=20270507`).

---

## Common Errors

| Error | Likely cause | Fix |
|-------|-------------|-----|
| `FileNotFoundError: circos.conf` | Circos CLI not found or `CIRCOS_ROOT` wrong | See `CIRCOS_SETUP.md` |
| `KeyError: 'Program Name/Major'` | Column name changed in new Excel export | Check column names in Excel, update the constant in `01_rebuild_cluster_lookup.py` |
| `KeyError: 'Incoming Major'` | Column name changed in CPF CSV | Check column names, update the constant in `07_generate_circos_data_industry.py` |
| SVGs are blank | Circos ran but produced no output | Check `outputs/renders/.../circos.conf` for syntax errors; run `circos -conf circos.conf` manually to see error output |
| Dashboard thumbnails don't match center image | SVG filenames changed | Verify that `site/v3_ordered_images/majors/*.svg` filenames match the JavaScript `MAJORS` array in `index.html` |
