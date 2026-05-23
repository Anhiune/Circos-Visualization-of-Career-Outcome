import argparse
import copy
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from taper_ribbon_svg import (
    build_circos_link_path,
    embolden_text_labels,
    normalize_label_text,
    normalize_text_labels,
    parse_circos_link_path,
    taper_ribbon_edges,
    wrap_text_labels,
)

SVG_NS = "http://www.w3.org/2000/svg"
NS = {"svg": SVG_NS}
ET.register_namespace("", SVG_NS)

BASE_DIR = Path(__file__).resolve().parents[1]
OVERALL_DIR = BASE_DIR / "outputs" / "renders" / "incoming_grad_grouped_latest"
OVERALL_SVG = OVERALL_DIR / "incoming_grad_grouped_latest.svg"
TAPERED_OVERALL_SVG = OVERALL_DIR / "incoming_grad_grouped_latest_tapered.svg"
OVERALL_PNG = OVERALL_DIR / "incoming_grad_grouped_latest.png"
KARYOTYPE = OVERALL_DIR / "karyotype.txt"
LINKS = OVERALL_DIR / "links.txt"
SITE_ROOT = BASE_DIR / "site" / "incoming_grad_grouped_dashboard_images"
SITE_MAIN = SITE_ROOT / "main.svg"
SITE_MAIN_PNG = SITE_ROOT / "main.png"
SITE_INCOMING = SITE_ROOT / "incoming"
SITE_GRADUATING = SITE_ROOT / "graduating"

# Match the live major-career overall ribbon taper design.
TAPER_MID_SCALE = 0.22
TAPER_PROFILE_POWER = 1.35
TAPER_RESAMPLE_POINTS = 72
TAPER_MIN_WIDTH_PX = 0.0
TAPER_MAX_MID_WIDTH_PX = 0.0
TAPER_STRICT_BODY_WIDTH_PX = 0.0
TAPER_STRICT_BODY_SPAN = 0.0
TAPER_SMOOTH_CURVES = False
TAPER_CURVE_TENSION = 1.0
SPECIAL_LINK_TAPER_RULES: dict[tuple[str, str], dict[str, float]] = {
    # These two grouped ribbons stay visually over-inflated under the shared
    # major-career taper rule because their untapered center spans are unusually wide.
    ("i_Social", "g_Social"): {
        "mid_scale": 0.14,
        "max_mid_width_px": 32.0,
    },
    ("i_Engineering", "g_Acct_Fin_Ops"): {
        "mid_scale": 0.12,
        "max_mid_width_px": 18.0,
    },
}


@dataclass(frozen=True)
class Node:
    kind: str
    node_id: str
    label: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create exact grouped incoming-major and graduating-major SVGs that "
            "reuse the live grouped overall SVG and hide all non-selected ribbons."
        )
    )
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true", help="Generate all incoming and graduating SVGs.")
    selection.add_argument("--incoming", help="Incoming grouped-major label, safe name, or node id.")
    selection.add_argument("--graduating", help="Graduating grouped-major label, safe name, or node id.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for a single --incoming or --graduating selection.",
    )
    return parser.parse_args()


def normalize_name(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


def safe_name_from_node_id(node_id: str) -> str:
    return node_id.split("_", 1)[1]


def style_to_dict(style: str | None) -> dict[str, str]:
    if not style:
        return {}
    result: dict[str, str] = {}
    for chunk in style.split(";"):
        if ":" not in chunk:
            continue
        key, value = chunk.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def dict_to_style(style_dict: dict[str, str]) -> str:
    return ";".join(f"{key}:{value}" for key, value in style_dict.items())


def load_nodes() -> list[Node]:
    nodes: list[Node] = []
    for line in KARYOTYPE.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) < 4 or parts[0] != "chr":
            continue
        node_id = parts[2]
        if node_id.startswith("i_"):
            kind = "incoming"
        elif node_id.startswith("g_"):
            kind = "graduating"
        else:
            continue
        label = normalize_label_text(parts[3])
        nodes.append(Node(kind=kind, node_id=node_id, label=label))
    if not nodes:
        raise ValueError("Could not load any grouped incoming/graduating nodes from karyotype.txt.")
    return nodes


def resolve_node(nodes: list[Node], kind: str, query: str) -> Node:
    normalized_query = normalize_name(query)
    matches = [
        node
        for node in nodes
        if node.kind == kind
        and normalized_query
        in {
            normalize_name(node.label),
            normalize_name(node.node_id),
            normalize_name(safe_name_from_node_id(node.node_id)),
        }
    ]
    if not matches:
        available = ", ".join(sorted(node.label for node in nodes if node.kind == kind))
        raise ValueError(f"Unknown {kind} grouped-major '{query}'. Available options: {available}")
    if len(matches) > 1:
        options = ", ".join(sorted(node.label for node in matches))
        raise ValueError(f"Ambiguous {kind} grouped-major '{query}'. Matches: {options}")
    return matches[0]


def load_link_pairs() -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in LINKS.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) < 4:
            raise ValueError(f"Unexpected links.txt row: {line}")
        pairs.append((parts[0], parts[3]))
    if not pairs:
        raise ValueError("No link pairs were found in grouped links.txt.")
    return pairs


def selected_link_indices(node: Node, link_pairs: list[tuple[str, str]]) -> set[int]:
    if node.kind == "incoming":
        return {index for index, (source_id, _target_id) in enumerate(link_pairs) if source_id == node.node_id}
    return {index for index, (_source_id, target_id) in enumerate(link_pairs) if target_id == node.node_id}


