# Data Cleaning and Clustering Decisions

This document records every significant data decision made during the four months of building this project. The goal is that a new student can read this and understand *why* the data looks the way it does, not just *what* it looks like.

---

## Source Data Overview

### Career survey data (`career_survey_data.xlsx`)

- **Origin:** Annual career outcomes survey export from Gonzaga's career services office.
- **Total raw rows:** 4,129 (one per graduate response).
- **Key columns used:** `Program Name/Major`, `Job Title`.
- **Key columns ignored:** Name, student ID, graduation year (not needed for the dashboard).

### Enrollment transition data (`Class_of_2026_CPF_vs_SP26.csv`)

- **Origin:** Registrar enrollment snapshot comparing students' declared major in their first semester (CPF) to their declared major at graduation (SP26).
- **Total rows:** 925 students who had a declared incoming major AND a declared graduating major.
- **Key columns used:** `Incoming Major` (or equivalent), `Graduating Major` (or equivalent).
- **Students excluded from this dataset:** Students who left the university, who declared late, or who had no detectable incoming major on record.

### Major grouping file (`major.csv`)

- **Origin:** Manually created by the project team from the university's academic catalog.
- **Columns:** `Major` (exact name as it appears in the enrollment data), `Group` (industry-style group abbreviation), `School` (college abbreviation).
- **Purpose:** Translates individual major names (e.g., `Computer Science`, `Data Science`) into the 14 display groups (e.g., `CS/DS/DA/Math/Stat`) used in the mobility dashboards.

---

## Decision 1: What counts as a classifiable career title?

**Rule applied:** A row is included in the final dashboard if and only if:
1. The major was matched to a cluster (every major was matched after aliases were added — see Decision 3).
2. The job title field is not blank.
3. The job title was classified into a non-"Other" career cluster.

**Why blank job titles are excluded:**

1,338 out of 4,129 rows had no job title. These represent graduates who did not report a career outcome in the survey (not employed, in graduate school, or did not respond to this field). It would be misleading to infer a career for them.

**Why "Other" is excluded from the filtered output:**

After applying heuristics, a small residual set (~60–80 titles) remained unclassifiable. These titles were either highly idiosyncratic (e.g., highly specialized government titles, role names that only exist at one organization) or ambiguous enough that any assignment would be a guess. Including a visible "Other" arc would misrepresent those graduates as forming a meaningful outcome cluster. They are retained in the full (unfiltered) lookup for reference.

**Implication for dashboard counts:**

The dashboard shows **2,682 graduates** rather than 4,129 because 1,338 had no job title and ~89 had unclassifiable titles after all heuristics were applied.

---

## Decision 2: Why rebuild the lookup from scratch instead of using the original?

The original project had a pre-existing lookup table from an external analysis. That lookup covered approximately 1,078 job titles exactly. Out of 4,129 raw rows, this produced only about 1,100–1,200 classified rows — a severe loss rate.

The decision was made to rebuild the lookup using:
1. Exact match against the original table (preserves continuity).
2. Normalized match (lowercase + strip punctuation — recovers simple formatting variants).
3. Rule-based heuristic classification (keyword matching against ~15 rule families).

This raised the classified row count to approximately 2,682, recovering roughly 1,500 additional graduates.

**Risk accepted:** The heuristic rules introduce the possibility of misclassification. For example, a title containing "research" will be assigned to `Health & Science Research` even if it describes market research at a financial firm. This was an explicit decision to prioritize coverage over precision for a public-facing aggregate visualization. Individual student data is not visible on the dashboard — only aggregated counts are displayed.

---

## Decision 3: Major name aliases

The raw Excel data contains inconsistent major name formats. Many represent the same academic program under different labels. The following aliases were defined (left = raw name in Excel, right = canonical cluster assignment used):

| Raw major name | Mapped to |
|----------------|-----------|
| `Computer Science (BS)` | `Computer Science` |
| `Data Science` | `Computer Science & IT` |
| `Information Technology` | `Computer Science & IT` |
| `Software Engineering` | `Computer Science & IT` |
| `Software Management` | `Computer Science & IT` |
| `Systems Engineering` | `Mechanical Engineering` → `Engineering` |
| `Manufacturing Engineering` | `Mechanical Engineering` → `Engineering` |
| `Biology (BS)` | `Biology` |
| `Economics - Public Policy` | `Economics` |
| `Economics - Business` | `Economics` |
| `Economics - International` | `Economics` |
| `Economics - Mathematical` | `Economics` |
| `MBA` | `General Business` |
| `Executive MBA` | `General Business` |
| `Health Care MBA` | `General Business` |
| `Liberal Arts` | `Philosophy` → `Humanities` |
| `Teacher Preparation - K-12` | `Middle/Secondary Education` |
| `Music Education` | `K-12 Music Education` |
| `Autism Spectrum Disorders` | `Social Work` → `Education & Social Services` |
| `Counseling Psychology` | `Psychology` → `Social Sciences` |
| `Organization Develop & Change` | `Human Resources Management` → `Specialized Business` |
| `Health Care Innovation` | `Public Health` → `Biological & Health Sciences` |
| `Regulatory Science` | `Chemistry` → `Physical & Environmental Sciences` |

