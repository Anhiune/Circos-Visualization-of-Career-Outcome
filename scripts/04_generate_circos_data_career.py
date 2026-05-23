import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = BASE_DIR / "outputs" / "lookup" / "Major_Job_Cluster_Lookup_v2_filtered_career_merged.csv"
OUTPUT_DIR = BASE_DIR / "outputs" / "renders" / "order_experiment_v3" / "overall"


MAJOR_ORDER = [
    "Engineering",
    "Computer Science & IT",
    "Biological & Health Sciences",
    "Physical & Environmental Sciences",
    "Finance & Accounting",
    "General Business",
    "Operations & Analytics",
    "Specialized Business",
    "Marketing & Communication",
    "Languages, Arts & Humanities",
    "Education & Social Services",
    "Social Sciences & Humanities",
    "Economics",
]

BIG_ORDER = [
    "ENGINEERING, SCIENCE & TECHNOLOGY",
    "BUSINESS & MANAGEMENT",
    "HUMANITIES & COMMUNICATION",
    "SOCIAL SCIENCES & EDUCATION",
]

BIG_CLUSTER_COLORS = {
    "BUSINESS & MANAGEMENT": [(18, 63, 122), (39, 95, 155), (74, 132, 196), (126, 173, 223)],
    "ENGINEERING, SCIENCE & TECHNOLOGY": [(17, 95, 63), (34, 126, 82), (67, 162, 113), (121, 198, 153)],
    "SOCIAL SCIENCES & EDUCATION": [(176, 93, 5), (209, 120, 9), (234, 154, 29), (248, 191, 85)],
    "HUMANITIES & COMMUNICATION": [(117, 64, 116), (145, 84, 145), (181, 116, 178), (214, 163, 210)],
}

JOB_GRAY = (185, 185, 185)
RIBBON_ALPHA = 0.995
DEFAULT_SPACING = "0.004r"
EDGE_SPACING = "0.004r"
MAJOR_FAMILY_SPACING = "0.004r"
IDEOGRAM_STROKE_THICKNESS = "1p"
SECTOR_GAP_UNITS = 18.0
LINK_RADIUS = "0.99r"
LINK_BEZIER_RADIUS = "0.15r"
LINK_CREST = "0.5"
LABEL_FONT = "bold"
LABEL_RADIUS = "1.02r"
LABEL_SIZE = 36