def hide_unselected_ribbons(root: ET.Element, keep_indices: set[int]) -> None:
    track = root.find(".//svg:g[@id='track_0']", NS)
    if track is None:
        raise ValueError("Could not find track_0 in grouped incoming_grad SVG.")
    paths = track.findall("svg:path", NS)
    for index, path in enumerate(paths):
        if index not in keep_indices:
            style_dict = style_to_dict(path.get("style"))
            style_dict["display"] = "none"
            path.set("style", dict_to_style(style_dict))


def output_path_for_node(node: Node) -> Path:
    filename = f"{safe_name_from_node_id(node.node_id)}.svg"
    if node.kind == "incoming":
        return SITE_INCOMING / filename
    return SITE_GRADUATING / filename


def write_focus_svg(base_root: ET.Element, node: Node, link_pairs: list[tuple[str, str]], output_path: Path) -> None:
    keep_indices = selected_link_indices(node, link_pairs)
    if not keep_indices:
        raise ValueError(f"No ribbons found for {node.kind} grouped-major '{node.label}'")
    output_root = copy.deepcopy(base_root)
    hide_unselected_ribbons(output_root, keep_indices)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(output_root).write(output_path, encoding="utf-8", xml_declaration=True)


def taper_grouped_ribbons(base_root: ET.Element, link_pairs: list[tuple[str, str]]) -> ET.Element:
    output_root = copy.deepcopy(base_root)
    track = output_root.find(".//svg:g[@id='track_0']", NS)
    if track is None:
        raise ValueError("Could not find track_0 in grouped incoming_grad SVG.")

    paths = track.findall("svg:path", NS)
    if len(paths) != len(link_pairs):
        raise ValueError(
            f"Ribbon/link mismatch during grouped taper: SVG has {len(paths)} paths but links.txt has {len(link_pairs)} rows."
        )

    for index, path in enumerate(paths):
        d = path.get("d")
        if not d:
            continue
        source_id, target_id = link_pairs[index]
        taper_rule = SPECIAL_LINK_TAPER_RULES.get((source_id, target_id), {})
        move_point, first_arc, first_edge, second_arc, second_edge = parse_circos_link_path(d)
        tapered_first_edge, tapered_second_edge = taper_ribbon_edges(
            first_edge,
            list(reversed(second_edge)),
            mid_scale=taper_rule.get("mid_scale", TAPER_MID_SCALE),
            profile_power=taper_rule.get("profile_power", TAPER_PROFILE_POWER),
            count=TAPER_RESAMPLE_POINTS,
            min_width_px=taper_rule.get("min_width_px", TAPER_MIN_WIDTH_PX),
            max_mid_width_px=taper_rule.get("max_mid_width_px", TAPER_MAX_MID_WIDTH_PX),
            strict_body_width_px=taper_rule.get("strict_body_width_px", TAPER_STRICT_BODY_WIDTH_PX),
            strict_body_span=taper_rule.get("strict_body_span", TAPER_STRICT_BODY_SPAN),
        )
        path.set(
            "d",
            build_circos_link_path(
                move_point,
                first_arc,
                tapered_first_edge,
                second_arc,
                list(reversed(tapered_second_edge)),
                smooth_curves=TAPER_SMOOTH_CURVES,
                curve_tension=TAPER_CURVE_TENSION,
            ),
        )

    return output_root


def main() -> None:
    args = parse_args()
    tree = ET.parse(OVERALL_SVG)
    root = tree.getroot()
    link_pairs = load_link_pairs()
    tapered_root = taper_grouped_ribbons(root, link_pairs)
    normalized_label_count = normalize_text_labels(tapered_root)
    styled_label_count = embolden_text_labels(tapered_root)
    wrapped_label_count = wrap_text_labels(tapered_root)
    nodes = load_nodes()

    track = tapered_root.find(".//svg:g[@id='track_0']", NS)
    if track is None:
        raise ValueError("Could not find track_0 in grouped incoming_grad SVG.")
    path_count = len(track.findall("svg:path", NS))
    if path_count != len(link_pairs):
        raise ValueError(
            f"Ribbon/link mismatch: SVG has {path_count} paths but links.txt has {len(link_pairs)} rows."
        )

    if args.all:
        SITE_ROOT.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(tapered_root).write(TAPERED_OVERALL_SVG, encoding="utf-8", xml_declaration=True)
        shutil.copy2(TAPERED_OVERALL_SVG, SITE_MAIN)
        if OVERALL_PNG.exists():
            shutil.copy2(OVERALL_PNG, SITE_MAIN_PNG)
        for node in nodes:
            write_focus_svg(tapered_root, node, link_pairs, output_path_for_node(node))
        print(f"Generated incoming grouped majors: {sum(1 for node in nodes if node.kind == 'incoming')}")
        print(f"Generated graduating grouped majors: {sum(1 for node in nodes if node.kind == 'graduating')}")
        print(f"Normalized grouped labels: {normalized_label_count}")
        print(f"Restyled grouped labels: {styled_label_count}")
        print(f"Wrapped grouped labels: {wrapped_label_count}")
        print(f"Wrote tapered overall SVG to: {TAPERED_OVERALL_SVG}")
        print(f"Copied main SVG to: {SITE_MAIN}")
        if OVERALL_PNG.exists():
            print(f"Copied main PNG to: {SITE_MAIN_PNG}")
        return

    kind = "incoming" if args.incoming else "graduating"
    query = args.incoming or args.graduating
    assert query is not None
    node = resolve_node(nodes, kind, query)
    output_path = args.output or output_path_for_node(node)
    write_focus_svg(tapered_root, node, link_pairs, output_path)
    print(f"{node.kind.title()}: {node.label}")
    print(f"Node id: {node.node_id}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