**Why aliases instead of correcting the source:**

Aliases are more transparent. You can see exactly which raw names were reassigned and why. Silently correcting the source file would make it harder for a future student to audit the decisions.

---

## Decision 4: Economics is a Social Science, not a Business

**Decision:** All Economics variants (`Economics`, `Economics - Business`, `Economics - International`, `Economics - Mathematical`, `Economics - Public Policy`) were assigned to `SOCIAL SCIENCES & EDUCATION`, not to `BUSINESS & MANAGEMENT`.

**Rationale:**
- Economics is taught in the College of Arts & Sciences at Gonzaga, not in the School of Business.
- Treating Economics as a social science is consistent with standard academic classification (e.g., US News, Carnegie Classification).
- A student majoring in economics with a business track does not have the same credentials as an MBA or Finance major for career purposes.
- Merging Economics into Business would inflate the Business arc size artificially.

**Visual effect:** Economics appears as a distinct small arc adjacent to the Social Sciences cluster on the diagram.

---

## Decision 5: Major cluster consolidation rules

The raw rebuild produced 24 small-cluster names. These were consolidated into 13 display clusters for cleaner visualization. The consolidation follows these principles:

**Rule 1 — Functional similarity over academic taxonomy.** `Biological Sciences` and `Health & Wellness` were merged because graduates from both groups are following similar career pathways (healthcare, research, clinical work).

**Rule 2 — Visual arc size.** Clusters with fewer than ~50 graduates were merged with adjacent related clusters. A cluster with 30 graduates would be nearly invisible on the Circos diagram.

**Rule 3 — Audience expectations.** A general university audience expects to see "Business" as a unified group even though it contains Finance, Marketing, Operations, and Management sub-programs. The merges respect this expectation.

**Full consolidation mapping:**

| Raw cluster name(s) | Display cluster | Large family |
|--------------------|----------------|-------------|
| `Engineering Disciplines` | `Engineering` | ENGINEERING, SCIENCE & TECHNOLOGY |
| `Computer Science & IT` | `Computer Science & IT` | ENGINEERING, SCIENCE & TECHNOLOGY |
| `Biological Sciences` + `Health & Wellness` | `Biological & Health Sciences` | ENGINEERING, SCIENCE & TECHNOLOGY |
| `Physical Sciences` + `Environmental Sciences` | `Physical & Environmental Sciences` | ENGINEERING, SCIENCE & TECHNOLOGY |
| `Finance & Accounting` | `Finance & Accounting` | BUSINESS & MANAGEMENT |
| `General Business` | `General Business` | BUSINESS & MANAGEMENT |
| `Operations & Analytics` | `Operations & Analytics` | BUSINESS & MANAGEMENT |
| `Specialized Business` | `Specialized Business` | BUSINESS & MANAGEMENT |
| `Marketing & Communication` + `Communication Studies` + `Journalism & Media` + `Creative Writing` | `Marketing & Communication` | HUMANITIES & COMMUNICATION |
| `Arts & Theology` + `English & Writing` + `Languages` | `Languages, Arts & Humanities` | HUMANITIES & COMMUNICATION |
| `Teacher Education` + `Social Work` + `Special Education & Counseling` + `Educational Leadership` | `Education & Social Services` | SOCIAL SCIENCES & EDUCATION |
| `Social Sciences` + `Humanities & Liberal Arts` + `International Studies` | `Social Sciences & Humanities` | SOCIAL SCIENCES & EDUCATION |
| `Economics` | `Economics` | SOCIAL SCIENCES & EDUCATION |

---

## Decision 6: Career cluster consolidation rules

The initial career classification (from Step 1 heuristics) produced 14 cluster names. These were consolidated to 8 display clusters:

| Raw career cluster(s) | Display cluster |
|----------------------|----------------|
| `Finance & Investment` + `Accounting & Audit` | `Finance & Accounting` |
| `Management & Operations` + `Leadership (General)` | `Management & Ops` |
| `Software & Data` + `IT & Infrastructure` | `Software & Data` |
| `Sales & Marketing` | `Sales & Marketing` |
| `Clinical Care` + `Research & Science` | `Health & Science Research` |
| `Education` + `Social Service` | `Education & Social Service` |
| `Legal & Policy` | `Legal & Policy` |
| `Engineering` | `Engineering` |

**Why IT & Infrastructure merged into Software & Data:**

IT support and infrastructure roles are often the career outcome of the same majors as software development roles (Computer Science, Information Technology). Separating them would show an artificially small "IT Infrastructure" arc next to a large "Software" arc, which would mislead viewers into thinking few CS graduates go into IT work.

