# Visualization Rules

This document records every visual design decision: colors, layout, fonts, spacing, SVG post-processing, and the rules hard-coded in the HTML files. If you need to change any visual aspect of the dashboards, start here.

---

## Color System

### Why these four colors?

The palette was designed with three requirements:
1. **Colorblind-friendly:** No red-green pairing (affects ~8% of men). Blue, teal-green, orange, and purple give sufficient contrast for deuteranopia and protanopia.
2. **Four distinct families:** One color per large academic family, shaded darker-to-lighter for the sub-clusters within each family.
3. **Career arcs are neutral gray:** Career outcomes use gray so the eye naturally separates the "source" (colored major arcs) from the "destination" (gray career arcs).

### Major cluster colors

| Large family | Hex | RGB | Shade usage |
|-------------|-----|-----|------------|
| BUSINESS & MANAGEMENT | `#2F6DB3` | (47, 109, 179) | Darkest shade for the anchor cluster |
| | `#275F9B` | (39, 95, 155) | Second cluster |
| | `#4A84C4` | (74, 132, 196) | Third cluster |
| | `#7EADDF` | (126, 173, 223) | Lightest (smallest) cluster |
| ENGINEERING, SCIENCE & TECHNOLOGY | `#115F3F` | (17, 95, 63) | Darkest |
| | `#227E52` | (34, 126, 82) | |
| | `#43A271` | (67, 162, 113) | |
| | `#79C699` | (121, 198, 153) | Lightest |
| SOCIAL SCIENCES & EDUCATION | `#B05D05` | (176, 93, 5) | Darkest |
| | `#D17809` | (209, 120, 9) | |
| | `#EA9A1D` | (234, 154, 29) | |
| | `#F8BF55` | (248, 191, 85) | Lightest |
| HUMANITIES & COMMUNICATION | `#754074` | (117, 64, 116) | Darkest |
| | `#915491` | (145, 84, 145) | |
| | `#B574B2` | (181, 116, 178) | |
| | `#D6A3D2` | (214, 163, 210) | Lightest |

### Career arc color

All career arcs use: `#B9B9B9` (RGB: 185, 185, 185) — a neutral medium gray.

**Why gray for careers?** The question the dashboard answers is "where do graduates from X major end up?" The major is the starting point (source), so it gets the informational color. The career is the destination — it doesn't need a color hierarchy of its own, and gray prevents the diagram from becoming overwhelming.

---

## Layout Ordering

### Major arc order (clockwise from top)

```
Engineering
Computer Science & IT
Biological & Health Sciences
Physical & Environmental Sciences
── gap (family boundary: EST → BUS) ──
Finance & Accounting
General Business
Operations & Analytics
Specialized Business
── gap (family boundary: BUS → HUM) ──
Marketing & Communication
Languages, Arts & Humanities
── gap (family boundary: HUM → SOC) ──
Education & Social Services
Social Sciences & Humanities
Economics
── gap (wraps back to Engineering) ──
```

### Career arc order (clockwise from top, opposite half)

```
Software & Data
Engineering
Finance & Accounting
Management & Ops
Sales & Marketing
Health & Science Research
Education & Social Service
Legal & Policy
```

### Why this specific order?

The ordering was chosen to minimize "crossing distance" for the most common connections. The principle: place a major cluster near the career clusters that receive the most graduates from that major. For example:

- Engineering and CS/IT are placed adjacent to Software & Data (their primary career destination).
- Finance & Accounting (major) is placed near Finance & Accounting (career).
- Education & Social Services (major) is placed near Education & Social Service (career).

This does not eliminate crossings (that is mathematically impossible for a chord diagram with many connections) but reduces the visual clutter at the center.

---

## Spacing and Geometry Parameters

These constants live in `scripts/04_generate_circos_data_career.py`. Change them there if you need to adjust the diagram geometry.

| Parameter | Value | Effect |
|-----------|-------|--------|
| `DEFAULT_SPACING` | `0.004r` | Gap between arc segments within a family |
| `MAJOR_FAMILY_SPACING` | `0.004r` | Gap at major cluster boundaries |
| `SECTOR_GAP_UNITS` | `18.0` | Gap between major and career halves (in karyotype units) |
| `LINK_RADIUS` | `0.99r` | Where ribbons attach to arc edge |
| `LINK_BEZIER_RADIUS` | `0.15r` | Controls how "bowed" ribbons are at their midpoint |
| `LINK_CREST` | `0.5` | Symmetry of ribbon curve |
| `LABEL_FONT` | `bold` | Circos label weight |
| `LABEL_RADIUS` | `1.02r` | How far outside the arc labels appear |
| `LABEL_SIZE` | `36` | Font size for arc labels (in Circos units ≈ 12pt) |
| `RIBBON_ALPHA` | `0.995` | Ribbon opacity (near-fully opaque) |

---

## SVG Taper Parameters

