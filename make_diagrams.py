"""
make_diagrams.py
----------------
Generates two PNG images for the Word report:
  1. folder_tree.png  — annotated package folder structure
  2. pipeline_flow.png — full 10-step data pipeline diagram
Run from the reproducible_package folder:  python make_diagrams.py
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

OUT = Path(__file__).parent

# ─── colour palette ────────────────────────────────────────────────────────────
NAVY     = "#122A52"
BLUE     = "#2F6DB3"
LTBLUE   = "#4A84C4"
VLTBLUE  = "#D6E4F5"
GREEN    = "#2E8B57"
LTGREEN  = "#D4EDDA"
ORANGE   = "#E68613"
LTORANGE = "#FDE8CB"
PURPLE   = "#B279A2"
LTPURPLE = "#F0DFF0"
GRAY     = "#B9B9B9"
LTGRAY   = "#F5F5F5"
DARKGRAY = "#444444"
WHITE    = "#FFFFFF"
RED_ACC  = "#C0392B"


# ══════════════════════════════════════════════════════════════════════════════
# 1.  FOLDER TREE
# ══════════════════════════════════════════════════════════════════════════════

TREE_LINES = [
    # (indent, icon, name, annotation, is_folder)
    (0, "[ROOT]", "reproducible_package/",        "GitHub repo root",                     True),
    (1, "[doc]",  "README.md",                     "Quick-start guide",                    False),
    (1, "[doc]",  "PIPELINE_OVERVIEW.md",          "10-step data flow + rationale",        False),
    (1, "[doc]",  "DATA_CLEANING_DECISIONS.md",    "Every data decision documented",       False),
    (1, "[doc]",  "VISUALIZATION_RULES.md",        "Colors, layout, SVG rules",            False),
    (1, "[doc]",  "CIRCOS_SETUP.md",               "Circos install (Win / Mac / Linux)",   False),
    (1, "[doc]",  "requirements.txt",              "pandas  openpyxl",                     False),
    (1, "[doc]",  "run_pipeline.py",               "Master runner — runs all 10 steps",    False),
    (1, "[doc]",  "Career_Outcome_Visualization_Report.docx", "This report",              False),
    (1, "[doc]",  "career_survey_data.xlsx",       "Raw career survey  (4,129 rows)",      False),
    (0, "",       "",                              "",                                     False),
    (1, "[dir]",  "inputs/",                       "Baseline reference CSVs",              True),
    (2, "[doc]",  "Major_Job_Cluster_Lookup_Rebuilt_Full_baseline.csv", "",                False),
    (2, "[doc]",  "Major_Job_Cluster_Lookup_Filtered_baseline.csv",     "",                False),
    (2, "[doc]",  "job_title_categorized.csv",     "~87 manual job-title overrides",       False),
    (2, "[doc]",  "Major_Career_Analysis_v4__Cluster_Breakdown.csv",    "",                False),
    (2, "[doc]",  "Major_Career_Analysis_v4__Career_Analysis.csv",      "",                False),
    (0, "",       "",                              "",                                     False),
    (1, "[dir]",  "outputs/",                      "Created by pipeline (empty at start)", True),
    (2, "[dir]",  "lookup/",                       "Intermediate + final lookup CSVs",     True),
    (3, "[doc]",  "Major_Job_Cluster_Lookup_v2_filtered_career_merged.csv", "Pre-built final lookup", False),
    (2, "[dir]",  "renders/",                      "Circos config files + raw SVGs",       True),
    (2, "[dir]",  "reports/",                      "Cluster count reports",                True),
    (0, "",       "",                              "",                                     False),
    (1, "[dir]",  "scripts/",                      "10 numbered production scripts",       True),
    (2, "[doc]",  "01_rebuild_cluster_lookup.py",  "Excel -> row-level classified lookup", False),
    (2, "[doc]",  "02_remap_major_clusters.py",    "24 -> 13 major display clusters",      False),
    (2, "[doc]",  "03_remap_career_clusters.py",   "14 -> 8 career display clusters",      False),
    (2, "[doc]",  "04_generate_circos_data_career.py", "Lookup -> Circos config (career)", False),
    (2, "[doc]",  "05_taper_ribbon_svg.py",        "SVG post-processing + fonts",          False),
    (2, "[doc]",  "06_generate_career_focus_svgs.py", "Extract 22 focus SVGs",            False),
    (2, "[doc]",  "07_generate_circos_data_industry.py", "-> Circos config (industry)",   False),
    (2, "[doc]",  "08_generate_industry_focus_svgs.py", "Extract 27 focus SVGs",          False),
    (2, "[doc]",  "09_generate_circos_data_college.py", "-> Circos config (college)",     False),
    (2, "[doc]",  "10_generate_college_focus_svgs.py", "Extract 38 focus SVGs",           False),
    (0, "",       "",                              "",                                     False),
    (1, "[dir]",  "site/",                         "Finished dashboards — open in browser", True),
    (2, "[doc]",  "index.html",                    "Career Outcomes Dashboard",            False),
    (2, "[doc]",  "incoming_grad_grouped.html",    "Industry Mobility Dashboard",          False),
    (2, "[doc]",  "incoming_grad_grouped_college.html", "College Mobility Dashboard",      False),
    (2, "[doc]",  "dashboard_docs.css / .js / _data.js", "Shared UI + methodology text",  False),
    (2, "[dir]",  "v3_ordered_images/",            "22 SVGs — career dashboard",           True),
    (2, "[dir]",  "incoming_grad_grouped_dashboard_images/", "27 SVGs — industry",         True),
    (2, "[dir]",  "incoming_grad_grouped_college_dashboard_images/", "38 SVGs — college",  True),
    (2, "[dir]",  "incomingmajor_fall2022_csv/",   "Mobility source data (925 students)",  True),
    (3, "[doc]",  "Class_of_2026_CPF_vs_SP26.csv", "",                                    False),
    (3, "[doc]",  "major.csv",                     "Major -> group -> college mapping",    False),
]

def make_folder_tree():
    n_rows = len(TREE_LINES)
    fig_h  = max(14, n_rows * 0.28 + 1.5)
    fig, ax = plt.subplots(figsize=(14, fig_h))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, fig_h)
    ax.axis("off")

    # background
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    # title
    ax.text(0.15, fig_h - 0.35, "Package Folder Structure",
            fontsize=15, fontweight="bold", color=NAVY,
            fontfamily="monospace")
    ax.text(0.15, fig_h - 0.72,
            "reproducible_package/  —  everything needed to view, understand, and regenerate the dashboards",
            fontsize=8.5, color=DARKGRAY)
    # divider
    ax.plot([0.1, 13.9], [fig_h - 0.88, fig_h - 0.88], color=BLUE, lw=1.5)

    y = fig_h - 1.25
    row_h = 0.275

    for indent, icon, name, annot, is_folder in TREE_LINES:
        if not name:
            y -= row_h * 0.45
            continue

        x_base = 0.15 + indent * 0.52

        # connector lines
        if indent > 0:
            ax.plot([x_base - 0.35, x_base - 0.05], [y + 0.06, y + 0.06],
                    color="#CCCCCC", lw=0.8)
            if indent == 1:
                ax.plot([x_base - 0.35, x_base - 0.35], [y + 0.06, y + row_h * 0.9],
                        color="#CCCCCC", lw=0.8)
            else:
                ax.plot([x_base - 0.35, x_base - 0.35], [y + 0.06, y + row_h * 0.9],
                        color="#DDDDDD", lw=0.7)

        # icon badge
        if icon == "[ROOT]":
            badge_clr, badge_txt, badge_fc = NAVY,  "PKG", "#D6E4F5"
        elif icon == "[dir]":
            badge_clr, badge_txt, badge_fc = ORANGE, "DIR", LTORANGE
        else:
            badge_clr, badge_txt, badge_fc = LTBLUE, "doc", VLTBLUE

        rect = FancyBboxPatch((x_base - 0.04, y - 0.095), 0.42, 0.195,
                               boxstyle="round,pad=0.02",
                               linewidth=0.6, edgecolor=badge_clr,
                               facecolor=badge_fc)
        ax.add_patch(rect)
        ax.text(x_base + 0.17, y, badge_txt,
                ha="center", va="center",
                fontsize=5.8, fontweight="bold", color=badge_clr)

        # name text
        ax.text(x_base + 0.52, y, name,
                fontsize=8.8 if is_folder else 8.3,
                fontweight="bold" if is_folder else "normal",
                color=NAVY if is_folder else DARKGRAY,
                fontfamily="monospace",
                va="center")

        # annotation
        if annot:
            ax.text(6.8, y, f"← {annot}",
                    fontsize=7.8, color="#777777", va="center",
                    style="italic")

        y -= row_h

    # legend
    ax.plot([0.1, 13.9], [y + 0.05, y + 0.05], color="#DDDDDD", lw=0.8)
    ax.text(0.15, y - 0.15, "DIR = folder    doc = file    <- annotation describes the file's purpose",
            fontsize=7.5, color="#888888")

    plt.tight_layout(pad=0.3)
    path = OUT / "folder_tree.png"
    plt.savefig(path, dpi=160, bbox_inches="tight", facecolor=WHITE)
    plt.close()
    print(f"Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# 2.  PIPELINE FLOW DIAGRAM
# ══════════════════════════════════════════════════════════════════════════════

def box(ax, x, y, w, h, label, sublabel="", color=BLUE, text_color=WHITE,
        fontsize=8.5, radius=0.015):
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle=f"round,pad={radius}",
                           linewidth=0.8,
                           edgecolor=color,
                           facecolor=color)
    ax.add_patch(rect)
    if sublabel:
        ax.text(x, y + h*0.15, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=text_color,
                wrap=True)
        ax.text(x, y - h*0.22, sublabel, ha="center", va="center",
                fontsize=fontsize - 1.5, color=text_color, style="italic")
    else:
        ax.text(x, y, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=text_color,
                wrap=True)


def arrow(ax, x1, y1, x2, y2, color=DARKGRAY, lw=1.2, style="->"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, connectionstyle="arc3,rad=0.0"))


def make_pipeline_flow():
    fig, ax = plt.subplots(figsize=(17, 11))
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 11)
    ax.axis("off")
    fig.patch.set_facecolor("#FAFBFC")

    # ── Title ──
    ax.text(8.5, 10.6, "Career Outcome Visualization — Data Pipeline",
            ha="center", fontsize=15, fontweight="bold", color=NAVY)
    ax.text(8.5, 10.25, "10-step pipeline: raw Excel/CSV  →  Python classification  →  Circos render  →  SVG  →  HTML dashboards",
            ha="center", fontsize=9, color=DARKGRAY)
    ax.plot([0.4, 16.6], [10.08, 10.08], color=BLUE, lw=1.5)

    # ── Track labels ──
    for lbl, x, clr in [
        ("CAREER TRACK  (Steps 1–6)", 4.25, BLUE),
        ("INDUSTRY MOBILITY  (Steps 7–8)", 10.5, GREEN),
        ("COLLEGE MOBILITY  (Steps 9–10)", 14.2, PURPLE),
    ]:
        ax.text(x, 9.75, lbl, ha="center", fontsize=8.5,
                fontweight="bold", color=clr,
                bbox=dict(boxstyle="round,pad=0.25", fc=WHITE, ec=clr, lw=1))

    # ╔══════════════════════════════════════════════════════╗
    # ║  RAW INPUTS  (top row)                               ║
    # ╚══════════════════════════════════════════════════════╝
    # Career raw inputs
    box(ax, 1.6, 9.05, 2.6, 0.52,
        "career_survey_data.xlsx", "4,129 rows · Major + Job Title",
        color="#B8860B", text_color=WHITE, fontsize=8)
    box(ax, 4.5, 9.05, 2.6, 0.52,
        "External cluster CSVs", "Major_Career_Analysis_v4__*.csv",
        color="#B8860B", text_color=WHITE, fontsize=8)

    # Mobility raw inputs
    box(ax, 10.5, 9.05, 3.2, 0.52,
        "Class_of_2026_CPF_vs_SP26.csv", "925 students · Incoming → Graduating major",
        color="#B8860B", text_color=WHITE, fontsize=8)
    box(ax, 14.2, 9.05, 2.2, 0.52,
        "major.csv", "Major → Group → College",
        color="#B8860B", text_color=WHITE, fontsize=8)

    # ╔══════════════════════════════════════════════════════╗
    # ║  CAREER TRACK  steps 1–3                            ║
    # ╚══════════════════════════════════════════════════════╝
    # Step 01
    arrow(ax, 1.6, 8.79, 1.6, 8.28)
    arrow(ax, 4.5, 8.79, 4.5, 8.28)
    box(ax, 3.05, 7.98, 4.9, 0.54,
        "Step 01 · rebuild_cluster_lookup.py",
        "Excel → row-level lookup  |  3 match tiers: exact → normalized → heuristic rules",
        color=BLUE, fontsize=8)

    # Step 02
    arrow(ax, 3.05, 7.71, 3.05, 7.21)
    box(ax, 3.05, 6.91, 4.9, 0.54,
        "Step 02 · remap_major_clusters.py",
        "Consolidate 24 raw major clusters → 13 display clusters  |  4 large academic families",
        color=BLUE, fontsize=8)

    # Step 03
    arrow(ax, 3.05, 6.64, 3.05, 6.14)
    box(ax, 3.05, 5.84, 4.9, 0.54,
        "Step 03 · remap_career_clusters.py",
        "Consolidate 14 career clusters → 8 display clusters  |  apply manual overrides",
        color=BLUE, fontsize=8)

    # Final lookup output
    arrow(ax, 3.05, 5.57, 3.05, 5.1)
    box(ax, 3.05, 4.83, 4.9, 0.48,
        "outputs/lookup/Major_Job_Cluster_Lookup_v2_filtered_career_merged.csv",
        "2,682 classified graduates  |  major cluster  +  career cluster per row",
        color="#27AE60", text_color=WHITE, fontsize=7.8)

    # ── inputs/ baseline arrow (into step 02) ──
    ax.annotate("", xy=(1.3, 6.91), xytext=(0.45, 6.91),
                arrowprops=dict(arrowstyle="->", color="#B8860B", lw=1,
                                connectionstyle="arc3,rad=0.0"))
    ax.text(0.38, 6.97, "inputs/\nbaseline CSVs",
            ha="center", fontsize=6.8, color="#B8860B", style="italic")

    # ╔══════════════════════════════════════════════════════╗
    # ║  CAREER TRACK  steps 4–6                            ║
    # ╚══════════════════════════════════════════════════════╝
    arrow(ax, 3.05, 4.59, 3.05, 4.09)
    box(ax, 3.05, 3.79, 4.9, 0.54,
        "Step 04 · generate_circos_data_career.py",
        "Lookup → karyotype.txt · links.txt · circos.conf · colors.conf  (v3 arc ordering)",
        color=LTBLUE, text_color=WHITE, fontsize=8)

    # Circos CLI
    arrow(ax, 3.05, 3.52, 3.05, 3.0)
    box(ax, 3.05, 2.72, 3.0, 0.5,
        "Circos CLI",
        "major_job_circos_v3.svg",
        color=DARKGRAY, fontsize=8)

    # Step 05 taper
    arrow(ax, 3.05, 2.47, 3.05, 1.97)
    box(ax, 3.05, 1.69, 4.9, 0.54,
        "Step 05 · taper_ribbon_svg.py",
        "Taper ribbon geometry  ·  replace Circos fonts with Segoe UI  ·  bold labels",
        color=LTBLUE, text_color=WHITE, fontsize=8)

    arrow(ax, 3.05, 1.42, 3.05, 0.95)
    box(ax, 3.05, 0.68, 4.9, 0.54,
        "Step 06 · generate_career_focus_svgs.py",
        "Extract 22 focus SVGs  (1 overall + 13 major + 8 career)  →  site/v3_ordered_images/",
        color=LTBLUE, text_color=WHITE, fontsize=8)

    # ╔══════════════════════════════════════════════════════╗
    # ║  INDUSTRY MOBILITY TRACK  steps 7–8                 ║
    # ╚══════════════════════════════════════════════════════╝
    arrow(ax, 10.5, 8.79, 10.5, 7.21)
    arrow(ax, 14.2, 8.79, 12.2, 7.21)
    box(ax, 10.5, 6.91, 4.5, 0.54,
        "Step 07 · generate_circos_data_industry.py",
        "Group majors into 14 industry groups  ·  count transitions  →  incoming_grad_grouped_latest/",
        color=GREEN, fontsize=8)

    arrow(ax, 10.5, 6.64, 10.5, 6.0)
    box(ax, 10.5, 5.72, 2.6, 0.5,
        "Circos CLI", "main.svg",
        color=DARKGRAY, fontsize=8)

    arrow(ax, 10.5, 5.47, 10.5, 4.97)
    box(ax, 10.5, 4.69, 4.5, 0.54,
        "Step 08 · generate_industry_focus_svgs.py",
        "Extract 27 focus SVGs  →  site/incoming_grad_grouped_dashboard_images/",
        color="#1A7A48", text_color=WHITE, fontsize=8)

    # ╔══════════════════════════════════════════════════════╗
    # ║  COLLEGE MOBILITY TRACK  steps 9–10                 ║
    # ╚══════════════════════════════════════════════════════╝
    arrow(ax, 10.5, 8.79, 14.2, 7.21)
    arrow(ax, 14.2, 8.79, 14.2, 7.21)
    box(ax, 14.2, 6.91, 4.5, 0.54,
        "Step 09 · generate_circos_data_college.py",
        "Group by college (OCB/CAS/EDUC/COH/SOE)  →  incoming_grad_grouped_college_latest/",
        color=PURPLE, fontsize=8)

    arrow(ax, 14.2, 6.64, 14.2, 6.0)
    box(ax, 14.2, 5.72, 2.6, 0.5,
        "Circos CLI", "main.svg",
        color=DARKGRAY, fontsize=8)

    arrow(ax, 14.2, 5.47, 14.2, 4.97)
    box(ax, 14.2, 4.69, 4.5, 0.54,
        "Step 10 · generate_college_focus_svgs.py",
        "Extract 38 focus SVGs  →  site/incoming_grad_grouped_college_dashboard_images/",
        color="#7B3F9E", text_color=WHITE, fontsize=8)

    # ╔══════════════════════════════════════════════════════╗
    # ║  SHARED UI ASSETS                                    ║
    # ╚══════════════════════════════════════════════════════╝
    box(ax, 8.5, 3.3, 3.6, 0.48,
        "dashboard_docs.css / .js / _data.js",
        "Shared stylesheet · interaction JS · methodology text (hand-maintained)",
        color="#555555", text_color=WHITE, fontsize=7.5)

    # ╔══════════════════════════════════════════════════════╗
    # ║  FINAL OUTPUTS (HTML dashboards)                     ║
    # ╚══════════════════════════════════════════════════════╝
    arrow(ax, 3.05, 0.41, 5.4, 0.0 + 0.42)
    arrow(ax, 10.5, 4.42, 8.0, 0.42 + 0.52)
    arrow(ax, 14.2, 4.42, 11.6, 0.42 + 0.52)
    arrow(ax, 8.5, 3.06, 8.5, 0.9)

    # Three dashboard boxes
    box(ax, 3.9, 0.38, 3.5, 0.54,
        "site/index.html",
        "Career Outcomes Dashboard  |  2,682 graduates",
        color=NAVY, fontsize=8)
    box(ax, 8.5, 0.38, 3.5, 0.54,
        "site/incoming_grad_grouped.html",
        "Industry Mobility Dashboard  |  925 students",
        color=NAVY, fontsize=8)
    box(ax, 13.1, 0.38, 3.5, 0.54,
        "site/incoming_grad_grouped_college.html",
        "College Mobility Dashboard  |  925 students",
        color=NAVY, fontsize=8)

    arrow(ax, 10.5, 4.42, 11.35, 0.42 + 0.52)
    arrow(ax, 14.2, 4.42, 13.0, 0.42 + 0.52)

    # ── legend ──────────────────────────────────────────────────────────────
    legend_items = [
        (mpatches.Patch(color="#B8860B"), "Raw input files"),
        (mpatches.Patch(color=BLUE),      "Career track scripts (Steps 1–3)"),
        (mpatches.Patch(color=LTBLUE),    "Career track scripts (Steps 4–6)"),
        (mpatches.Patch(color=GREEN),     "Industry mobility (Steps 7–8)"),
        (mpatches.Patch(color=PURPLE),    "College mobility (Steps 9–10)"),
        (mpatches.Patch(color="#27AE60"), "Final lookup CSV"),
        (mpatches.Patch(color=NAVY),      "HTML dashboard outputs"),
    ]
    handles, labels = zip(*legend_items)
    ax.legend(handles, labels, loc="lower right",
              bbox_to_anchor=(1.0, -0.01),
              fontsize=7.5, framealpha=0.9,
              ncol=4, columnspacing=1.0,
              handlelength=1.2, handletextpad=0.5)

    plt.tight_layout(pad=0.5)
    path = OUT / "pipeline_flow.png"
    plt.savefig(path, dpi=160, bbox_inches="tight", facecolor="#FAFBFC")
    plt.close()
    print(f"Saved: {path}")


if __name__ == "__main__":
    make_folder_tree()
    make_pipeline_flow()
    print("Both diagrams generated.")
