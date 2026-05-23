import argparse
import csv
import re
from collections import Counter
from pathlib import Path

import pandas as pd


_PACKAGE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DATA = _PACKAGE_DIR / "career_survey_data.xlsx"
DEFAULT_MAJOR_CLUSTERS = _PACKAGE_DIR / "inputs" / "Major_Career_Analysis_v4__Cluster_Breakdown.csv"
DEFAULT_CAREER_CLUSTERS = _PACKAGE_DIR / "inputs" / "Major_Career_Analysis_v4__Career_Analysis.csv"
DEFAULT_OUTPUT_DIR = _PACKAGE_DIR / "outputs" / "lookup"


MAJOR_NAME_ALIASES = {
    "computer science (bs)": "computer science",
    "comp science bs (master track)": "comp science bs (master track)",
    "economics - public policy": "economics",
    "economics - business": "economics",
    "economics - international": "economics",
    "economics - mathematical": "economics",
    "biology (bs)": "biology",
    "geology (bs)": "geology",
    "physics (bs)": "physics",
    "data science": "data analytics",
    "information technology": "computer science",
    "software engineering": "computer science",
    "software management": "computer science",
    "systems engineering": "mechanical engineering",
    "manufacturing engineering": "mechanical engineering",
    "mba": "gen business mgmt",
    "executive mba": "gen business mgmt",
    "health care mba": "gen business mgmt",
    "leadership": "leadership & management",
    "spanish": "spanish cultural/literary st.",
    "creative writing & publishing": "english - creative writing",
    "music education": "k-12 music education",
    "liberal arts": "philosophy",
    "teacher preparation - k-12": "middle/secondary education",
    "teacher preparation-elem k-6": "elementary education (k-6)",
    "teacher preparation-secondary": "middle/secondary education",
    "educational studies": "middle/secondary education",
    "educational leadership & admin": "leadership & management",
    "educ leadership & learning": "leadership & management",
    "counseling psychology": "psychology",
    "pastoral leadership": "theology",
    "pastoral ministry": "theology",
    "autism spectrum disorders": "social work",
    "acad behavioral strategist": "social work",
    "early childhood special educ": "social work",
    "organization develop & change": "human resources management",
    "organization development": "human resources management",
    "org. ethics & compliance": "law & compliance",
    "health care innovation": "public health",
    "regulatory science": "chemistry",
    "technology management": "operations management",
    "u.s. law": "law & compliance",
    "publc safety & law enfr ldrshp": "law & compliance",
    "part-time flex mba": "gen business mgmt",
    "business administration": "gen business mgmt",
    "operations & supply chain mgmt": "operations management",
    "ms health care innovation": "public health",
    "mathematics (applied track)": "mathematics",
    "mathematics (education track)": "mathematics",
    "mathematics (pure track)": "mathematics",
    "mathematics (statistics track)": "statistics",
    "leadership in student affairs": "leadership & management",
}


