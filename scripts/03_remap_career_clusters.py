import csv
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FULL = BASE_DIR / "outputs" / "lookup" / "Major_Job_Cluster_Lookup_v2_full.csv"
INPUT_MANUAL_CATEGORIZATION = BASE_DIR / "inputs" / "job_title_categorized.csv"
OUTPUT_LOOKUP = BASE_DIR / "outputs" / "lookup"
OUTPUT_REPORTS = BASE_DIR / "outputs" / "reports"


CAREER_REMAP = {
    "Engineering": ("Engineering", "Engineering"),
    "Finance & Investment": ("Finance & Accounting", "Finance & Accounting"),
    "Accounting & Audit": ("Finance & Accounting", "Finance & Accounting"),
    "Management & Operations": ("Management & Ops", "Management & Ops"),
    "Leadership (General)": ("Management & Ops", "Management & Ops"),
    "Software & Data": ("Software & Data", "Software & Data"),
    "IT & Infrastructure": ("Software & Data", "Software & Data"),
    "Sales & Marketing": ("Sales & Marketing", "Sales & Marketing"),
    "Clinical Care": ("Health & Science Research", "Health & Science Research"),
    "Research & Science": ("Health & Science Research", "Health & Science Research"),
    "Education": ("Education & Social Service", "Education & Social Service"),
    "Social Service": ("Education & Social Service", "Education & Social Service"),
    "Legal & Policy": ("Legal & Policy", "Legal & Policy"),
    "Unclassified Jobs": ("Other", "Other"),
}


JOB_TITLE_OVERRIDES = {
    "associate": ("Management & Ops", "Management & Ops"),
    "analyst": ("Software & Data", "Software & Data"),
    "business analyst": ("Management & Ops", "Management & Ops"),
    "associate consultant": ("Management & Ops", "Management & Ops"),
    "consultant": ("Management & Ops", "Management & Ops"),
    "server": ("Management & Ops", "Management & Ops"),
    "technical recruiter": ("Management & Ops", "Management & Ops"),
    "business development representative": ("Sales & Marketing", "Sales & Marketing"),
    "recruiter": ("Management & Ops", "Management & Ops"),
    "scribe": ("Health & Science Research", "Health & Science Research"),
    "assurance associate": ("Finance & Accounting", "Finance & Accounting"),
    "delivery driver": ("Management & Ops", "Management & Ops"),
    "advisory services analyst": ("Finance & Accounting", "Finance & Accounting"),
    "development associate": ("Sales & Marketing", "Sales & Marketing"),
    "nursing": ("Health & Science Research", "Health & Science Research"),
    "fso assurance staff": ("Finance & Accounting", "Finance & Accounting"),
    "barista": ("Management & Ops", "Management & Ops"),
    "project analyst": ("Management & Ops", "Management & Ops"),
    "business development specialist": ("Sales & Marketing", "Sales & Marketing"),
    "rn": ("Health & Science Research", "Health & Science Research"),
    "host/hostess": ("Management & Ops", "Management & Ops"),
    "reinsurance analyst": ("Finance & Accounting", "Finance & Accounting"),
    "bartender": ("Management & Ops", "Management & Ops"),
    "sourcing analyst": ("Management & Ops", "Management & Ops"),
    "sourcing and procurement analyst": ("Management & Ops", "Management & Ops"),
    "accounting associate": ("Finance & Accounting", "Finance & Accounting"),
    "transfer pricing associate": ("Finance & Accounting", "Finance & Accounting"),
    "environmental specialist": ("Health & Science Research", "Health & Science Research"),
    "customer service representative": ("Management & Ops", "Management & Ops"),
    "flight attendant": ("Management & Ops", "Management & Ops"),
    "recruitment specialist": ("Management & Ops", "Management & Ops"),
    "tdp associate": ("Management & Ops", "Management & Ops"),
    "missionary": ("Education & Social Service", "Education & Social Service"),
    "customer service associate": ("Management & Ops", "Management & Ops"),
    "customer service specialist": ("Management & Ops", "Management & Ops"),
    "program associate": ("Management & Ops", "Management & Ops"),
    "operations analyst": ("Management & Ops", "Management & Ops"),
    "business development associate": ("Sales & Marketing", "Sales & Marketing"),
    "case manager": ("Education & Social Service", "Education & Social Service"),
    "research assistant": ("Health & Science Research", "Health & Science Research"),
    "project coordinator": ("Management & Ops", "Management & Ops"),
    "administrative assistant": ("Management & Ops", "Management & Ops"),
    "pricing analyst": ("Finance & Accounting", "Finance & Accounting"),
    "underwriting associate": ("Finance & Accounting", "Finance & Accounting"),
    "relationship banker": ("Finance & Accounting", "Finance & Accounting"),
    "clinical assistant": ("Health & Science Research", "Health & Science Research"),
    "talent acquisition specialist": ("Management & Ops", "Management & Ops"),
    "service coordinator": ("Education & Social Service", "Education & Social Service"),
    "care coordinator": ("Health & Science Research", "Health & Science Research"),
    "event coordinator": ("Management & Ops", "Management & Ops"),
    "procurement analyst": ("Management & Ops", "Management & Ops"),
    "operations associate": ("Management & Ops", "Management & Ops"),
    "product specialist": ("Sales & Marketing", "Sales & Marketing"),
    "data analyst": ("Software & Data", "Software & Data"),
    "software developer": ("Software & Data", "Software & Data"),
}


