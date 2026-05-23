import csv
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FULL = BASE_DIR / "inputs" / "Major_Job_Cluster_Lookup_Rebuilt_Full_baseline.csv"
OUTPUT_LOOKUP = BASE_DIR / "outputs" / "lookup"
OUTPUT_REPORTS = BASE_DIR / "outputs" / "reports"


BIG_ENGINEERING = "ENGINEERING, SCIENCE & TECHNOLOGY"
BIG_BUSINESS = "BUSINESS & MANAGEMENT"
BIG_HUMCOMM = "HUMANITIES & COMMUNICATION"
BIG_SOCED = "SOCIAL SCIENCES & EDUCATION"


MAJOR_REMAP = {
    "Finance & Accounting": ("Finance & Accounting", BIG_BUSINESS),
    "General Business": ("General Business", BIG_BUSINESS),
    "Operations & Analytics": ("Operations & Analytics", BIG_BUSINESS),
    "Specialized Business": ("Specialized Business", BIG_BUSINESS),
    "Marketing & Communication": ("Marketing & Communication", BIG_HUMCOMM),
    "Communication Studies": ("Marketing & Communication", BIG_HUMCOMM),
    "Journalism & Media": ("Marketing & Communication", BIG_HUMCOMM),
    "Creative Writing": ("Marketing & Communication", BIG_HUMCOMM),
    "Arts & Theology": ("Languages, Arts & Humanities", BIG_HUMCOMM),
    "English & Writing": ("Languages, Arts & Humanities", BIG_HUMCOMM),
    "Languages": ("Languages, Arts & Humanities", BIG_HUMCOMM),
    "Engineering Disciplines": ("Engineering", BIG_ENGINEERING),
    "Computer Science & IT": ("Computer Science & IT", BIG_ENGINEERING),
    "Biological Sciences": ("Biological & Health Sciences", BIG_ENGINEERING),
    "Health & Wellness": ("Biological & Health Sciences", BIG_ENGINEERING),
    "Physical Sciences": ("Physical & Environmental Sciences", BIG_ENGINEERING),
    "Environmental Sciences": ("Physical & Environmental Sciences", BIG_ENGINEERING),
    "Teacher Education": ("Education & Social Services", BIG_SOCED),
    "Social Work": ("Education & Social Services", BIG_SOCED),
    "Special Education & Counseling": ("Education & Social Services", BIG_SOCED),
    "Educational Leadership": ("Education & Social Services", BIG_SOCED),
    "Social Sciences": ("Social Sciences & Humanities", BIG_SOCED),
    "Humanities & Liberal Arts": ("Social Sciences & Humanities", BIG_SOCED),
    "International Studies": ("Social Sciences & Humanities", BIG_SOCED),
    "Economics": ("Economics", BIG_SOCED),
}


def write_csv(path: Path, rows: list[list[str]], header: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.writer(file_obj)
        writer.writerow(header)
        writer.writerows(rows)


def remap_major(small_major: str, large_major: str) -> tuple[str, str]:
    small_major = (small_major or "").strip()
    large_major = (large_major or "").strip()
    if small_major in MAJOR_REMAP:
        return MAJOR_REMAP[small_major]
    if small_major == "Unclassified" or large_major == "Unclassified":
        return "Unclassified", "Unclassified"
    return small_major, large_major


def main() -> None:
    rows = list(csv.DictReader(INPUT_FULL.open(encoding="utf-8")))
    full_rows: list[list[str]] = []
    filtered_rows: list[list[str]] = []
    big_counts: Counter[str] = Counter()
    small_counts: Counter[tuple[str, str]] = Counter()

    for row in rows:
        new_small, new_large = remap_major(row["Small Major Cluster"], row["Large Major Cluster"])
        out_row = [
            row["Major"],
            new_small,
            new_large,
            row["Job Title"],
            row["Small Job Title Cluster"],
            row["Large Job Title Cluster"],
        ]
        full_rows.append(out_row)

        if (
            new_small
            and new_large
            and row["Small Job Title Cluster"].strip()
            and row["Large Job Title Cluster"].strip()
            and row["Small Job Title Cluster"].strip().lower() != "unclassified jobs"
            and row["Large Job Title Cluster"].strip().lower() != "unclassified"
            and new_small.lower() != "unclassified"
            and new_large.lower() != "unclassified"
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
    write_csv(OUTPUT_LOOKUP / "Major_Job_Cluster_Lookup_v2_full.csv", full_rows, header)
    write_csv(OUTPUT_LOOKUP / "Major_Job_Cluster_Lookup_v2_filtered.csv", filtered_rows, header)

    big_rows = [[cluster, count] for cluster, count in big_counts.most_common()]
    small_rows = [[large, small, count] for (large, small), count in sorted(small_counts.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))]
    write_csv(OUTPUT_REPORTS / "major_cluster_counts_v2.csv", big_rows, ["Large Major Cluster", "Count"])
    write_csv(OUTPUT_REPORTS / "small_major_cluster_counts_v2.csv", small_rows, ["Large Major Cluster", "Small Major Cluster", "Count"])

    notes = [
        "# Major Remap V2 Notes",
        "",
        "This file documents the first-round major-cluster merge requested for the v2 workspace.",
        "",
        "Assumptions applied:",
        "",
        f"- `ENGINEERING & TECHNOLOGY` and `NATURAL & HEALTH SCIENCES` were combined into `{BIG_ENGINEERING}`.",
        "- `Engineering Disciplines` was kept as `Engineering`.",
        "- `Computer Science & IT` was kept separate as `Computer Science & IT`.",
        "- `Biological Sciences` and `Health & Wellness` were merged into `Biological & Health Sciences`.",
        "- `Physical Sciences` and `Environmental Sciences` were merged into `Physical & Environmental Sciences`.",
        f"- `COMMUNICATION & MEDIA` plus `Marketing & Communication` were consolidated into `{BIG_HUMCOMM}`.",
        "- `Marketing & Communication`, `Communication Studies`, `Journalism & Media`, and `Creative Writing` were merged into `Marketing & Communication`.",
        "- `Arts & Theology`, `English & Writing`, and `Languages` were merged into `Languages, Arts & Humanities`.",
        f"- `EDUCATION & SOCIAL SERVICES` and `SOCIAL SCIENCES & HUMANITIES` were combined into `{BIG_SOCED}`.",
        "- `Teacher Education`, `Social Work`, `Special Education & Counseling`, and `Educational Leadership` were merged into `Education & Social Services`.",
        "- `Social Sciences`, `Humanities & Liberal Arts`, and `International Studies` were merged into `Social Sciences & Humanities`.",
        "- `Economics` was kept separate as its own small major cluster inside `SOCIAL SCIENCES & EDUCATION`.",
        "",
        "This version changes only major clustering. Career reclustering and color redesign are intentionally left for the next pass.",
    ]
    (OUTPUT_REPORTS / "major_remap_v2_notes.md").write_text("\n".join(notes) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