DIRECT_CLUSTER_OVERRIDES = {
    "economics": {"small": "Economics", "large": "SOCIAL SCIENCES & HUMANITIES"},
    "economics public policy": {"small": "Economics", "large": "SOCIAL SCIENCES & HUMANITIES"},
    "economics - public policy": {"small": "Economics", "large": "SOCIAL SCIENCES & HUMANITIES"},
    "economics business": {"small": "Economics", "large": "SOCIAL SCIENCES & HUMANITIES"},
    "economics - business": {"small": "Economics", "large": "SOCIAL SCIENCES & HUMANITIES"},
    "economics international": {"small": "Economics", "large": "SOCIAL SCIENCES & HUMANITIES"},
    "economics - international": {"small": "Economics", "large": "SOCIAL SCIENCES & HUMANITIES"},
    "economics mathematical": {"small": "Economics", "large": "SOCIAL SCIENCES & HUMANITIES"},
    "economics - mathematical": {"small": "Economics", "large": "SOCIAL SCIENCES & HUMANITIES"},
    "liberal arts": {"small": "Humanities & Liberal Arts", "large": "SOCIAL SCIENCES & HUMANITIES"},
    "systems engineering": {"small": "Engineering Disciplines", "large": "ENGINEERING & TECHNOLOGY"},
    "manufacturing engineering": {"small": "Engineering Disciplines", "large": "ENGINEERING & TECHNOLOGY"},
    "data science": {"small": "Computer Science & IT", "large": "ENGINEERING & TECHNOLOGY"},
    "information technology": {"small": "Computer Science & IT", "large": "ENGINEERING & TECHNOLOGY"},
    "software engineering": {"small": "Computer Science & IT", "large": "ENGINEERING & TECHNOLOGY"},
    "software management": {"small": "Computer Science & IT", "large": "ENGINEERING & TECHNOLOGY"},
    "counseling psychology": {"small": "Social Sciences", "large": "SOCIAL SCIENCES & HUMANITIES"},
    "autism spectrum disorders": {"small": "Special Education & Counseling", "large": "EDUCATION & SOCIAL SERVICES"},
    "acad behavioral strategist": {"small": "Special Education & Counseling", "large": "EDUCATION & SOCIAL SERVICES"},
    "early childhood special educ": {"small": "Special Education & Counseling", "large": "EDUCATION & SOCIAL SERVICES"},
    "educational studies": {"small": "Teacher Education", "large": "EDUCATION & SOCIAL SERVICES"},
    "educational leadership & admin": {"small": "Educational Leadership", "large": "EDUCATION & SOCIAL SERVICES"},
    "educ leadership & learning": {"small": "Educational Leadership", "large": "EDUCATION & SOCIAL SERVICES"},
    "leadership in student affairs": {"small": "Educational Leadership", "large": "EDUCATION & SOCIAL SERVICES"},
    "organization develop & change": {"small": "Specialized Business", "large": "BUSINESS & MANAGEMENT"},
    "organization development": {"small": "Specialized Business", "large": "BUSINESS & MANAGEMENT"},
    "org. ethics & compliance": {"small": "Specialized Business", "large": "BUSINESS & MANAGEMENT"},
    "u.s. law": {"small": "Specialized Business", "large": "BUSINESS & MANAGEMENT"},
    "publc safety & law enfr ldrshp": {"small": "Specialized Business", "large": "BUSINESS & MANAGEMENT"},
    "mba": {"small": "General Business", "large": "BUSINESS & MANAGEMENT"},
    "executive mba": {"small": "General Business", "large": "BUSINESS & MANAGEMENT"},
    "health care mba": {"small": "General Business", "large": "BUSINESS & MANAGEMENT"},
    "health care innovation": {"small": "Health & Wellness", "large": "NATURAL & HEALTH SCIENCES"},
    "regulatory science": {"small": "Physical Sciences", "large": "NATURAL & HEALTH SCIENCES"},
    "technology management": {"small": "Operations & Analytics", "large": "BUSINESS & MANAGEMENT"},
    "part-time flex mba": {"small": "General Business", "large": "BUSINESS & MANAGEMENT"},
    "business administration": {"small": "General Business", "large": "BUSINESS & MANAGEMENT"},
    "operations & supply chain mgmt": {"small": "Operations & Analytics", "large": "BUSINESS & MANAGEMENT"},
    "ms health care innovation": {"small": "Health & Wellness", "large": "NATURAL & HEALTH SCIENCES"},
    "creative writing & publishing": {"small": "Creative Writing", "large": "COMMUNICATION & MEDIA"},
    "music education": {"small": "Teacher Education", "large": "EDUCATION & SOCIAL SERVICES"},
    "spanish": {"small": "Languages", "large": "ARTS, LANGUAGES & THEOLOGY"},
    "pastoral leadership": {"small": "Arts & Theology", "large": "ARTS, LANGUAGES & THEOLOGY"},
    "pastoral ministry": {"small": "Arts & Theology", "large": "ARTS, LANGUAGES & THEOLOGY"},
}