def clean_id(name: str, prefix: str) -> str:
    return prefix + "_" + (
        name.replace(" ", "_")
        .replace("&", "AND")
        .replace(",", "")
        .replace("'", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
    )


def labelize(name: str) -> str:
    return name.replace(" & ", "-").replace(" ", "-")


def spacing_differs(a: str, b: str) -> bool:
    return a.strip().lower() != b.strip().lower()


def assign_major_colors(major_order: list[str], small_to_large: dict[str, str]) -> dict[str, tuple[int, int, int]]:
    major_set = set(major_order)
    grouped: dict[str, list[str]] = defaultdict(list)
    for major in MAJOR_ORDER:
        if major in major_set:
            grouped[small_to_large[major]].append(major)
    for major in major_order:
        if major not in grouped[small_to_large[major]]:
            grouped[small_to_large[major]].append(major)

    assigned: dict[str, tuple[int, int, int]] = {}
    for big in BIG_ORDER:
        palette = BIG_CLUSTER_COLORS[big]
        for idx, major in enumerate(grouped.get(big, [])):
            assigned[major] = palette[min(idx, len(palette) - 1)]
    return assigned


def choose_job_order(
    flows: dict[str, dict[str, int]],
    job_totals: dict[str, int],
    major_order: list[str],
) -> list[str]:
    major_index = {major: idx for idx, major in enumerate(major_order)}
    max_index = len(major_order) - 1
    weighted_targets = []
    for job, total in job_totals.items():
        # Jobs are drawn before majors; the end of the career arc is closest to
        # the start of the major arc, so use reversed major positions here.
        target = sum((max_index - major_index[major]) * flows[major][job] for major in major_order) / total
        weighted_targets.append((target, -total, job))
    weighted_targets.sort()
    return [job for _, _, job in weighted_targets]


def build_job_order(
    job_totals: dict[str, int],
    requested_order: list[str] | None,
    flows: dict[str, dict[str, int]],
    major_order: list[str],
) -> list[str]:
    if requested_order is None:
        return choose_job_order(flows, job_totals, major_order)

    missing_jobs = [job for job in job_totals if job not in requested_order]
    if missing_jobs:
        raise ValueError(f"Missing careers from --career-order: {missing_jobs}")

    extra_jobs = [job for job in requested_order if job not in job_totals]
    if extra_jobs:
        raise ValueError(f"Unknown careers in --career-order: {extra_jobs}")

    return requested_order


def build_exact_major_order(
    available_majors: list[str],
    requested_order: list[str] | None,
) -> list[str] | None:
    if requested_order is None:
        return None

    missing_majors = [major for major in available_majors if major not in requested_order]
    if missing_majors:
        raise ValueError(f"Missing majors from --major-order: {missing_majors}")

    extra_majors = [major for major in requested_order if major not in available_majors]
    if extra_majors:
        raise ValueError(f"Unknown majors in --major-order: {extra_majors}")

    return requested_order


def circle_delta(a: float, b: float, total_length: float) -> float:
    delta = abs(a - b)
    return min(delta, total_length - delta)


def forward_distance(start: float, end: float, total_length: float) -> float:
    return (end - start) % total_length


def sector_layout(
    job_order: list[str],
    major_order: list[str],
    job_totals: dict[str, int],
    major_sizes: dict[str, int],
) -> tuple[dict[str, tuple[float, float]], dict[str, tuple[float, float]], float]:
    job_intervals: dict[str, tuple[float, float]] = {}
    major_intervals: dict[str, tuple[float, float]] = {}
    cursor = 0.0
    items = [("job", name) for name in job_order] + [("major", name) for name in major_order]
    for kind, name in items:
        length = float(job_totals[name] if kind == "job" else major_sizes[name])
        start = cursor
        end = start + length
        if kind == "job":
            job_intervals[name] = (start, end)
        else:
            major_intervals[name] = (start, end)
        cursor = end + SECTOR_GAP_UNITS
    return job_intervals, major_intervals, cursor


def choose_local_orientation(
    local_lengths: dict[str, int],
    sector_interval: tuple[float, float],
    target_intervals: dict[str, tuple[float, float]],
    total_length: float,
    target_order: list[str],
) -> list[str]:
    connected = [name for name in target_order if local_lengths.get(name, 0)]
    if len(connected) <= 1:
        return connected

    best_order = connected
    best_score = None
    for candidate in (connected, list(reversed(connected))):
        cursor = 0.0
        score = 0.0
        for target in candidate:
            length = float(local_lengths[target])
            start = cursor
            end = start + length
            local_center = sector_interval[0] + ((start + end) / 2.0)
            target_start, target_end = target_intervals[target]
            target_center = (target_start + target_end) / 2.0
            score += float(local_lengths[target]) * circle_delta(local_center, target_center, total_length)
            cursor = end
        if best_score is None or score < best_score:
            best_order = list(candidate)
            best_score = score
    return best_order


def choose_directional_side_order(
    local_lengths: dict[str, int],
    sector_interval: tuple[float, float],
    target_intervals: dict[str, tuple[float, float]],
    total_length: float,
    target_order: list[str],
) -> list[str]:
    connected = [name for name in target_order if local_lengths.get(name, 0)]
    if len(connected) <= 1:
        return connected

    order_index = {name: idx for idx, name in enumerate(target_order)}
    first_sector = math.isclose(sector_interval[0], 0.0, abs_tol=1e-9)
    if first_sector:
        # This arc starts on the seam next to the last major in target_order,
        # so local 0 should walk backward through the major order.
        return [target for target in reversed(target_order) if local_lengths.get(target, 0)]

    sector_center = (sector_interval[0] + sector_interval[1]) / 2.0

    right_side: list[tuple[float, int, str]] = []
    left_side: list[tuple[float, int, str]] = []
    for target in connected:
        target_start, target_end = target_intervals[target]
        target_center = (target_start + target_end) / 2.0
        left_distance = forward_distance(sector_center, target_center, total_length)
        right_distance = forward_distance(target_center, sector_center, total_length)

        if left_distance < right_distance:
            left_side.append((left_distance, order_index[target], target))
        elif right_distance < left_distance:
            right_side.append((right_distance, order_index[target], target))
        else:
            # Exact ties are rare; bias toward preserving the existing target order.
            left_side.append((left_distance, order_index[target], target))

    # Most career arcs run visually from right edge (local 0) to left edge (local max).
    # Put right-side majors first so they occupy the right edge, and left-side majors
    # last so the nearest-left majors can land on the far-left edge.
    right_side.sort(key=lambda item: (item[0], item[1]))
    left_side.sort(key=lambda item: (-item[0], item[1]))
    return [target for _, _, target in right_side] + [target for _, _, target in left_side]


def allocate_local_slices(order: list[str], local_lengths: dict[str, int]) -> dict[str, tuple[int, int]]:
    slices: dict[str, tuple[int, int]] = {}
    cursor = 0
    for name in order:
        length = int(local_lengths[name])
        start = cursor
        end = start + length
        slices[name] = (start, end)
        cursor = end
    return slices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the ordered Circos overall chart data.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory where Circos input/output files should be written.",
    )
    parser.add_argument(
        "--major-family-order",
        nargs="+",
        default=BIG_ORDER,
        help="Large major family order to use when rebuilding the major arc order.",
    )
    parser.add_argument(
        "--career-order",
        nargs="+",
        default=None,
        help="Optional fixed career order to preserve while rebuilding the layout.",
    )
    parser.add_argument(
        "--major-order",
        nargs="+",
        default=None,
        help="Optional exact major order to use instead of deriving order from the major family layout.",
    )
    parser.add_argument(
        "--image-filename",
        default="major_job_circos_v3_ordered.png",
        help="PNG/SVG basename written into the Circos config.",
    )
    parser.add_argument(
        "--link-radius",
        default=LINK_RADIUS,
        help="Link start radius used in the Circos config.",
    )
    parser.add_argument(
        "--link-bezier-radius",
        default=LINK_BEZIER_RADIUS,
        help="Bezier radius used to shape the ribbon pinch toward the middle.",
    )
    parser.add_argument(
        "--link-crest",
        default=LINK_CREST,
        help="Crest factor used to shape the ribbon body between the edge and the bezier midpoint.",
    )
    parser.add_argument(
        "--layout-filename",
        default="layout_order_v3.csv",
        help="CSV filename for the exported major/career layout order.",
    )
    parser.add_argument(
        "--circos-root",
        default="__CIRCOS_ROOT__",
        help="Circos root path used in the generated config include statements.",
    )
    parser.add_argument(
        "--career-nearest-edge",
        action="store_true",
        help="Allocate slices within each career arc toward the nearest side of the major arc order.",
    )
    parser.add_argument(
        "--career-directional-sides",
        action="store_true",
        help="Allocate career-side slices so majors on the left of a career land on the left edge and majors on the right land on the right edge.",
    )
    return parser.parse_args()


