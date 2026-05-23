"""
generate_circos_data_incoming_grad_groups.py
--------------------------------------------
Builds an incoming-major -> graduating-major Circos render using the
newest grouped mapping from:

  circos_refresh_v2/site/incomingmajor_fall2022_csv/major.csv

Input files
-----------
  circos_refresh_v2/site/incomingmajor_fall2022_csv/Class_of_2026_CPF_vs_SP26.csv
  circos_refresh_v2/site/incomingmajor_fall2022_csv/major.csv

Output directory
----------------
  circos_refresh_v2/outputs/renders/incoming_grad_grouped_latest/
"""

from __future__ import annotations

import csv
import math
import os
from collections import defaultdict
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BASE_DIR.parent
CLASS_CSV = BASE_DIR / "site" / "incomingmajor_fall2022_csv" / "Class_of_2026_CPF_vs_SP26.csv"
GROUP_CSV = BASE_DIR / "site" / "incomingmajor_fall2022_csv" / "major.csv"
OUTPUT_DIR = BASE_DIR / "outputs" / "renders" / "incoming_grad_grouped_latest"
CIRCOS_ROOT = Path(os.environ.get("CIRCOS_ROOT", "C:/Users/hoang/circos"))

VISUAL_GROUP_ORDER = [
    "Acct/Fin/Ops",
    "Mgmt",
    "OtherBusiness",
    "Mktg",
    "Writing/Comm",
    "Humanities",
    "Lang",
    "Social",
    "Other",
    "EDUC",
    "COH",
    "Science",
    "Engineering",
    "CS/DS/DA/Math/Stat",
]

DISPLAY_LABELS = {
    "Acct/Fin/Ops": "Accounting/Finance/Ops",
    "COH": "Health Sciences",
    "CS/DS/DA/Math/Stat": "Computing/Data/Math/Stats",
    "EDUC": "Education",
    "Engineering": "Engineering",
    "Humanities": "Humanities",
    "Lang": "Languages",
    "Mgmt": "Management",
    "Mktg": "Marketing",
    "Other": "Pre-Professional/Undeclared",
    "OtherBusiness": "Specialized Business",
    "Science": "Natural Sciences",
    "Social": "Social Sciences",
    "Writing/Comm": "Writing/Communication",
}

FAMILY_ORDER = [
    "BUSINESS & MANAGEMENT",
    "HUMANITIES & COMMUNICATION",
    "SOCIAL SCIENCES & EDUCATION",
    "ENGINEERING, SCIENCE & TECHNOLOGY",
]

GROUP_TO_FAMILY = {
    "Engineering": "ENGINEERING, SCIENCE & TECHNOLOGY",
    "CS/DS/DA/Math/Stat": "ENGINEERING, SCIENCE & TECHNOLOGY",
    "COH": "ENGINEERING, SCIENCE & TECHNOLOGY",
    "Science": "ENGINEERING, SCIENCE & TECHNOLOGY",
    "EDUC": "SOCIAL SCIENCES & EDUCATION",
    "Social": "SOCIAL SCIENCES & EDUCATION",
    "Other": "SOCIAL SCIENCES & EDUCATION",
    "Mktg": "HUMANITIES & COMMUNICATION",
    "Writing/Comm": "HUMANITIES & COMMUNICATION",
    "Humanities": "HUMANITIES & COMMUNICATION",
    "Lang": "HUMANITIES & COMMUNICATION",
    "OtherBusiness": "BUSINESS & MANAGEMENT",
    "Mgmt": "BUSINESS & MANAGEMENT",
    "Acct/Fin/Ops": "BUSINESS & MANAGEMENT",
}

FAMILY_COLORS = {
    "HUMANITIES & COMMUNICATION": [
        (122, 86, 151),
        (165, 124, 192),
        (204, 121, 167),
        (227, 176, 214),
    ],
    "BUSINESS & MANAGEMENT": [
        (0, 82, 128),
        (0, 114, 178),
        (86, 180, 233),
        (169, 218, 255),
    ],
    "ENGINEERING, SCIENCE & TECHNOLOGY": [
        (0, 109, 79),
        (0, 158, 115),
        (94, 187, 151),
        (175, 223, 205),
    ],
    "SOCIAL SCIENCES & EDUCATION": [
        (176, 120, 0),
        (230, 159, 0),
        (243, 195, 86),
        (251, 225, 170),
    ],
}

GRAD_GRAY = (185, 185, 185)
RIBBON_ALPHA = 0.995
DEFAULT_SPACING = "0.004r"
EDGE_SPACING = "0.004r"
FAMILY_SPACING = "0.004r"
LINK_BEZIER_RADIUS = "0.15r"
LINK_CREST = "0.5"
FLAT_RIBBONS = "yes"