def normalize_text(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\b(sr|jr|ii|iii|iv)\b", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def load_major_cluster_map(path: Path) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            major = row["Major"].strip()
            mapping[major.lower()] = {
                "small": row["Small Cluster"].strip(),
                "large": row["Large Cluster"].strip(),
            }
    return mapping


def load_career_cluster_map(path: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as file_obj:
        rows = list(csv.reader(file_obj))

    header_idx = None
    for idx, row in enumerate(rows):
        if len(row) >= 3 and row[0] == "Large Cluster" and row[1] == "Small Cluster" and row[2] == "Job Title":
            header_idx = idx
            break

    if header_idx is None:
        raise ValueError(f"Could not find detailed breakdown header in {path}")

    exact: dict[str, dict[str, str]] = {}
    normalized: dict[str, dict[str, str]] = {}
    for row in rows[header_idx + 1:]:
        if len(row) < 4 or not row[0].strip():
            continue
        large = row[0].strip()
        small = row[1].strip()
        job_title = row[2].strip()
        if not job_title or job_title.lower() == "unknown":
            continue
        payload = {"small": small, "large": large}
        exact[job_title.lower()] = payload
        normalized[normalize_text(job_title)] = payload
    return exact, normalized


def lookup_major(major_name: str, major_map: dict[str, dict[str, str]]) -> dict[str, str]:
    key = major_name.strip().lower()
    normalized_key = normalize_text(major_name)
    if key in DIRECT_CLUSTER_OVERRIDES:
        return DIRECT_CLUSTER_OVERRIDES[key]
    if normalized_key in DIRECT_CLUSTER_OVERRIDES:
        return DIRECT_CLUSTER_OVERRIDES[normalized_key]
    if key in major_map:
        return major_map[key]
    if key in MAJOR_NAME_ALIASES:
        alias = MAJOR_NAME_ALIASES[key]
        if alias in major_map:
            return major_map[alias]
    return {"small": "", "large": ""}


def lookup_job(job_title: str, exact_map: dict[str, dict[str, str]], normalized_map: dict[str, dict[str, str]]) -> tuple[dict[str, str], str]:
    if not job_title or not job_title.strip():
        return {"small": "", "large": ""}, "blank"

    key = job_title.strip().lower()
    if key in exact_map:
        return exact_map[key], "exact"

    normalized_key = normalize_text(job_title)
    if normalized_key in normalized_map:
        return normalized_map[normalized_key], "normalized"

    return {"small": "Unclassified Jobs", "large": "Unclassified"}, "unclassified"


def classify_job_by_rules(job_title: str, major_cluster: dict[str, str]) -> dict[str, str]:
    title = job_title.strip()
    norm = normalize_text(title)
    major_large = major_cluster.get("large", "")
    major_small = major_cluster.get("small", "")

    if not norm:
        return {"small": "", "large": ""}

    def has(*parts: str) -> bool:
        return any(part in norm for part in parts)

    def is_major(*parts: str) -> bool:
        haystack = f"{major_large} {major_small}".lower()
        return any(part.lower() in haystack for part in parts)

    if has("teacher", "professor", "faculty", "paraeducator", "educator", "adjunct", "lecturer", "academic coach", "collegepoint coach", "college coach"):
        return {"small": "Education", "large": "Education & Service"}

    if has("social worker", "case manager", "child support", "family advocate", "youth worker", "direct care", "community support", "care coordinator"):
        return {"small": "Social Service", "large": "Education & Service"}

    if has("therapist", "counselor", "psychotherapist", "mental health", "clinical social worker", "registered nurse", " rn ", "nurse", "practitioner", "scribe", "behavioral health", "outpatient", "clinical care"):
        return {"small": "Clinical Care", "large": "Healthcare & Science"}

    if has("research", "scientist", "laboratory", "lab ", "researcher", "regulatory affairs", "quality control", "microbiologist", "chemist"):
        return {"small": "Research & Science", "large": "Healthcare & Science"}

    if has("attorney", "law", "legal", "compliance", "policy", "contract specialist", "police", "sergeant", "officer") and not has("sales officer", "loan officer", "security officer", "operations officer"):
        return {"small": "Legal & Policy", "large": "Arts, Media & Legal"}

    if has("accountant", "accounting", "audit", "auditor", "tax ", "taxation", "assurance", "controller", "bookkeeper", "cpa"):
        return {"small": "Accounting & Audit", "large": "Business & Finance"}

    if has("financial", "finance", "investment", "bank", "banking", "wealth", "advisor", "adviser", "planner", "paraplanner", "credit analyst", "underwriter", "actuarial", "treasury"):
        return {"small": "Finance & Investment", "large": "Business & Finance"}

    if has("sales", "account executive", "business development", "marketing", "communications", "public relations", "campaign", "brand manager", "ecommerce", "growth", "account manager", "customer success"):
        return {"small": "Sales & Marketing", "large": "Business & Finance"}

    if has("software", "developer", "programmer", "data scientist", "data engineer", "machine learning", "cyber security", "cybersecurity", "full stack", "application lead", "web developer", "business intelligence", "product development engineer"):
        return {"small": "Software & Data", "large": "Technology & Engineering"}

    if has("network", "infrastructure", "support specialist", "help desk", "it analyst", "systems analyst", "technical support", "desktop support", "system administrator", "cloud support", "tech aid", "technical analyst"):
        return {"small": "IT & Infrastructure", "large": "Technology & Engineering"}

    if has("engineer", "engineering", "electrical designer", "substation", "metrology", "manufacturing engineer", "traffic engineer", "controls engineer", "solutions engineer", "engineering technician"):
        return {"small": "Engineering", "large": "Technology & Engineering"}

    if has("supply chain", "procurement", "sourcing", "operations", "project", "program manager", "program analyst", "project specialist", "operations coordinator", "consultant", "logistics", "production manager", "manufacturing manager", "engagement manager"):
        return {"small": "Management & Operations", "large": "Business & Finance"}

    if has("technical product manager"):
        return {"small": "Software & Data", "large": "Technology & Engineering"}

    if has("product manager"):
        if is_major("ENGINEERING & TECHNOLOGY", "Computer Science & IT", "Engineering Disciplines"):
            return {"small": "Software & Data", "large": "Technology & Engineering"}
        return {"small": "Management & Operations", "large": "Business & Finance"}

    if has("director", "vice president", "vp ", "chief", "head of", "executive director", "assistant director", "supervisor", "team lead", "lead ", "manager", "administrator", "owner"):
        if has("engineering") or is_major("ENGINEERING & TECHNOLOGY") and has("product manager", "engineering manager", "technical product manager"):
            return {"small": "Engineering", "large": "Technology & Engineering"}
        return {"small": "Leadership (General)", "large": "Business & Finance"}

    if has("analyst", "associate", "specialist", "coordinator", "representative", "intern", "assistant"):
        if has("tax", "account", "audit", "assurance"):
            return {"small": "Accounting & Audit", "large": "Business & Finance"}
        if has("financial", "finance", "investment", "credit", "treasury", "actuarial"):
            return {"small": "Finance & Investment", "large": "Business & Finance"}
        if has("sales", "marketing", "communications", "campaign", "brand", "business development"):
            return {"small": "Sales & Marketing", "large": "Business & Finance"}
        if has("system", "it ", "infrastructure", "support", "technical"):
            return {"small": "IT & Infrastructure", "large": "Technology & Engineering"}
        if has("software", "data", "cyber", "machine learning", "developer"):
            return {"small": "Software & Data", "large": "Technology & Engineering"}
        if has("operations", "project", "program", "sourcing", "supply chain", "procurement"):
            return {"small": "Management & Operations", "large": "Business & Finance"}
        if has("research", "lab", "clinical", "health"):
            return {"small": "Research & Science", "large": "Healthcare & Science"}
        if is_major("ENGINEERING & TECHNOLOGY"):
            return {"small": "Engineering", "large": "Technology & Engineering"}
        if is_major("NATURAL & HEALTH SCIENCES"):
            return {"small": "Research & Science", "large": "Healthcare & Science"}
        if is_major("EDUCATION & SOCIAL SERVICES"):
            return {"small": "Education", "large": "Education & Service"}
        if is_major("SOCIAL SCIENCES & HUMANITIES"):
            return {"small": "Social Service", "large": "Education & Service"}
        if is_major("BUSINESS & MANAGEMENT"):
            return {"small": "Management & Operations", "large": "Business & Finance"}

    return {"small": "Unclassified Jobs", "large": "Unclassified"}


def write_csv(path: Path, rows: list[list[str]], header: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.writer(file_obj)
        writer.writerow(header)
        writer.writerows(rows)


def clean_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild the major/job cluster lookup from raw source files.")
    parser.add_argument("--raw-data", type=Path, default=DEFAULT_RAW_DATA)
    parser.add_argument("--major-clusters", type=Path, default=DEFAULT_MAJOR_CLUSTERS)
    parser.add_argument("--career-clusters", type=Path, default=DEFAULT_CAREER_CLUSTERS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    major_map = load_major_cluster_map(args.major_clusters)
    career_exact_map, career_normalized_map = load_career_cluster_map(args.career_clusters)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    full_rows: list[list[str]] = []
    filtered_rows: list[list[str]] = []
    unmatched_majors: Counter[str] = Counter()
    unmatched_jobs: Counter[str] = Counter()
    major_match_modes: Counter[str] = Counter()
    job_match_modes: Counter[str] = Counter()

    if args.raw_data.suffix.lower() in {".xlsx", ".xls"}:
        source_rows = pd.read_excel(args.raw_data).to_dict(orient="records")
    else:
        with args.raw_data.open(encoding="utf-8", newline="") as file_obj:
            source_rows = list(csv.DictReader(file_obj))

    for row in source_rows:
            major = clean_text(row.get("Program Name/Major", ""))
            job_title = clean_text(row.get("Job Title", ""))

            major_cluster = lookup_major(major, major_map)
            job_cluster, job_match_mode = lookup_job(job_title, career_exact_map, career_normalized_map)

            if job_match_mode == "unclassified":
                heuristic_cluster = classify_job_by_rules(job_title, major_cluster)
                if heuristic_cluster["small"]:
                    job_cluster = heuristic_cluster
                    job_match_mode = "heuristic"

            if major_cluster["small"]:
                major_match_modes["matched"] += 1
            else:
                major_match_modes["unmatched"] += 1
                unmatched_majors[major] += 1

            job_match_modes[job_match_mode] += 1
            if job_match_mode == "unclassified":
                unmatched_jobs[job_title] += 1

            out_row = [
                major,
                major_cluster["small"],
                major_cluster["large"],
                job_title,
                job_cluster["small"],
                job_cluster["large"],
            ]
            full_rows.append(out_row)

            if all([
                major_cluster["small"],
                major_cluster["large"],
                job_cluster["small"],
                job_cluster["large"],
                job_cluster["large"].lower() != "unclassified",
                job_cluster["small"].lower() != "unclassified jobs",
            ]):
                filtered_rows.append(out_row)

    header = [
        "Major",
        "Small Major Cluster",
        "Large Major Cluster",
        "Job Title",
        "Small Job Title Cluster",
        "Large Job Title Cluster",
    ]
    write_csv(output_dir / "Major_Job_Cluster_Lookup_rebuilt.csv", full_rows, header)
    write_csv(output_dir / "Major_Job_Cluster_Lookup_rebuilt_filtered.csv", filtered_rows, header)

    unmatched_job_rows = [[job, count] for job, count in unmatched_jobs.most_common()]
    write_csv(output_dir / "Unmatched_Job_Titles_Summary.csv", unmatched_job_rows, ["Job Title", "Count"])

    unmatched_major_rows = [[major, count] for major, count in unmatched_majors.most_common()]
    write_csv(output_dir / "Unmatched_Majors_Summary.csv", unmatched_major_rows, ["Major", "Count"])

    summary_rows = [
        ["raw_rows", str(len(full_rows))],
        ["filtered_rows", str(len(filtered_rows))],
        ["major_matched_rows", str(major_match_modes["matched"])],
        ["major_unmatched_rows", str(major_match_modes["unmatched"])],
        ["job_exact_match_rows", str(job_match_modes["exact"])],
        ["job_normalized_match_rows", str(job_match_modes["normalized"])],
        ["job_heuristic_match_rows", str(job_match_modes["heuristic"])],
        ["job_blank_rows", str(job_match_modes["blank"])],
        ["job_unclassified_rows", str(job_match_modes["unclassified"])],
        ["distinct_unmatched_job_titles", str(len(unmatched_jobs))],
        ["distinct_unmatched_majors", str(len(unmatched_majors))],
    ]
    write_csv(output_dir / "Rebuild_Summary.csv", summary_rows, ["Metric", "Value"])

    print(f"Raw rows: {len(full_rows)}")
    print(f"Filtered rows: {len(filtered_rows)}")
    print(f"Major matched rows: {major_match_modes['matched']}")
    print(f"Major unmatched rows: {major_match_modes['unmatched']}")
    print(f"Job exact match rows: {job_match_modes['exact']}")
    print(f"Job normalized match rows: {job_match_modes['normalized']}")
    print(f"Job heuristic match rows: {job_match_modes['heuristic']}")
    print(f"Job blank rows: {job_match_modes['blank']}")
    print(f"Job unclassified rows: {job_match_modes['unclassified']}")
    print(f"Distinct unmatched job titles: {len(unmatched_jobs)}")
    print(f"Output dir: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