These constants live in `scripts/05_taper_ribbon_svg.py` and are passed as command-line arguments in `run_pipeline.py`.

| Parameter | Value | Effect |
|-----------|-------|--------|
| `--mid-scale` | `0.28` | Ribbon is 28% of its endpoint width at the midpoint |
| `--profile-power` | `1.35` | Taper aggressiveness (higher = narrower at center) |
| `--group-id` | `track_0` | SVG group ID containing ribbon paths (do not change unless Circos changes its output format) |

**Changing taper behavior:** Increase `--mid-scale` toward 1.0 for less taper (fatter ribbons at center). Decrease toward 0.1 for more taper (nearly invisible at center). Values below 0.15 can produce visual artifacts.

---

## Fonts

The dashboard uses system fonts in all SVG labels:

```
"Segoe UI", Tahoma, Geneva, Verdana, Arial, sans-serif
```

This is applied by the taper post-processing script, which replaces Circos's default Helvetica/bitmap font references with the system font stack.

**Why this font stack:** Segoe UI is the default Windows system UI font. It renders cleanly at small sizes and is widely available. The fallback chain (Tahoma → Geneva → Verdana → Arial) covers macOS and Linux.

---

## Label Text Rules

### Arc labels

- Long labels are word-wrapped at `\n` — the taper script splits labels longer than ~20 characters.
- Ampersands in labels are replaced with hyphens for display: `Education & Social Services` → `Education-Social-Services`.
- Spaces become hyphens: `Computer Science & IT` → `Computer-Science-&-IT`.
- This is a Circos requirement (Circos does not support spaces in label text fields natively).

### One known label override:

| Original Circos label | Display label |
|-----------------------|--------------|
| `Pre-Professional-Undeclared` | `Pre-Professional Undeclared` |

This is the only case where a label was corrected post-render. The override is in `taper_ribbon_svg.py` under `LABEL_TEXT_OVERRIDES`.

---

## Cache-Busting Query Strings

Each SVG `<img>` src in the HTML files has a query string like `?v=20260507normalized1`. This forces browsers to re-download the SVG if it was changed, because browsers aggressively cache image files.

**When you update an SVG, update the query string** in the corresponding HTML file to today's date. The format is:

```
?v=YYYYMMDD<shortdescription>
```

Example: `?v=20270115newcohort`

The query string has no effect on the SVG content — it is only used by the browser's caching layer.

---

## Dashboard Docs Panel

The right-side documentation panel in each dashboard is populated by `site/dashboard_docs_data.js`. This file is **not generated by any script** — it must be updated manually.

The file defines a `window.DASHBOARD_DOCS_DATA` object with three keys:

```javascript
window.DASHBOARD_DOCS_DATA = {
  career: {   /* content for index.html */
    title: "...",
    summary: "...",
    methodology: "...",
    clusters: [ { name: "...", description: "..." }, ... ]
  },
  grouped: {  /* content for incoming_grad_grouped.html */
    ...
  },
  groupedCollege: {  /* content for incoming_grad_grouped_college.html */
    ...
  }
}
```

If you add a new cluster, rename a cluster, or update graduate counts, you must edit this file to match.

---

## Pre-Rendered SVG Focus Set

### Career dashboard focus SVGs (`site/v3_ordered_images/`)

| Subfolder | Count | Naming convention |
|-----------|-------|-------------------|
| `main.svg` | 1 | Overall diagram |
| `majors/` | 13 | One per major cluster, e.g. `engineering.svg`, `finance_accounting.svg` |
| `careers/` | 8 | One per career cluster, e.g. `software_data.svg`, `health_science_research.svg` |

**Total: 22 SVGs**

### Industry mobility focus SVGs (`site/incoming_grad_grouped_dashboard_images/`)

| Path | Count |
|------|-------|
| `main.svg` | 1 |
| `incoming/` | 13 (one per incoming group) |
| `graduating/` | 13 (one per graduating group) |

**Total: 27 SVGs**

### College mobility focus SVGs (`site/incoming_grad_grouped_college_dashboard_images/`)

| Path | Count |
|------|-------|
| `main.svg` | 1 |
| `incoming_colleges/` | 6 (OCB, CAS, EDUC, COH, SOE, Other) |
| `graduating_colleges/` | 6 |
| `incoming/` | 12 (per-group within colleges) |
| `graduating/` | 13 |

**Total: 38 SVGs**

---

## Thumbnail Grid Layout

The thumbnail grid in each dashboard HTML is hard-coded. The JavaScript `MAJORS` and `CAREERS` arrays in each HTML file define which SVG filenames to load and what display names to show. If you rename a cluster, you must update:

1. The SVG filename generated by Step 06/08/10.
2. The array entry in the HTML file.
3. The label text in `dashboard_docs_data.js`.

The SVG filenames are generated from the cluster names by `clean_id()` in the generator scripts: spaces → underscores, `&` → `AND`, commas and parentheses removed, hyphens → underscores.