LEGACY_CODE_ALIASES = {
    # `THEO` appears in the graduating data but the updated major map keeps
    # Theology under code `MTHL` in the Humanities group.
    "THEO": "MTHL",
}


def spacing_differs(a: str, b: str) -> bool:
    return a.strip().lower() != b.strip().lower()


def clean_id(name: str, prefix: str) -> str:
    return prefix + "_" + (
        name.replace(" ", "_")
        .replace("&", "AND")
        .replace(",", "")
        .replace("'", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
        .replace("/", "_")
        .replace("+", "PLUS")
    )


def labelize(name: str) -> str:
    return (
        name.replace(" & ", "-and-")
        .replace(" ", "-")
        .replace("/", "-")
        .replace("+", "plus")
        .replace(",", "")
    )


def display_label(group: str) -> str:
    return DISPLAY_LABELS.get(group, group)


def circle_delta(a: float, b: float, total_length: float) -> float:
    delta = abs(a - b)
    return min(delta, total_length - delta)


def forward_distance(start: float, end: float, total_length: float) -> float:
    return (end - start) % total_length


def include_path(*parts: str) -> str:
    return (CIRCOS_ROOT.joinpath(*parts)).as_posix()


def normalize_code(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def is_real_code(value: object) -> bool:
    code = normalize_code(value)
    return code not in {"", "0", "nan"}


def assign_group_colors() -> dict[str, tuple[int, int, int]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for group in VISUAL_GROUP_ORDER:
        grouped[GROUP_TO_FAMILY[group]].append(group)

    assigned: dict[str, tuple[int, int, int]] = {}
    for family in FAMILY_ORDER:
        groups = grouped.get(family, [])
        palette = FAMILY_COLORS[family]
        for index, group in enumerate(groups):
            assigned[group] = palette[min(index, len(palette) - 1)]
    return assigned


def choose_grad_order(
    flows: dict[str, dict[str, int]],
    grad_totals: dict[str, int],
    inc_order: list[str],
) -> list[str]:
    inc_index = {group: index for index, group in enumerate(inc_order)}
    max_index = len(inc_order) - 1
    weighted_targets = []
    for grad_group, total in grad_totals.items():
        target = sum(
            (max_index - inc_index[inc_group]) * flows[inc_group].get(grad_group, 0)
            for inc_group in inc_order
        ) / total
        weighted_targets.append((target, -total, grad_group))
    weighted_targets.sort()
    return [grad_group for _, _, grad_group in weighted_targets]


def sector_layout(
    grad_order: list[str],
    inc_order: list[str],
    grad_totals: dict[str, int],
    inc_totals: dict[str, int],
) -> tuple[dict[str, tuple[float, float]], dict[str, tuple[float, float]], float]:
    grad_intervals: dict[str, tuple[float, float]] = {}
    inc_intervals: dict[str, tuple[float, float]] = {}
    cursor = 0.0
    items = [("grad", name) for name in grad_order] + [("inc", name) for name in inc_order]
    for kind, name in items:
        length = float(grad_totals[name] if kind == "grad" else inc_totals[name])
        start = cursor
        end = start + length
        if kind == "grad":
            grad_intervals[name] = (start, end)
        else:
            inc_intervals[name] = (start, end)
        cursor = end + 18.0
    return grad_intervals, inc_intervals, cursor


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
            left_side.append((left_distance, order_index[target], target))

    right_side.sort(key=lambda item: (item[0], item[1]))
    left_side.sort(key=lambda item: (-item[0], item[1]))
    return [target for _, _, target in right_side] + [target for _, _, target in left_side]


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


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    students = pd.read_csv(CLASS_CSV, dtype=str).fillna("")
    major = pd.read_csv(GROUP_CSV, dtype=str).fillna("")

    students.columns = [column.strip() for column in students.columns]
    students = students.rename(
        columns={
            "UST ID": "UST_ID",
            "CPF Major Fall 2022": "CPF_MAJOR_LONG",
            "CPF Major Code": "CPF_MAJOR_CODE",
            "Declared Major Spring 2026": "GRAD1",
            "Declared Second Major Spring 2026": "GRAD2",
            "Declared minor Spring 2026": "MINOR1",
            "Declared Minor 2 spring 2026": "MINOR2",
        }
    )

    code_to_group = {
        normalize_code(code): group.strip()
        for code, group in zip(major["majorcode"], major["group"])
        if normalize_code(code) and group.strip()
    }
    students["CPF_MAJOR_CODE"] = students["CPF_MAJOR_CODE"].map(normalize_code)
    students["GRAD1"] = students["GRAD1"].map(normalize_code)
    students["GRAD2"] = students["GRAD2"].map(normalize_code)

    ribbon_rows: list[dict[str, object]] = []
    for _, row in students.iterrows():
        grad1 = row["GRAD1"]
        has_second_major = is_real_code(row["GRAD2"])
        grad2 = row["GRAD2"] if has_second_major else grad1

        base = {
            "UST_ID": row["UST_ID"],
            "CPF_MAJOR_CODE": row["CPF_MAJOR_CODE"],
            "CPF_MAJOR_LONG": row["CPF_MAJOR_LONG"],
            "GRAD_MAJOR_1_CODE": grad1,
            "GRAD_MAJOR_2_CODE": row["GRAD2"] if has_second_major else "",
            "IS_DOUBLE_MAJOR": has_second_major,
            "MINOR1": normalize_code(row.get("MINOR1", "")),
            "MINOR2": normalize_code(row.get("MINOR2", "")),
            "WEIGHT": 1,
        }
        ribbon_rows.append({**base, "RIBBON_ROW": 1, "RIBBON_TARGET_CODE": grad1})
        ribbon_rows.append({**base, "RIBBON_ROW": 2, "RIBBON_TARGET_CODE": grad2})

    ribbon = pd.DataFrame(ribbon_rows)
    ribbon["CPF_MAJOR_CODE"] = ribbon["CPF_MAJOR_CODE"].map(normalize_code)
    ribbon["RIBBON_TARGET_CODE"] = ribbon["RIBBON_TARGET_CODE"].map(
        lambda code: LEGACY_CODE_ALIASES.get(normalize_code(code), normalize_code(code))
    )
    ribbon["WEIGHT"] = ribbon["WEIGHT"].astype(int)

    ribbon["inc_group"] = ribbon["CPF_MAJOR_CODE"].map(code_to_group)
    ribbon["grad_group"] = ribbon["RIBBON_TARGET_CODE"].map(code_to_group)

    unmapped_incoming = sorted(ribbon.loc[ribbon["inc_group"].isna(), "CPF_MAJOR_CODE"].dropna().unique().tolist())
    unmapped_grad = sorted(ribbon.loc[ribbon["grad_group"].isna(), "RIBBON_TARGET_CODE"].dropna().unique().tolist())
    if unmapped_incoming or unmapped_grad:
        raise ValueError(
            f"Unmapped grouped codes detected. Incoming={unmapped_incoming} Graduating={unmapped_grad}"
        )

    flows: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for _, row in ribbon.iterrows():
        flows[row["inc_group"]][row["grad_group"]] += int(row["WEIGHT"])

    inc_totals = {group: sum(flows[group].values()) for group in flows}
    grad_totals: dict[str, int] = defaultdict(int)
    for incoming_group, targets in flows.items():
        for grad_group, count in targets.items():
            grad_totals[grad_group] += count
            if grad_group not in GROUP_TO_FAMILY:
                raise ValueError(f"Missing family mapping for graduating group '{grad_group}'")

    missing_incoming_order = sorted(group for group in inc_totals if group not in VISUAL_GROUP_ORDER)
    missing_graduating_order = sorted(group for group in grad_totals if group not in VISUAL_GROUP_ORDER)
    if missing_incoming_order or missing_graduating_order:
        raise ValueError(
            "Groups missing from VISUAL_GROUP_ORDER. "
            f"Incoming={missing_incoming_order} Graduating={missing_graduating_order}"
        )

    grad_order = [group for group in VISUAL_GROUP_ORDER if group in grad_totals]
    inc_order = [group for group in reversed(VISUAL_GROUP_ORDER) if group in inc_totals]

    inc_ids = {group: clean_id(group, "i") for group in inc_order}
    grad_ids = {group: clean_id(group, "g") for group in grad_order}
    inc_color_keys = {group: f"ci{index}" for index, group in enumerate(inc_order)}
    inc_colors = assign_group_colors()

    karyotype_lines: list[str] = []
    for group in grad_order:
        karyotype_lines.append(
            f"chr - {grad_ids[group]} {labelize(display_label(group))} 0 {grad_totals[group]} cgrad_gray"
        )
    for group in inc_order:
        karyotype_lines.append(
            f"chr - {inc_ids[group]} {labelize(display_label(group))} 0 {inc_totals[group]} {inc_color_keys[group]}"
        )
    (OUTPUT_DIR / "karyotype.txt").write_text("\n".join(karyotype_lines) + "\n", encoding="utf-8")

    grad_slices: dict[tuple[str, str], tuple[int, int]] = {}
    grad_intervals, inc_intervals, total_length = sector_layout(
        grad_order,
        inc_order,
        grad_totals,
        inc_totals,
    )
    for grad_group in grad_order:
        local_lengths = {inc_group: flows[inc_group][grad_group] for inc_group in inc_order if flows[inc_group][grad_group]}
        oriented = choose_directional_side_order(
            local_lengths,
            grad_intervals[grad_group],
            inc_intervals,
            total_length,
            inc_order,
        )
        for inc_group, slice_range in allocate_local_slices(oriented, local_lengths).items():
            grad_slices[(inc_group, grad_group)] = slice_range

    link_lines: list[str] = []
    inc_pos = {group: inc_totals[group] for group in inc_order}
    for inc_group in inc_order:
        for grad_group in grad_order:
            count = flows[inc_group].get(grad_group, 0)
            if not count:
                continue
            inc_end = inc_pos[inc_group]
            inc_start = inc_end - count
            grad_start, grad_end = grad_slices[(inc_group, grad_group)]
            color_key = inc_color_keys[inc_group]
            link_lines.append(
                f"{inc_ids[inc_group]} {inc_start} {inc_end} {grad_ids[grad_group]} {grad_start} {grad_end} color={color_key}_a"
            )
            inc_pos[inc_group] = inc_start
    (OUTPUT_DIR / "links.txt").write_text("\n".join(link_lines) + "\n", encoding="utf-8")

    color_lines = ["<colors>"]
    for group in inc_order:
        red, green, blue = inc_colors[group]
        color_key = inc_color_keys[group]
        color_lines.append(f"{color_key} = {red},{green},{blue}")
        color_lines.append(f"{color_key}_a = {red},{green},{blue},{RIBBON_ALPHA}")
    gray_red, gray_green, gray_blue = GRAD_GRAY
    color_lines.append(f"cgrad_gray = {gray_red},{gray_green},{gray_blue}")
    color_lines.append("</colors>")
    (OUTPUT_DIR / "colors.conf").write_text("\n".join(color_lines) + "\n", encoding="utf-8")

    pairwise_lines: list[str] = []
    if grad_order and inc_order and spacing_differs(EDGE_SPACING, DEFAULT_SPACING):
        pairwise_lines.append(
            f"    <pairwise {grad_ids[grad_order[-1]]} {inc_ids[inc_order[0]]}>\n"
            f"      spacing = {EDGE_SPACING}\n"
            f"    </pairwise>"
        )
        pairwise_lines.append(
            f"    <pairwise {inc_ids[inc_order[-1]]} {grad_ids[grad_order[0]]}>\n"
            f"      spacing = {EDGE_SPACING}\n"
            f"    </pairwise>"
        )

    previous_family = None
    previous_group = None
    for group in inc_order:
        family = GROUP_TO_FAMILY[group]
        if previous_group and previous_family != family and spacing_differs(FAMILY_SPACING, DEFAULT_SPACING):
            pairwise_lines.append(
                f"    <pairwise {inc_ids[previous_group]} {inc_ids[group]}>\n"
                f"      spacing = {FAMILY_SPACING}\n"
                f"    </pairwise>"
            )
        previous_family = family
        previous_group = group

    conf = f"""karyotype = karyotype.txt
chromosomes_units = 1
chromosomes_display_default = yes

<image>
dir   = .
file  = incoming_grad_grouped_latest.png
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
  stroke_thickness = 2p

  show_label       = yes
  label_font       = default
  label_radius     = 1.05r
  label_size       = 24
  label_parallel   = no
</ideogram>

show_ticks       = no
show_tick_labels = no

<links>
  <link>
    file          = links.txt
    radius        = 0.99r
    bezier_radius = {LINK_BEZIER_RADIUS}
    crest         = {LINK_CREST}
    thickness     = 1
    ribbon        = yes
    flat          = {FLAT_RIBBONS}
  </link>
</links>

<<include colors.conf>>
<<include {include_path("etc", "colors_fonts_patterns.conf")}>>
<<include {include_path("etc", "housekeeping.conf")}>>
"""
    (OUTPUT_DIR / "circos.conf").write_text(conf, encoding="utf-8")

    summary = [
        ["incoming_groups", str(len(inc_order))],
        ["graduating_groups", str(len(grad_order))],
        ["students", str(ribbon["UST_ID"].nunique())],
        ["ribbon_rows", str(len(ribbon))],
        ["connections", str(len(link_lines))],
    ]
    with (OUTPUT_DIR / "summary.csv").open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.writer(file_obj)
        writer.writerow(["Metric", "Value"])
        writer.writerows(summary)

    print(f"Output dir         : {OUTPUT_DIR}")
    print(f"Incoming groups    : {len(inc_order)}")
    for group in inc_order:
        print(f"  [{GROUP_TO_FAMILY[group][:28]:28}] {group}  size={inc_totals[group]}")
    print(f"Graduating groups  : {len(grad_order)}")
    for group in grad_order:
        print(f"  {group}  size={grad_totals[group]}")
    print(f"Students           : {ribbon['UST_ID'].nunique()}")
    print(f"Ribbon rows        : {len(ribbon)}")
    print(f"Link lines         : {len(link_lines)}")


if __name__ == "__main__":
    main()