MANUAL_CATEGORY_MAP = {
    "Engineering": ("Engineering", "Engineering"),
    "Finance/Investment": ("Finance & Accounting", "Finance & Accounting"),
    "Management/Ops": ("Management & Ops", "Management & Ops"),
    "Software/Data": ("Software & Data", "Software & Data"),
    "Sales/Marketing": ("Sales & Marketing", "Sales & Marketing"),
    "Clinical Care": ("Health & Science Research", "Health & Science Research"),
    "Research/Science": ("Health & Science Research", "Health & Science Research"),
    "Education & Social Service": ("Education & Social Service", "Education & Social Service"),
    "Legal/Policy": ("Legal & Policy", "Legal & Policy"),
    "Other/Unclear": ("Other", "Other"),
}


def write_csv(path: Path, rows: list[list[str]], header: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.writer(file_obj)
        writer.writerow(header)
        writer.writerows(rows)


def load_manual_categorization() -> dict[str, tuple[str, str]]:
    if not INPUT_MANUAL_CATEGORIZATION.exists():
        return {}
    rows = list(csv.DictReader(INPUT_MANUAL_CATEGORIZATION.open(encoding="utf-8-sig")))
    mapping: dict[str, tuple[str, str]] = {}
    for row in rows:
        title = (row.get("Job Title") or "").strip().lower()
        category = (row.get("Category") or "").strip()
        if not title or category not in MANUAL_CATEGORY_MAP:
            continue
        mapping[title] = MANUAL_CATEGORY_MAP[category]
    return mapping


def remap_career(job_title: str, small_career: str, large_career: str, manual_map: dict[str, tuple[str, str]]) -> tuple[str, str]:
    job_title = (job_title or "").strip().lower()
    small_career = (small_career or "").strip()
    large_career = (large_career or "").strip()
    if job_title in manual_map:
        return manual_map[job_title]
    if job_title in JOB_TITLE_OVERRIDES:
        return JOB_TITLE_OVERRIDES[job_title]
    if small_career in CAREER_REMAP:
        return CAREER_REMAP[small_career]
    if small_career == "Unclassified Jobs" or large_career == "Unclassified":
        return "Other", "Other"
    return small_career, large_career


def main() -> None:
    rows = list(csv.DictReader(INPUT_FULL.open(encoding="utf-8")))
    manual_map = load_manual_categorization()
    full_rows: list[list[str]] = []
    filtered_rows: list[list[str]] = []
    big_counts: Counter[str] = Counter()
    small_counts: Counter[tuple[str, str]] = Counter()

    for row in rows:
        new_small, new_large = remap_career(row["Job Title"], row["Small Job Title Cluster"], row["Large Job Title Cluster"], manual_map)
        out_row = [
            row["Major"],
            row["Small Major Cluster"],
            row["Large Major Cluster"],
            row["Job Title"],
            new_small,
            new_large,
        ]
        full_rows.append(out_row)

        if (
            row["Small Major Cluster"].strip()
            and row["Large Major Cluster"].strip()
            and new_small
            and new_large
            and row["Small Major Cluster"].strip().lower() != "unclassified"
            and row["Large Major Cluster"].strip().lower() != "unclassified"
            and new_large != "Other"
        ):
            filtered_rows.append(out_row)
            big_counts[new_large] += 1
            small_counts[(new_large, new_small)] += 1

    header = [
        "Major",
        "Small Major Cluster",
        "Large Major Cluster",
        "Job Title",
        "Small Job Title Cluster",
        "Large Job Title Cluster",
    ]
    write_csv(OUTPUT_LOOKUP / "Major_Job_Cluster_Lookup_v2_full_career_merged.csv", full_rows, header)
    write_csv(OUTPUT_LOOKUP / "Major_Job_Cluster_Lookup_v2_filtered_career_merged.csv", filtered_rows, header)

    big_rows = [[cluster, count] for cluster, count in big_counts.most_common()]
    small_rows = [[large, small, count] for (large, small), count in sorted(small_counts.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))]
    write_csv(OUTPUT_REPORTS / "career_cluster_counts_v2.csv", big_rows, ["Large Job Title Cluster", "Count"])
    write_csv(OUTPUT_REPORTS / "small_career_cluster_counts_v2.csv", small_rows, ["Large Job Title Cluster", "Small Job Title Cluster", "Count"])

    notes = [
        "# Career Remap V2 Notes",
        "",
        "This file documents the first-round career-cluster merge requested for the v2 workspace.",
        "",
        "Career merges applied:",
        "",
        "- `Accounting & Audit` was merged into `Finance & Accounting`.",
        "- `Leadership (General)` was merged into `Management & Ops`.",
        "- `IT & Infrastructure` was merged into `Software & Data`.",
        "- `Clinical Care` and `Research & Science` were merged into `Health & Science Research`.",
        "- `Education` and `Social Service` were merged into `Education & Social Service`.",
        "- rows with mapped majors but unclassified job titles were retained and merged into `Other` in the full file.",
        "- the publishable filtered file excludes `Other` because only a very small edge-case set remained.",
        "- selected high-frequency `Other` titles were force-mapped based on professor-approved assumptions.",
        "- manual classifications from `inputs/job_title_categorized.csv` were applied before fallback rules.",
        "",
        "Standalone career clusters retained:",
        "",
        "- `Engineering`",
        "- `Finance & Accounting`",
        "- `Management & Ops`",
        "- `Software & Data`",
        "- `Sales & Marketing`",
        "- `Health & Science Research`",
        "- `Education & Social Service`",
        "- `Legal & Policy`",
        "- `Other`",
    ]
    (OUTPUT_REPORTS / "career_remap_v2_notes.md").write_text("\n".join(notes) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