**Why Engineering stayed separate:**

Engineering graduates overwhelmingly go into engineering roles (mechanical, civil, electrical, chemical). Merging Engineering into "Software & Data" or a general technology bucket would obscure this strong pipeline.

**Why Legal & Policy stayed separate:**

Law is a distinct outcome that audiences expect to see called out. Merging it into "Management & Ops" (because it involves policy coordination) would be misleading.

---

## Decision 7: Manual job title overrides (`job_title_categorized.csv`)

Approximately 87 job titles were reviewed manually and assigned a category that the heuristics could not determine reliably. Examples:

| Job title | Assigned category | Reason |
|-----------|------------------|--------|
| `Associate` | `Management/Ops` | Too generic for keyword rules; most Associates at this career stage are in entry-level ops roles |
| `Analyst` | `Software/Data` | Could be financial or data; treated as data given university's CS graduate count |
| `Business Analyst` | `Management/Ops` | Distinct from data analyst; focuses on process improvement |
| `Consultant` | `Management/Ops` | General consulting, not IT consulting |
| `Scribe` | `Clinical Care` | Medical scribe = clinical support role |
| `RN` | `Clinical Care` | Registered Nurse abbreviation |
| `Server` | `Management/Ops` | Food service / hospitality — operational |
| `Barista` | `Management/Ops` | Same reasoning as Server |
| `Bartender` | `Management/Ops` | Same |
| `Sourcing Analyst` | `Management/Ops` | Supply chain, not data analytics |
| `Fso Assurance Staff` | `Finance/Investment` | Financial services assurance |
| `Delivery Driver` | `Management/Ops` | Operations/logistics |
| `Flight Attendant` | `Management/Ops` | Aviation operations |
| `Missionary` | `Education & Social Service` | Service/humanitarian role |

The full list is in `data/raw/inputs/job_title_categorized.csv`.

---

## Decision 8: Why 925 students in the mobility dashboards vs. 2,682 in the career dashboard

These are two separate datasets from two separate data sources:

- **Career dashboard (2,682):** Career survey responses. A student appears if they graduated AND reported a job title to career services.
- **Mobility dashboards (925):** Registrar enrollment data. A student appears if they have a recorded incoming major AND a recorded graduating major in the administrative system.

These are not the same 925 students who are a subset of 2,682. Many of the 925 in mobility data did not report a career outcome (or reported a blank job title) and therefore do not appear in the career dashboard.

---

## Decision 9: Layout order on the Circos diagram

The major clusters appear in this clockwise order on the diagram:

1. Engineering
2. Computer Science & IT
3. Biological & Health Sciences
4. Physical & Environmental Sciences
5. Finance & Accounting
6. General Business
7. Operations & Analytics
8. Specialized Business
9. Marketing & Communication
10. Languages, Arts & Humanities
11. Education & Social Services
12. Social Sciences & Humanities
13. Economics

This order was chosen after testing 7 layout experiments (v1–v7) to minimize ribbon crossings. The principle used: place major clusters that share graduates with similar career clusters adjacent to each other. Engineering and CS graduates both go heavily into Software & Data, so they are placed adjacent. Economics graduates split between Finance and Social sectors, so Economics is placed at the boundary between the Business and Social Science families.

Career clusters appear on the right half of the circle in a mirrored order to reduce the number of ribbons that cross each other at the center.

---

## Decision 10: Filtering the mobility data

For the mobility dashboards, the raw enrollment data was filtered to keep only students who:

1. Had a non-blank incoming major.
2. Had a non-blank graduating major.
3. Were in a cohort year consistent with the CPF vs. SP26 comparison.

Students who changed majors multiple times, took leaves of absence, or had enrollment anomalies were included as long as both endpoints (incoming and graduating) were defined. The dashboard shows where they ended up, not the path they took to get there.

---

## What to Do When New Data Arrives

1. **New job titles appear unclassified:** Check `outputs/lookup/Unmatched_Job_Titles_Summary.csv` after running Step 1. Add high-frequency unclassified titles to `data/raw/inputs/job_title_categorized.csv` with an appropriate category.

2. **A new major appears that has no match:** Check `outputs/lookup/Unmatched_Majors_Summary.csv`. Add an alias entry in `scripts/01_rebuild_cluster_lookup.py` under `MAJOR_NAME_ALIASES` or `DIRECT_CLUSTER_OVERRIDES`.

3. **A college reorganizes (e.g., a major moves from CAS to a new school):** Update `data/raw/major.csv` to reflect the new school assignment for that major.

4. **You want to add a new cluster:** This requires changes to Step 2 or Step 3 scripts (the REMAP dictionaries), AND to the HTML files (which have the arc names and display labels hard-coded), AND to `dashboard_docs_data.js`. See `VISUALIZATION_RULES.md` for the HTML constants you need to change.
