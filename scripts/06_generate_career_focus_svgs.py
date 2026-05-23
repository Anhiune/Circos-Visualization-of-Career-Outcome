import argparse
import copy
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from taper_ribbon_svg import (
    embolden_text_labels,
    normalize_label_text,
    normalize_text_labels,
    wrap_text_labels,
)


SVG_NS = "http://www.w3.org/2000/svg"
NS = {"svg": SVG_NS}
ET.register_namespace("", SVG_NS)

BASE_DIR = Path(__file__).resolve().parents[1]
OVERALL_SVG = (
    BASE_DIR
    / "outputs"
    / "renders"
    / "order_exp_v3_svg_taper"
    / "overall"
    / "major_job_circos_v3_svg_taper.svg"
)
SOURCE_LAYOUT_DIR = BASE_DIR / "outputs" / "renders" / "order_exp_v3_blue_up_keep_colors" / "overall"
SITE_IMAGE_DIR = BASE_DIR / "site" / "v3_ordered_images"
SITE_MAIN = SITE_IMAGE_DIR / "main.svg"
SITE_MAJOR_DIR = SITE_IMAGE_DIR / "majors"
SITE_CAREER_DIR = SITE_IMAGE_DIR / "careers"


@dataclass(frozen=True)
class Node:
    kind: str
    node_id: str
    label: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create exact single-focus SVGs that keep the overall dashboard "
            "layout and only leave the selected ribbons visible."
        )
    )
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--major",
        help="Major label, safe filename, or node id, for example 'General Business'.",
    )
    selection.add_argument(
        "--career",
        help="Career label, safe filename, or node id, for example 'Management Ops'.",
    )
    selection.add_argument(
        "--all",
        action="store_true",
        help="Generate exact SVGs for every major and career.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Optional output SVG path for a single --major or --career selection. "
            "Defaults to the matching site/v3_ordered_images directory."
        ),
    )
    return parser.parse_args()


def safe_name(name: str) -> str:
    return (
        name.replace(" & ", "_")
        .replace(" ", "_")
        .replace(",", "")
        .replace("'", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
    )


def safe_name_from_node_id(node_id: str) -> str:
    return node_id.split("_", 1)[1].replace("_AND_", "_")


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


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
    for line in (SOURCE_LAYOUT_DIR / "karyotype.txt").read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) < 4 or parts[0] != "chr":
            continue
        node_id = parts[2]
        if not (node_id.startswith("m_") or node_id.startswith("j_")):
            continue
        label = normalize_label_text(parts[3])
        kind = "major" if node_id.startswith("m_") else "career"
        nodes.append(Node(kind=kind, node_id=node_id, label=label))
    if not nodes:
        raise ValueError("Could not load major and career nodes from karyotype.txt.")
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
            normalize_name(safe_name_from_node_id(node.node_id)),
            normalize_name(node.node_id),
        }
    ]
    if not matches:
        available = ", ".join(sorted(node.label for node in nodes if node.kind == kind))
        raise ValueError(f"Unknown {kind} '{query}'. Available {kind}s: {available}")
    if len(matches) > 1:
        options = ", ".join(sorted(node.label for node in matches))
        raise ValueError(f"Ambiguous {kind} '{query}'. Matching options: {options}")
    return matches[0]


def load_links() -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    for line in (SOURCE_LAYOUT_DIR / "links.txt").read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) < 4:
            raise ValueError(f"Unexpected link format: {line}")
        links.append((parts[0], parts[3]))
    if not links:
        raise ValueError("Could not load any links from links.txt.")
    return links


def hide_unselected_ribbons(root: ET.Element, keep_indices: set[int]) -> None:
    track = root.find(".//svg:g[@id='track_0']", NS)
    if track is None:
        raise ValueError("Could not find track_0 ribbon group in overall SVG.")

    paths = track.findall("svg:path", NS)
    for index, path in enumerate(paths):
        if index not in keep_indices:
            style_dict = style_to_dict(path.get("style"))
            style_dict["display"] = "none"
            path.set("style", dict_to_style(style_dict))


def output_path_for_node(node: Node) -> Path:
    filename = f"{safe_name_from_node_id(node.node_id)}.svg"
    if node.kind == "major":
        return SITE_MAJOR_DIR / filename
    return SITE_CAREER_DIR / filename


def selected_link_indices(node_id: str, links: list[tuple[str, str]]) -> set[int]:
    if node_id.startswith("m_"):
        return {index for index, (source_id, _target_id) in enumerate(links) if source_id == node_id}
    return {index for index, (_source_id, target_id) in enumerate(links) if target_id == node_id}


def write_focus_svg(base_root: ET.Element, node: Node, links: list[tuple[str, str]], output_path: Path) -> None:
    keep_indices = selected_link_indices(node.node_id, links)
    if not keep_indices:
        raise ValueError(f"No ribbons found for {node.kind} '{node.label}'")
    output_root = copy.deepcopy(base_root)
    hide_unselected_ribbons(output_root, keep_indices)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(output_root).write(output_path, encoding="utf-8", xml_declaration=True)


def generate_all(base_root: ET.Element, nodes: list[Node], links: list[tuple[str, str]]) -> None:
    for node in nodes:
        write_focus_svg(base_root, node, links, output_path_for_node(node))


def main() -> None:
    args = parse_args()
    tree = ET.parse(OVERALL_SVG)
    root = tree.getroot()
    normalized_label_count = normalize_text_labels(root)
    styled_label_count = embolden_text_labels(root)
    wrapped_label_count = wrap_text_labels(root)
    links = load_links()
    nodes = load_nodes()

    track = root.find(".//svg:g[@id='track_0']", NS)
    if track is None:
        raise ValueError("Could not find track_0 ribbon group in overall SVG.")
    path_count = len(track.findall("svg:path", NS))
    if path_count != len(links):
        raise ValueError(
            f"Ribbon/link count mismatch: overall SVG has {path_count} paths but links.txt has {len(links)} rows."
        )

    if args.all:
        SITE_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(root).write(SITE_MAIN, encoding="utf-8", xml_declaration=True)
        generate_all(root, nodes, links)
        major_count = sum(1 for node in nodes if node.kind == "major")
        career_count = sum(1 for node in nodes if node.kind == "career")
        print(f"Generated majors: {major_count}")
        print(f"Generated careers: {career_count}")
        print(f"Normalized labels: {normalized_label_count}")
        print(f"Restyled labels: {styled_label_count}")
        print(f"Wrapped labels: {wrapped_label_count}")
        print(f"Updated main SVG: {SITE_MAIN}")
        print(f"Output root: {SITE_IMAGE_DIR}")
        return

    kind = "major" if args.major else "career"
    query = args.major or args.career
    assert query is not None
    node = resolve_node(nodes, kind, query)
    output_path = args.output or output_path_for_node(node)
    write_focus_svg(root, node, links, output_path)
    print(f"{node.kind.title()}: {node.label}")
    print(f"Node id: {node.node_id}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
