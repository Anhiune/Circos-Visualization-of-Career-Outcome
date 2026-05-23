import csv
import shutil
from pathlib import Path


BASE_DIR = Path(r"C:\Users\hoang\Documents\project_test\circos_from_csv")
OUTPUT_DIR = Path(r"C:\Users\hoang\Documents\Career_Major_project\dashboard_images")


MAJOR_DIR_NAMES = {
    "Finance & Accounting": "Finance_Accounting",
    "Marketing & Communication": "Marketing_Communication",
    "General Business": "General_Business",
    "Operations & Analytics": "Operations_Analytics",
    "Specialized Business": "Specialized_Business",
    "Economics": "Economics",
    "Engineering Disciplines": "Engineering_Disciplines",
    "Computer Science & IT": "Computer_Science_IT",
    "Biological Sciences": "Biological_Sciences",
    "Health & Wellness": "Health_Wellness",
    "Physical Sciences": "Physical_Sciences",
    "Environmental Sciences": "Environmental_Sciences",
    "Teacher Education": "Teacher_Education",
    "Social Work": "Social_Work",
    "Special Education & Counseling": "Special_Education",
    "Educational Leadership": "Educational_Leadership",
    "Social Sciences": "Social_Sciences",
    "Humanities & Liberal Arts": "Humanities_Liberal_Arts",
    "International Studies": "International_Studies",
    "Communication Studies": "Communication_Studies",
    "Journalism & Media": "Journalism_Media",
    "Creative Writing": "Creative_Writing",
    "Arts & Theology": "Arts_Theology",
    "English & Writing": "English_Writing",
    "Languages": "Languages",
}


CAREER_DIR_NAMES = {
    "Engineering": "Engineering",
    "Finance & Investment": "Finance_Investment",
    "Management & Operations": "Management_Operations",
    "Software & Data": "Software_Data",
    "Sales & Marketing": "Sales_Marketing",
    "Accounting & Audit": "Accounting_Audit",
    "Leadership (General)": "Leadership",
    "Clinical Care": "Clinical_Care",
    "Research & Science": "Research_Science",
    "Education": "Education",
    "IT & Infrastructure": "IT_Infrastructure",
    "Legal & Policy": "Legal_Policy",
    "Social Service": "Social_Service",
}


def clean_id(name: str, prefix: str) -> str:
    return prefix + "_" + (
        name.replace(" ", "_")
        .replace("&", "AND")
        .replace(",", "")
        .replace("'", "")
        .replace("(", "")
        .replace(")", "")
    )


def load_clusters():
    rows = list(csv.DictReader((Path("Major_Job_Cluster_Lookup_Filtered.csv")).open(encoding="utf-8")))
    majors = sorted({
        row["Small Major Cluster"].strip()
        for row in rows
        if row["Small Major Cluster"].strip() in MAJOR_DIR_NAMES
    })
    careers = sorted({
        row["Small Job Title Cluster"].strip()
        for row in rows
        if row["Small Job Title Cluster"].strip() in CAREER_DIR_NAMES
    })
    return majors, careers


def load_base_links():
    return [line.strip() for line in (BASE_DIR / "links.txt").read_text(encoding="utf-8").splitlines() if line.strip()]


def write_focus_dir(out_dir: Path, output_filename: str, selected_links: list[str]):
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BASE_DIR / "karyotype.txt", out_dir / "karyotype.txt")
    shutil.copy2(BASE_DIR / "colors.conf", out_dir / "colors.conf")
    (out_dir / "links.txt").write_text("\n".join(selected_links) + "\n", encoding="utf-8")
    conf = f"""karyotype = karyotype.txt
chromosomes_units = 1
chromosomes_display_default = yes

<image>
dir   = .
file  = {output_filename}
png   = yes
svg   = yes
radius         = 2000p
background     = white
angle_offset   = -90
auto_alpha_colors = yes
auto_alpha_steps  = 5
</image>

<ideogram>
  <spacing>
    default = 0.004r
  </spacing>

  radius           = 0.84r
  thickness        = 38p
  fill             = yes
  stroke_color     = white
  stroke_thickness = 2p

  show_label       = yes
  label_font       = default
  label_radius     = 1.04r
  label_size       = 28
  label_parallel   = no
</ideogram>

show_ticks       = no
show_tick_labels = no

<links>
  <link>
    file          = links.txt
    radius        = 0.99r
    bezier_radius = 0.15r
    thickness     = 1
    ribbon        = yes
    flat          = yes
  </link>
</links>

<<include colors.conf>>
<<include __CIRCOS_ROOT__/etc/colors_fonts_patterns.conf>>
<<include __CIRCOS_ROOT__/etc/housekeeping.conf>>
"""
    (out_dir / "circos.conf").write_text(conf, encoding="utf-8")


def main():
    majors, careers = load_clusters()
    base_links = load_base_links()

    for major in majors:
        major_id = clean_id(major, "m")
        safe_name = MAJOR_DIR_NAMES[major]
        selected = [line for line in base_links if line.split()[0] == major_id]
        write_focus_dir(OUTPUT_DIR / "majors" / safe_name, f"{safe_name}.png", selected)

    for career in careers:
        career_id = clean_id(career, "j")
        safe_name = CAREER_DIR_NAMES[career]
        selected = [line for line in base_links if line.split()[3] == career_id]
        write_focus_dir(OUTPUT_DIR / "careers" / safe_name, f"{safe_name}.png", selected)


if __name__ == "__main__":
    main()
