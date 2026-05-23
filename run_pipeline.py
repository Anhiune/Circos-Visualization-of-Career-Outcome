"""
run_pipeline.py
---------------
Master runner for the Career Outcome Visualization pipeline.

This script runs all 10 steps in order to reproduce the three dashboards
from raw data files. Read README.md and PIPELINE_OVERVIEW.md before running.

Usage:
    python run_pipeline.py                     # run all steps
    python run_pipeline.py --steps 1 2 3       # run specific steps
    python run_pipeline.py --steps 4-6         # run a range of steps
    python run_pipeline.py --skip 5            # skip a step
    python run_pipeline.py --dry-run           # show what would run without running

Prerequisites:
    1. Python 3.10+ with: pip install -r requirements.txt
    2. Circos installed and CIRCOS_ROOT environment variable set (see CIRCOS_SETUP.md)
    3. Input data files in data/raw/ (see README.md for file list)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = PACKAGE_DIR / "scripts"

# ---------------------------------------------------------------------------
# Pipeline step definitions
# Each step is: (number, display_name, script_path, extra_args_fn)
# extra_args_fn receives PACKAGE_DIR and returns a list of additional CLI args.
# ---------------------------------------------------------------------------

def _career_taper_args(pkg: Path) -> list[str]:
    """
    Step 05 (taper_ribbon_svg.py) requires explicit --input-svg and --output-svg.
    Input: the raw SVG produced by Circos in Step 04.
    Output: the tapered SVG consumed by Step 06.
    """
    renders = pkg / "outputs" / "renders"
    input_svg = renders / "order_experiment_v3" / "overall" / "major_job_circos_v3.svg"
    output_dir = renders / "order_exp_v3_svg_taper" / "overall"
    output_svg = output_dir / "major_job_circos_v3_svg_taper.svg"
    output_dir.mkdir(parents=True, exist_ok=True)
    return [
        "--input-svg", str(input_svg),
        "--output-svg", str(output_svg),
        "--mid-scale", "0.28",
        "--profile-power", "1.35",
    ]


STEPS: list[tuple[int, str, str, object]] = [
    (
        1,
        "Rebuild cluster lookup from raw Excel data",
        "01_rebuild_cluster_lookup.py",
        None,
    ),
    (
        2,
        "Remap and consolidate major clusters (24 → 13 display clusters)",
        "02_remap_major_clusters.py",
        None,
    ),
    (
        3,
        "Remap and consolidate career clusters (14 → 8 display clusters)",
        "03_remap_career_clusters.py",
        None,
    ),
    (
        4,
        "Generate Circos config files for career dashboard",
        "04_generate_circos_data_career.py",
        None,
    ),
    (
        5,
        "Taper ribbon SVG + apply custom fonts (career dashboard)",
        "05_taper_ribbon_svg.py",
        _career_taper_args,
    ),
    (
        6,
        "Extract per-major and per-career focus SVGs (career dashboard)",
        "06_generate_career_focus_svgs.py",
        None,
    ),
    (
        7,
        "Generate Circos config files for industry mobility dashboard",
        "07_generate_circos_data_industry.py",
        None,
    ),
    (
        8,
        "Extract per-group focus SVGs (industry mobility dashboard)",
        "08_generate_industry_focus_svgs.py",
        None,
    ),
    (
        9,
        "Generate Circos config files for college mobility dashboard",
        "09_generate_circos_data_college.py",
        None,
    ),
    (
        10,
        "Extract per-college focus SVGs (college mobility dashboard)",
        "10_generate_college_focus_svgs.py",
        None,
    ),
]


def parse_step_list(token: str) -> list[int]:
    """Parse '1', '1,2,3', or '4-6' into a list of ints."""
    result = []
    for part in token.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            result.extend(range(int(lo), int(hi) + 1))
        else:
            result.append(int(part))
    return result


def check_prerequisites() -> bool:
    """Check that Circos and required Python packages are available."""
    ok = True

    circos_root = os.environ.get("CIRCOS_ROOT", "")
    if not circos_root:
        print("WARNING: CIRCOS_ROOT environment variable is not set.")
        print("         Steps 4, 7, and 9 will fail when they try to call Circos.")
        print("         See CIRCOS_SETUP.md for installation instructions.")
        print()
        ok = False
    else:
        circos_bin = Path(circos_root) / "bin" / "circos"
        if not circos_bin.exists():
            print(f"WARNING: Circos executable not found at {circos_bin}")
            print("         Check that CIRCOS_ROOT points to your Circos install folder.")
            print()
            ok = False

    # Check input data files
    required_files = [
        PACKAGE_DIR / "career_survey_data.xlsx",
        PACKAGE_DIR / "site" / "incomingmajor_fall2022_csv" / "Class_of_2026_CPF_vs_SP26.csv",
        PACKAGE_DIR / "site" / "incomingmajor_fall2022_csv" / "major.csv",
        PACKAGE_DIR / "inputs" / "Major_Job_Cluster_Lookup_Rebuilt_Full_baseline.csv",
        PACKAGE_DIR / "inputs" / "job_title_categorized.csv",
    ]
    for path in required_files:
        if not path.exists():
            print(f"WARNING: Missing input file: {path.relative_to(PACKAGE_DIR)}")
            ok = False

    if not ok:
        print()

    return ok


def run_step(step_num: int, name: str, script: str, extra_args_fn: object, dry_run: bool) -> bool:
    """Run a single pipeline step. Returns True if successful."""
    script_path = SCRIPTS_DIR / script
    if not script_path.exists():
        print(f"  ERROR: Script not found: {script_path}")
        return False

    cmd = [sys.executable, str(script_path)]
    if extra_args_fn is not None:
        cmd.extend(extra_args_fn(PACKAGE_DIR))

    print(f"\n{'='*60}")
    print(f"Step {step_num}: {name}")
    print(f"Script: {script}")
    if dry_run:
        print(f"  [DRY RUN] Would run: {' '.join(cmd)}")
        return True

    print(f"Running...")
    start = time.time()
    result = subprocess.run(cmd, cwd=str(SCRIPTS_DIR))
    elapsed = time.time() - start

    if result.returncode == 0:
        print(f"  OK ({elapsed:.1f}s)")
        return True
    else:
        print(f"  FAILED (exit code {result.returncode}, {elapsed:.1f}s)")
        print(f"  Re-run manually: python scripts/{script}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Career Outcome Visualization pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--steps",
        nargs="+",
        help="Run only these steps (e.g., --steps 1 2 3 or --steps 4-6)",
    )
    parser.add_argument(
        "--skip",
        nargs="+",
        help="Skip these steps (e.g., --skip 5)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would run without actually running it.",
    )
    parser.add_argument(
        "--no-prereq-check",
        action="store_true",
        help="Skip the prerequisite check at startup.",
    )
    args = parser.parse_args()

    # Determine which steps to run
    if args.steps:
        requested = set()
        for token in args.steps:
            requested.update(parse_step_list(token))
    else:
        requested = {s[0] for s in STEPS}

    if args.skip:
        skipped = set()
        for token in args.skip:
            skipped.update(parse_step_list(token))
        requested -= skipped

    steps_to_run = [s for s in STEPS if s[0] in requested]

    print("Career Outcome Visualization Pipeline")
    print(f"Package directory: {PACKAGE_DIR}")
    print(f"Steps to run: {sorted(requested)}")
    print()

    if not args.no_prereq_check:
        check_prerequisites()

    if args.dry_run:
        print("[DRY RUN MODE — no scripts will actually be executed]\n")

    failed_steps = []
    for step_num, name, script, extra_args_fn in steps_to_run:
        success = run_step(step_num, name, script, extra_args_fn, args.dry_run)
        if not success:
            failed_steps.append(step_num)
            print(f"\nPipeline stopped at Step {step_num}.")
            print("Fix the error above and then re-run with:")
            remaining = [s[0] for s in steps_to_run if s[0] >= step_num]
            print(f"  python run_pipeline.py --steps {' '.join(str(s) for s in remaining)}")
            sys.exit(1)

    print(f"\n{'='*60}")
    if not args.dry_run:
        print("All steps completed successfully.")
        print()
        print("Your dashboards are ready. Open these files in a browser:")
        print(f"  {PACKAGE_DIR / 'site' / 'index.html'}")
        print(f"  {PACKAGE_DIR / 'site' / 'incoming_grad_grouped.html'}")
        print(f"  {PACKAGE_DIR / 'site' / 'incoming_grad_grouped_college.html'}")
    else:
        print("Dry run complete. Run without --dry-run to execute the pipeline.")


if __name__ == "__main__":
    main()