def build_major_order(
    base_major_order: list[str],
    small_to_large: dict[str, str],
    family_order: list[str],
) -> list[str]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for major in base_major_order:
        grouped[small_to_large[major]].append(major)

    missing_families = [family for family in grouped if family not in family_order]
    if missing_families:
        raise ValueError(f"Missing families from --major-family-order: {missing_families}")

    extra_families = [family for family in family_order if family not in grouped]
    if extra_families:
        raise ValueError(f"Unknown families in --major-family-order: {extra_families}")

    major_order: list[str] = []
    for family in family_order:
        major_order.extend(grouped[family])
    return major_order


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(INPUT_CSV.open(encoding="utf-8")))

    flows = defaultdict(lambda: defaultdict(int))
    small_to_large: dict[str, str] = {}
    for row in rows:
        major = row["Small Major Cluster"].strip()
        job = row["Large Job Title Cluster"].strip()
        flows[major][job] += 1
        small_to_large[major] = row["Large Major Cluster"].strip()

    missing_majors = [major for major in flows if major not in MAJOR_ORDER]
    if missing_majors:
        raise ValueError(f"Missing majors from MAJOR_ORDER: {missing_majors}")

    major_order = build_exact_major_order(MAJOR_ORDER, args.major_order)
    if major_order is None:
        major_order = build_major_order(MAJOR_ORDER, small_to_large, args.major_family_order)

    job_totals = defaultdict(int)
    for major in major_order:
        for job, count in flows[major].items():
            job_totals[job] += count
    job_order = build_job_order(job_totals, args.career_order, flows, major_order)

    major_sizes = {major: sum(flows[major].values()) for major in major_order}
    major_ids = {major: clean_id(major, "m") for major in major_order}
    job_ids = {job: clean_id(job, "j") for job in job_order}
    major_ckeys = {major: f"cm{i}" for i, major in enumerate(major_order)}
    major_colors = assign_major_colors(major_order, small_to_large)

    karyotype_lines = []
    for job in job_order:
        karyotype_lines.append(f"chr - {job_ids[job]} {labelize(job)} 0 {job_totals[job]} cjob_gray")
    for major in major_order:
        karyotype_lines.append(
            f"chr - {major_ids[major]} {labelize(major)} 0 {major_sizes[major]} {major_ckeys[major]}"
        )
    (output_dir / "karyotype.txt").write_text("\n".join(karyotype_lines) + "\n", encoding="utf-8")

    major_pos = {major: major_sizes[major] for major in major_order}
    job_pos = {job: 0 for job in job_order}
    job_slices: dict[tuple[str, str], tuple[int, int]] = {}
    if args.career_nearest_edge or args.career_directional_sides:
        job_intervals, major_intervals, total_length = sector_layout(
            job_order,
            major_order,
            job_totals,
            major_sizes,
        )
        for job in job_order:
            local_lengths = {major: flows[major][job] for major in major_order if flows[major][job]}
            if args.career_directional_sides:
                oriented = choose_directional_side_order(
                    local_lengths,
                    job_intervals[job],
                    major_intervals,
                    total_length,
                    major_order,
                )
            else:
                oriented = choose_local_orientation(
                    local_lengths,
                    job_intervals[job],
                    major_intervals,
                    total_length,
                    major_order,
                )
            for major, slice_range in allocate_local_slices(oriented, local_lengths).items():
                job_slices[(major, job)] = slice_range
    link_lines = []
    for major in major_order:
        for job in job_order:
            count = flows[major][job]
            if not count:
                continue
            me = major_pos[major]
            ms = me - count
            if args.career_nearest_edge or args.career_directional_sides:
                js, je = job_slices[(major, job)]
            else:
                js = job_pos[job]
                je = js + count
            link_lines.append(f"{major_ids[major]} {ms} {me} {job_ids[job]} {js} {je} color={major_ckeys[major]}_a")
            major_pos[major] = ms
            if not args.career_nearest_edge and not args.career_directional_sides:
                job_pos[job] = je
    (output_dir / "links.txt").write_text("\n".join(link_lines) + "\n", encoding="utf-8")

    color_lines = ["<colors>"]
    for major in major_order:
        r, g, b = major_colors[major]
        ckey = major_ckeys[major]
        color_lines.append(f"{ckey} = {r},{g},{b}")
        color_lines.append(f"{ckey}_a = {r},{g},{b},{RIBBON_ALPHA}")
    gr, gg, gb = JOB_GRAY
    color_lines.append(f"cjob_gray = {gr},{gg},{gb}")
    color_lines.append("</colors>")
    (output_dir / "colors.conf").write_text("\n".join(color_lines) + "\n", encoding="utf-8")

    pairwise_lines = []
    if spacing_differs(EDGE_SPACING, DEFAULT_SPACING):
        pairwise_lines.extend([
            f"""    <pairwise {job_ids[job_order[-1]]} {major_ids[major_order[0]]}>
      spacing = {EDGE_SPACING}
    </pairwise>""",
            f"""    <pairwise {major_ids[major_order[-1]]} {job_ids[job_order[0]]}>
      spacing = {EDGE_SPACING}
    </pairwise>""",
        ])

    previous_big = None
    for index, major in enumerate(major_order):
        big = small_to_large[major]
        if previous_big is not None and big != previous_big and spacing_differs(MAJOR_FAMILY_SPACING, DEFAULT_SPACING):
            prev_major = major_order[index - 1]
            pairwise_lines.append(
                f"""    <pairwise {major_ids[prev_major]} {major_ids[major]}>
      spacing = {MAJOR_FAMILY_SPACING}
    </pairwise>"""
            )
        previous_big = big

    conf = f"""karyotype = karyotype.txt
chromosomes_units = 1
chromosomes_display_default = yes

<image>
dir   = .
file  = {args.image_filename}
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
    default = {DEFAULT_SPACING}
{chr(10).join(pairwise_lines)}
  </spacing>

  radius           = 0.84r
  thickness        = 38p
  fill             = yes
  stroke_color     = white
  stroke_thickness = {IDEOGRAM_STROKE_THICKNESS}

  show_label       = yes
  label_font       = {LABEL_FONT}
  label_radius     = {LABEL_RADIUS}
  label_size       = {LABEL_SIZE}
  label_parallel   = no
</ideogram>

show_ticks       = no
show_tick_labels = no

<links>
  <link>
    file          = links.txt
    radius        = {args.link_radius}
    bezier_radius = {args.link_bezier_radius}
    crest         = {args.link_crest}
    thickness     = 1
    ribbon        = yes
    flat          = yes
  </link>
</links>

<<include colors.conf>>
<<include {args.circos_root}/etc/colors_fonts_patterns.conf>>
<<include {args.circos_root}/etc/housekeeping.conf>>
"""
    (output_dir / "circos.conf").write_text(conf, encoding="utf-8")

    with (output_dir / args.layout_filename).open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.writer(file_obj)
        writer.writerow(["Side", "Position", "Cluster", "Total"])
        for idx, job in enumerate(job_order, start=1):
            writer.writerow(["Career", idx, job, job_totals[job]])
        for idx, major in enumerate(major_order, start=1):
            writer.writerow(["Major", idx, major, major_sizes[major]])

    summary = [
        ["majors", str(len(MAJOR_ORDER))],
        ["major_family_order", " | ".join(args.major_family_order)],
        ["career_nearest_edge", str(args.career_nearest_edge).lower()],
        ["career_directional_sides", str(args.career_directional_sides).lower()],
        ["link_radius", args.link_radius],
        ["link_bezier_radius", args.link_bezier_radius],
        ["link_crest", args.link_crest],
        ["careers", str(len(job_order))],
        ["graduates", str(len(rows))],
        ["connections", str(len(link_lines))],
    ]
    summary[0][1] = str(len(major_order))
    with (output_dir / "summary.csv").open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.writer(file_obj)
        writer.writerow(["Metric", "Value"])
        writer.writerows(summary)

    print(f"Output dir: {output_dir}")
    print("Major family order:", " | ".join(args.major_family_order))
    print("Major order:", " | ".join(major_order))
    print("Career order:", " | ".join(job_order))
    print(f"Link radius: {args.link_radius}")
    print(f"Link bezier radius: {args.link_bezier_radius}")
    print(f"Link crest: {args.link_crest}")
    print(f"Majors: {len(major_order)}")
    print(f"Careers: {len(job_order)}")
    print(f"Graduates: {len(rows)}")
    print(f"Connections: {len(link_lines)}")


if __name__ == "__main__":
    main()
