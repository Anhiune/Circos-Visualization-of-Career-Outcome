import argparse
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
LABEL_FONT_FAMILY = '"Segoe UI", Tahoma, Geneva, Verdana, Arial, sans-serif'
LABEL_TEXT_OVERRIDES = {
    "Pre-Professional-Undeclared": "Pre-Professional Undeclared",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Taper Circos ribbon SVG paths toward their midpoints.")
    parser.add_argument("--input-svg", type=Path, required=True, help="Input SVG produced by Circos.")
    parser.add_argument("--output-svg", type=Path, required=True, help="Output SVG with tapered ribbons.")
    parser.add_argument(
        "--labels-only",
        action="store_true",
        help="Only embolden and wrap SVG text labels; leave ribbon paths unchanged.",
    )
    parser.add_argument(
        "--group-id",
        default="track_0",
        help="SVG group id containing ribbon paths.",
    )
    parser.add_argument(
        "--mid-scale",
        type=float,
        default=0.28,
        help="Relative ribbon width at the midpoint. Smaller means more taper.",
    )
    parser.add_argument(
        "--profile-power",
        type=float,
        default=1.35,
        help="Controls how quickly the ribbon narrows toward the middle.",
    )
    parser.add_argument(
        "--resample-points",
        type=int,
        default=72,
        help="Target point count used when resampling each ribbon edge.",
    )
    parser.add_argument(
        "--min-width-px",
        type=float,
        default=0.0,
        help="Minimum ribbon width to preserve in SVG units after tapering.",
    )
    parser.add_argument(
        "--max-mid-width-px",
        type=float,
        default=0.0,
        help="Optional maximum ribbon width allowed at the midpoint in SVG units.",
    )
    parser.add_argument(
        "--strict-body-width-px",
        type=float,
        default=0.0,
        help="Optional absolute width cap shared by all ribbons through the middle body.",
    )
    parser.add_argument(
        "--strict-body-span",
        type=float,
        default=0.0,
        help="Normalized midpoint span that keeps the shared body-width cap before releasing back toward the ends.",
    )
    parser.add_argument(
        "--smooth-curves",
        action="store_true",
        help="Rebuild tapered ribbon edges as cubic curves instead of straight line chains.",
    )
    parser.add_argument(
        "--hourglass-curves",
        action="store_true",
        help="Rebuild each ribbon as a true hourglass using four cubic Bezier curves total.",
    )
    parser.add_argument(
        "--curve-tension",
        type=float,
        default=1.0,
        help="Spline tension used when smooth-curves is enabled. Lower values are gentler.",
    )
    parser.add_argument(
        "--hourglass-center-pull",
        type=float,
        default=0.34,
        help="How strongly the hourglass waist control points bias inward toward the circle center.",
    )
    parser.add_argument(
        "--hourglass-waist-radius-scale",
        type=float,
        default=0.36,
        help="Places the ribbon waist at this fraction of its original midpoint radius from the circle center.",
    )
    parser.add_argument(
        "--hourglass-end-handle-scale",
        type=float,
        default=0.34,
        help="Handle-length ratio used near arc endpoints for hourglass ribbons.",
    )
    parser.add_argument(
        "--hourglass-control-radius-scale",
        type=float,
        default=0.55,
        help="Places the midpoint-adjacent Bezier controls at this fraction of the original edge midpoint radius.",
    )
    parser.add_argument(
        "--hourglass-waist-handle-scale",
        type=float,
        default=0.52,
        help="Handle-length ratio used on either side of the hourglass waist.",
    )
    parser.add_argument(
        "--color-mid-scale",
        action="append",
        default=[],
        help=(
            "Optional fill-color-specific midpoint scale override in the form "
            "'r,g,b=scale'. May be repeated."
        ),
    )
    parser.add_argument(
        "--preserve-largest-fill",
        action="append",
        default=[],
        help=(
            "Optional fill-color-specific preserve rule in the form "
            "'r,g,b=count'. The largest ribbons for that fill keep their "
            "original untapered path."
        ),
    )
    parser.add_argument(
        "--largest-fill-mid-scale",
        action="append",
        default=[],
        help=(
            "Optional fill-color-specific midpoint scale override for the "
            "single largest ribbon of that fill, in the form 'r,g,b=scale'."
        ),
    )
    return parser.parse_args()


def parse_numbers(text: str) -> list[float]:
    return [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", text)]


def parse_style_declarations(style: str | None) -> dict[str, str]:
    if not style:
        return {}

    declarations: dict[str, str] = {}
    for chunk in style.split(";"):
        if ":" not in chunk:
            continue
        key, value = chunk.split(":", 1)
        declarations[key.strip().lower()] = value.strip()
    return declarations


def serialize_style_declarations(declarations: dict[str, str]) -> str:
    return ";".join(f"{key}:{value}" for key, value in declarations.items())


def flatten_text_content(text: ET.Element) -> str:
    parts: list[str] = []
    if text.text and text.text.strip():
        parts.append(text.text.strip())
    for child in list(text):
        child_text = "".join(chunk.strip() for chunk in child.itertext() if chunk and chunk.strip())
        if child_text:
            parts.append(child_text)
    return " ".join(parts).strip()


def normalize_label_text(label: str) -> str:
    cleaned = " ".join(label.strip().split())
    if not cleaned:
        return cleaned
    if cleaned in LABEL_TEXT_OVERRIDES:
        return LABEL_TEXT_OVERRIDES[cleaned]

    cleaned = cleaned.replace("-and-", " and ").replace("-AND-", " and ")
    cleaned = cleaned.replace("/", " ").replace("-", " ")
    cleaned = cleaned.replace(" + ", " plus ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return LABEL_TEXT_OVERRIDES.get(cleaned, cleaned)


def split_label_into_lines(label: str) -> list[str]:
    cleaned = label.replace(",", " ").replace("/", " ")
    tokens = [token for token in re.split(r"[-\s]+", cleaned) if token]
    if len(tokens) <= 1:
        return [label]

    best_lines: list[str] | None = None
    best_score: tuple[int, int, float, int] | None = None
    token_count = len(tokens)
    for split_idx in range(1, token_count):
        first_line = " ".join(tokens[:split_idx])
        second_line = " ".join(tokens[split_idx:])
        score = (
            max(len(first_line), len(second_line)),
            abs(len(first_line) - len(second_line)),
            abs((split_idx / token_count) - 0.5),
            split_idx,
        )
        if best_score is None or score < best_score:
            best_score = score
            best_lines = [first_line, second_line]

    return best_lines or [label]


def normalize_rgb_key(value: str) -> str:
    numbers = [part.strip() for part in value.split(",")]
    if len(numbers) != 3:
        raise ValueError(f"Expected RGB triplet, got '{value}'")
    parsed = [str(int(component)) for component in numbers]
    return ",".join(parsed)


def extract_fill_color_key(path: ET.Element) -> str | None:
    fill = path.get("fill")
    if fill and fill.lower() != "none":
        match = re.fullmatch(r"rgb\(([^)]+)\)", fill.strip(), flags=re.IGNORECASE)
        if match:
            return normalize_rgb_key(match.group(1))

    style_fill = parse_style_declarations(path.get("style")).get("fill")
    if not style_fill or style_fill.lower() == "none":
        return None

    match = re.fullmatch(r"rgb\(([^)]+)\)", style_fill, flags=re.IGNORECASE)
    if not match:
        return None
    return normalize_rgb_key(match.group(1))


def parse_color_mid_scale_overrides(entries: list[str]) -> dict[str, float]:
    overrides: dict[str, float] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(
                f"Invalid --color-mid-scale value '{entry}'. Expected format 'r,g,b=scale'."
            )
        color_text, scale_text = entry.split("=", 1)
        color_key = normalize_rgb_key(color_text)
        overrides[color_key] = clamp(float(scale_text), 0.0, 1.0)
    return overrides


def parse_preserve_largest_fill(entries: list[str]) -> dict[str, int]:
    rules: dict[str, int] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(
                f"Invalid --preserve-largest-fill value '{entry}'. Expected format 'r,g,b=count'."
            )
        color_text, count_text = entry.split("=", 1)
        color_key = normalize_rgb_key(color_text)
        rules[color_key] = max(0, int(count_text))
    return rules


def parse_largest_fill_mid_scale(entries: list[str]) -> dict[str, float]:
    rules: dict[str, float] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(
                f"Invalid --largest-fill-mid-scale value '{entry}'. Expected format 'r,g,b=scale'."
            )
        color_text, scale_text = entry.split("=", 1)
        color_key = normalize_rgb_key(color_text)
        rules[color_key] = clamp(float(scale_text), 0.0, 1.0)
    return rules


def parse_points(text: str) -> list[tuple[float, float]]:
    values = parse_numbers(text)
    if len(values) % 2 != 0:
        raise ValueError(f"Expected an even number of point coordinates, got {len(values)}")
    return list(zip(values[0::2], values[1::2]))


def format_point(point: tuple[float, float]) -> str:
    return f"{point[0]:.2f},{point[1]:.2f}"


def path_length(points: list[tuple[float, float]]) -> float:
    total = 0.0
    for idx in range(1, len(points)):
        x1, y1 = points[idx - 1]
        x2, y2 = points[idx]
        total += math.hypot(x2 - x1, y2 - y1)
    return total


def interpolate(
    a: tuple[float, float], b: tuple[float, float], t: float
) -> tuple[float, float]:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def add_points(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return (a[0] + b[0], a[1] + b[1])


def subtract_points(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return (a[0] - b[0], a[1] - b[1])


def scale_point(point: tuple[float, float], scalar: float) -> tuple[float, float]:
    return (point[0] * scalar, point[1] * scalar)


def point_distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def normalize(vector: tuple[float, float]) -> tuple[float, float]:
    length = math.hypot(vector[0], vector[1])
    if length == 0:
        return (0.0, 0.0)
    return (vector[0] / length, vector[1] / length)


def dot(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1]


def midpoint(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


def parse_svg_dimension(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", value)
    if not match:
        return None
    return float(match.group(0))


def determine_canvas_center(root: ET.Element) -> tuple[float, float]:
    view_box = root.get("viewBox")
    if view_box:
        values = parse_numbers(view_box)
        if len(values) == 4:
            return (values[0] + values[2] / 2.0, values[1] + values[3] / 2.0)

    width = parse_svg_dimension(root.get("width"))
    height = parse_svg_dimension(root.get("height"))
    if width is not None and height is not None:
        return (width / 2.0, height / 2.0)

    rect = root.find(f".//{{{SVG_NS}}}rect")
    if rect is not None:
        rect_x = parse_svg_dimension(rect.get("x")) or 0.0
        rect_y = parse_svg_dimension(rect.get("y")) or 0.0
        rect_w = parse_svg_dimension(rect.get("width")) or 0.0
        rect_h = parse_svg_dimension(rect.get("height")) or 0.0
        if rect_w > 0 and rect_h > 0:
            return (rect_x + rect_w / 2.0, rect_y + rect_h / 2.0)

    return (0.0, 0.0)


def resample_polyline(points: list[tuple[float, float]], count: int) -> list[tuple[float, float]]:
    if count <= 1 or len(points) <= 1:
        return points[:]

    cumulative = [0.0]
    for idx in range(1, len(points)):
        cumulative.append(cumulative[-1] + math.hypot(points[idx][0] - points[idx - 1][0], points[idx][1] - points[idx - 1][1]))

    total = cumulative[-1]
    if total == 0:
        return [points[0]] * count

    targets = [total * idx / (count - 1) for idx in range(count)]
    result: list[tuple[float, float]] = []
    segment = 1

    for target in targets:
        while segment < len(cumulative) - 1 and cumulative[segment] < target:
            segment += 1
        prev_len = cumulative[segment - 1]
        next_len = cumulative[segment]
        if next_len == prev_len:
            ratio = 0.0
        else:
            ratio = (target - prev_len) / (next_len - prev_len)
        result.append(interpolate(points[segment - 1], points[segment], ratio))

    return result


def taper_scale(t: float, mid_scale: float, profile_power: float) -> float:
    distance_to_center = abs(2.0 * t - 1.0)
    return mid_scale + (1.0 - mid_scale) * (distance_to_center ** profile_power)


def smoothstep01(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def strict_body_cap_width(
    width: float,
    distance_to_center: float,
    strict_body_width_px: float,
    strict_body_span: float,
) -> float:
    if width <= 0 or strict_body_width_px <= 0:
        return width

    shared_width = min(width, strict_body_width_px)
    span = max(0.0, min(1.0, strict_body_span))

    if distance_to_center <= span:
        return shared_width

    if span >= 1.0:
        return shared_width

    release = (distance_to_center - span) / (1.0 - span)
    blend = smoothstep01(release)
    return shared_width + (width - shared_width) * blend


def capped_taper_scale(
    t: float,
    width: float,
    mid_scale: float,
    profile_power: float,
    min_width_px: float,
    max_mid_width_px: float,
    strict_body_width_px: float,
    strict_body_span: float,
) -> float:
    scale = taper_scale(t, mid_scale, profile_power)
    distance_to_center = abs(2.0 * t - 1.0)

    if max_mid_width_px > 0 and width > 0:
        cap_mid_scale = min(1.0, max_mid_width_px / width)
        cap_scale = cap_mid_scale + (1.0 - cap_mid_scale) * (distance_to_center ** profile_power)
        scale = min(scale, cap_scale)

    if min_width_px > 0 and width > 0:
        min_scale = min(1.0, min_width_px / width)
        scale = max(scale, min_scale)

    if strict_body_width_px > 0 and width > 0:
        capped_width = width * scale
        body_cap = strict_body_cap_width(
            width,
            distance_to_center,
            strict_body_width_px,
            strict_body_span,
        )
        scale = min(scale, body_cap / width, capped_width / width)

    return scale


def taper_ribbon_edges(
    edge_a: list[tuple[float, float]],
    edge_b: list[tuple[float, float]],
    mid_scale: float,
    profile_power: float,
    count: int,
    min_width_px: float,
    max_mid_width_px: float,
    strict_body_width_px: float,
    strict_body_span: float,
) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    samples = max(count, len(edge_a), len(edge_b))
    resampled_a = resample_polyline(edge_a, samples)
    resampled_b = resample_polyline(edge_b, samples)

    tapered_a: list[tuple[float, float]] = []
    tapered_b: list[tuple[float, float]] = []

    for idx, (point_a, point_b) in enumerate(zip(resampled_a, resampled_b)):
        t = 0.0 if samples == 1 else idx / (samples - 1)
        center = ((point_a[0] + point_b[0]) / 2.0, (point_a[1] + point_b[1]) / 2.0)
        vector = (point_a[0] - point_b[0], point_a[1] - point_b[1])
        width = math.hypot(vector[0], vector[1])
        scale = capped_taper_scale(
            t,
            width,
            mid_scale,
            profile_power,
            min_width_px,
            max_mid_width_px,
            strict_body_width_px,
            strict_body_span,
        )
        tapered_a.append((center[0] + vector[0] * scale / 2.0, center[1] + vector[1] * scale / 2.0))
        tapered_b.append((center[0] - vector[0] * scale / 2.0, center[1] - vector[1] * scale / 2.0))

    # Keep arc joins locked to the original boundary endpoints.
    tapered_a[0] = edge_a[0]
    tapered_a[-1] = edge_a[-1]
    tapered_b[0] = edge_b[0]
    tapered_b[-1] = edge_b[-1]
    return tapered_a, tapered_b


def parse_circos_link_path(d: str) -> tuple[tuple[float, float], str, list[tuple[float, float]], str, list[tuple[float, float]]]:
    commands = re.findall(r"([MLAZ])([^MLAZ]*)", d)
    if [command for command, _ in commands] != ["M", "A", "L", "A", "L", "Z"]:
        raise ValueError("Unexpected Circos ribbon path format")

    move_point = parse_points(commands[0][1])[0]
    first_arc = " ".join(commands[1][1].split())
    first_edge = parse_points(commands[2][1])
    second_arc = " ".join(commands[3][1].split())
    second_edge = parse_points(commands[4][1])
    return move_point, first_arc, first_edge, second_arc, second_edge


def build_circos_link_path(
    move_point: tuple[float, float],
    first_arc: str,
    first_edge: list[tuple[float, float]],
    second_arc: str,
    second_edge: list[tuple[float, float]],
    smooth_curves: bool,
    curve_tension: float,
) -> str:
    first_edge_str = build_edge_fragment(first_edge, smooth_curves, curve_tension)
    second_edge_str = build_edge_fragment(second_edge, smooth_curves, curve_tension)
    return (
        f"M {format_point(move_point)} "
        f"A {first_arc} "
        f"{first_edge_str} "
        f"A {second_arc} "
        f"{second_edge_str} Z"
    )


def catmull_rom_controls(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    tension: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    factor = tension / 6.0
    c1 = (p1[0] + (p2[0] - p0[0]) * factor, p1[1] + (p2[1] - p0[1]) * factor)
    c2 = (p2[0] - (p3[0] - p1[0]) * factor, p2[1] - (p3[1] - p1[1]) * factor)
    return c1, c2


def build_edge_fragment(
    points: list[tuple[float, float]],
    smooth_curves: bool,
    curve_tension: float,
) -> str:
    if not points:
        return ""

    if not smooth_curves or len(points) == 1:
        return f"L {' '.join(format_point(point) for point in points)}"

    commands = [f"L {format_point(points[0])}"]
    for idx in range(len(points) - 1):
        p0 = points[idx - 1] if idx > 0 else points[idx]
        p1 = points[idx]
        p2 = points[idx + 1]
        p3 = points[idx + 2] if idx + 2 < len(points) else points[idx + 1]
        c1, c2 = catmull_rom_controls(p0, p1, p2, p3, curve_tension)
        commands.append(f"C {format_point(c1)} {format_point(c2)} {format_point(p2)}")

    return " ".join(commands)


def sample_tangent(points: list[tuple[float, float]], index: int, forward: bool) -> tuple[float, float]:
    if len(points) == 1:
        return (0.0, 0.0)

    window = 3
    if forward:
        probe = min(len(points) - 1, index + window)
        tangent = subtract_points(points[probe], points[index])
    else:
        probe = max(0, index - window)
        tangent = subtract_points(points[index], points[probe])
    return normalize(tangent)


def blend_tangent_to_center(
    tangent: tuple[float, float],
    point: tuple[float, float],
    canvas_center: tuple[float, float],
    center_pull: float,
) -> tuple[float, float]:
    inward = normalize(subtract_points(canvas_center, point))
    if inward == (0.0, 0.0):
        return tangent

    blended = normalize(
        add_points(
            scale_point(tangent, 1.0 - center_pull),
            scale_point(inward, center_pull),
        )
    )
    if blended == (0.0, 0.0):
        return tangent
    if dot(blended, tangent) < 0:
        blended = scale_point(blended, -1.0)
    return blended


def choose_cross_direction(
    point_a: tuple[float, float],
    point_b: tuple[float, float],
    tangent_a: tuple[float, float],
    tangent_b: tuple[float, float],
) -> tuple[float, float]:
    across = normalize(subtract_points(point_a, point_b))
    if across != (0.0, 0.0):
        return across

    tangent = normalize(add_points(tangent_a, tangent_b))
    if tangent == (0.0, 0.0):
        return (0.0, 1.0)
    return (-tangent[1], tangent[0])


def hourglass_segments_for_side(
    start_point: tuple[float, float],
    waist_point: tuple[float, float],
    end_point: tuple[float, float],
    start_tangent: tuple[float, float],
    end_tangent: tuple[float, float],
    end_handle_scale: float,
    waist_control_point: tuple[float, float],
) -> tuple[
    tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]],
    tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]],
]:
    first_span = point_distance(start_point, waist_point)
    second_span = point_distance(waist_point, end_point)

    first_outer_len = first_span * end_handle_scale
    second_outer_len = second_span * end_handle_scale

    first_curve = (
        start_point,
        add_points(start_point, scale_point(start_tangent, first_outer_len)),
        waist_control_point,
        waist_point,
    )
    second_curve = (
        waist_point,
        waist_control_point,
        add_points(end_point, scale_point(end_tangent, -second_outer_len)),
        end_point,
    )
    return first_curve, second_curve


def preserve_waist_order(
    candidate_a: tuple[float, float],
    candidate_b: tuple[float, float],
    reference_a: tuple[float, float],
    reference_b: tuple[float, float],
) -> tuple[tuple[float, float], tuple[float, float]]:
    direct_cost = point_distance(candidate_a, reference_a) + point_distance(candidate_b, reference_b)
    swapped_cost = point_distance(candidate_a, reference_b) + point_distance(candidate_b, reference_a)
    if swapped_cost < direct_cost:
        return candidate_b, candidate_a
    return candidate_a, candidate_b


def pull_toward_center(
    point: tuple[float, float],
    canvas_center: tuple[float, float],
    scale: float,
) -> tuple[float, float]:
    # scale=0 -> center, scale=1 -> original point
    return (
        canvas_center[0] + (point[0] - canvas_center[0]) * scale,
        canvas_center[1] + (point[1] - canvas_center[1]) * scale,
    )


def adaptive_ctrl_scale(
    p_start: tuple[float, float],
    p_end: tuple[float, float],
    canvas_center: tuple[float, float],
    waist_radius_scale: float,
) -> float:
    avg_r = (
        point_distance(canvas_center, p_start) + point_distance(canvas_center, p_end)
    ) / 2.0
    chord = point_distance(p_start, p_end)
    separation = 1.0 if avg_r <= 0 else clamp(chord / (2.0 * avg_r), 0.0, 1.0)
    gentle_scale = max(waist_radius_scale, 0.68)
    t = separation ** 0.55
    return gentle_scale + (waist_radius_scale - gentle_scale) * t


def build_hourglass_link_path(
    move_point: tuple[float, float],
    first_arc: str,
    first_edge: list[tuple[float, float]],
    second_arc: str,
    second_edge: list[tuple[float, float]],
    canvas_center: tuple[float, float],
    waist_radius_scale: float,
    **_kwargs: float,
) -> str:
    base_scale = clamp(waist_radius_scale, 0.0, 0.85)

    # Arc A ends at first_edge[0], then the first connector runs to first_edge[-1]
    edge1_start = first_edge[0]
    edge1_end = first_edge[-1]

    # second_edge is already reversed by the caller, so it runs from arc B back to arc A
    edge2_start = second_edge[0]
    edge2_end = second_edge[-1]

    s1 = adaptive_ctrl_scale(edge1_start, edge1_end, canvas_center, base_scale)
    s2 = adaptive_ctrl_scale(edge2_start, edge2_end, canvas_center, base_scale)

    control1_a = pull_toward_center(edge1_start, canvas_center, s1)
    control1_b = pull_toward_center(edge1_end, canvas_center, s1)
    control2_a = pull_toward_center(edge2_start, canvas_center, s2)
    control2_b = pull_toward_center(edge2_end, canvas_center, s2)

    return (
        f"M {format_point(move_point)} "
        f"A {first_arc} "
        f"C {format_point(control1_a)} {format_point(control1_b)} {format_point(edge1_end)} "
        f"A {second_arc} "
        f"C {format_point(control2_a)} {format_point(control2_b)} {format_point(edge2_end)} Z"
    )


def ribbon_end_width_score(d: str) -> float:
    move_point, _first_arc, first_edge, _second_arc, second_edge = parse_circos_link_path(d)
    if not first_edge or not second_edge:
        return 0.0
    return point_distance(move_point, first_edge[0]) + point_distance(first_edge[-1], second_edge[0])


def normalize_text_labels(root: ET.Element) -> int:
    updated = 0
    for text in root.findall(f".//{{{SVG_NS}}}text"):
        normalized = normalize_label_text(flatten_text_content(text))
        if not normalized:
            continue
        if list(text):
            for child in list(text):
                text.remove(child)
        if (text.text or "").strip() != normalized or list(text):
            text.text = normalized
            updated += 1
        else:
            text.text = normalized
    return updated


def embolden_text_labels(root: ET.Element) -> int:
    updated = 0
    for text in root.findall(f".//{{{SVG_NS}}}text"):
        style = parse_style_declarations(text.get("style"))
        style["font-weight"] = "700"
        style["font-family"] = LABEL_FONT_FAMILY
        text.set("style", serialize_style_declarations(style))
        text.set("font-weight", "700")
        text.set("font-family", LABEL_FONT_FAMILY)
        updated += 1
    return updated


def wrap_text_labels(root: ET.Element) -> int:
    updated = 0
    for text in root.findall(f".//{{{SVG_NS}}}text"):
        if list(text):
            continue
        raw_label = (text.text or "").strip()
        lines = split_label_into_lines(raw_label)
        if len(lines) < 2:
            continue

        x_value = text.get("x")
        text.text = None
        first_line = ET.SubElement(
            text,
            f"{{{SVG_NS}}}tspan",
            {"x": x_value or "0", "dy": "-0.34em"},
        )
        first_line.text = lines[0]
        second_line = ET.SubElement(
            text,
            f"{{{SVG_NS}}}tspan",
            {"x": x_value or "0", "dy": "1.02em"},
        )
        second_line.text = lines[1]
        updated += 1
    return updated


def main() -> None:
    args = parse_args()
    color_mid_scale_overrides = parse_color_mid_scale_overrides(args.color_mid_scale)
    preserve_largest_fill_rules = parse_preserve_largest_fill(args.preserve_largest_fill)
    largest_fill_mid_scale_rules = parse_largest_fill_mid_scale(args.largest_fill_mid_scale)
    tree = ET.parse(args.input_svg)
    root = tree.getroot()
    preserve_indices: set[int] = set()
    largest_fill_mid_scale_indices: dict[int, float] = {}
    updated = 0
    if not args.labels_only:
        group = root.find(f".//{{{SVG_NS}}}g[@id='{args.group_id}']")
        if group is None:
            raise ValueError(f"Could not find SVG group with id '{args.group_id}'")
        canvas_center = determine_canvas_center(root)
        path_elements = list(group.findall(f"{{{SVG_NS}}}path"))

        if preserve_largest_fill_rules or largest_fill_mid_scale_rules:
            candidates_by_fill: dict[str, list[tuple[float, int]]] = {}
            for idx, path in enumerate(path_elements):
                d = path.get("d")
                if not d:
                    continue
                fill_color_key = extract_fill_color_key(path)
                if (
                    fill_color_key not in preserve_largest_fill_rules
                    and fill_color_key not in largest_fill_mid_scale_rules
                ):
                    continue
                candidates_by_fill.setdefault(fill_color_key, []).append((ribbon_end_width_score(d), idx))

            for fill_color_key, count in preserve_largest_fill_rules.items():
                candidates = sorted(candidates_by_fill.get(fill_color_key, []), reverse=True)
                preserve_indices.update(idx for _score, idx in candidates[:count])

            for fill_color_key, scale in largest_fill_mid_scale_rules.items():
                candidates = sorted(candidates_by_fill.get(fill_color_key, []), reverse=True)
                if candidates:
                    largest_fill_mid_scale_indices[candidates[0][1]] = scale

        for idx, path in enumerate(path_elements):
            d = path.get("d")
            if not d:
                continue
            if idx in preserve_indices:
                continue
            fill_color_key = extract_fill_color_key(path)
            path_mid_scale = largest_fill_mid_scale_indices.get(
                idx,
                color_mid_scale_overrides.get(fill_color_key, args.mid_scale),
            )
            move_point, first_arc, first_edge, second_arc, second_edge = parse_circos_link_path(d)
            paired_second_edge = list(reversed(second_edge))
            if args.hourglass_curves:
                path.set(
                    "d",
                    build_hourglass_link_path(
                        move_point=move_point,
                        first_arc=first_arc,
                        first_edge=first_edge,
                        second_arc=second_arc,
                        second_edge=paired_second_edge,
                        canvas_center=canvas_center,
                        mid_scale=path_mid_scale,
                        profile_power=args.profile_power,
                        count=args.resample_points,
                        min_width_px=args.min_width_px,
                        max_mid_width_px=args.max_mid_width_px,
                        strict_body_width_px=args.strict_body_width_px,
                        strict_body_span=args.strict_body_span,
                        center_pull=args.hourglass_center_pull,
                        waist_radius_scale=args.hourglass_waist_radius_scale,
                        end_handle_scale=args.hourglass_end_handle_scale,
                        control_radius_scale=args.hourglass_control_radius_scale,
                        waist_handle_scale=args.hourglass_waist_handle_scale,
                    ),
                )
            else:
                tapered_first_edge, tapered_second_edge = taper_ribbon_edges(
                    first_edge,
                    paired_second_edge,
                    mid_scale=path_mid_scale,
                    profile_power=args.profile_power,
                    count=args.resample_points,
                    min_width_px=args.min_width_px,
                    max_mid_width_px=args.max_mid_width_px,
                    strict_body_width_px=args.strict_body_width_px,
                    strict_body_span=args.strict_body_span,
                )
                path.set(
                    "d",
                    build_circos_link_path(
                        move_point,
                        first_arc,
                        tapered_first_edge,
                        second_arc,
                        list(reversed(tapered_second_edge)),
                        smooth_curves=args.smooth_curves,
                        curve_tension=args.curve_tension,
                    ),
                )
            updated += 1

    normalized_label_updates = normalize_text_labels(root)
    label_updates = embolden_text_labels(root)
    wrapped_label_updates = wrap_text_labels(root)
    args.output_svg.parent.mkdir(parents=True, exist_ok=True)
    tree.write(args.output_svg, encoding="utf-8", xml_declaration=True)
    print(f"Updated {updated} ribbon paths")
    print(f"Normalized {normalized_label_updates} text labels")
    print(f"Updated {label_updates} text labels")
    print(f"Wrapped {wrapped_label_updates} text labels")
    print(f"Output SVG: {args.output_svg}")
    print(f"Mid scale: {args.mid_scale}")
    print(f"Profile power: {args.profile_power}")
    print(f"Min width px: {args.min_width_px}")
    print(f"Max mid width px: {args.max_mid_width_px}")
    print(f"Strict body width px: {args.strict_body_width_px}")
    print(f"Strict body span: {args.strict_body_span}")
    print(f"Smooth curves: {args.smooth_curves}")
    print(f"Hourglass curves: {args.hourglass_curves}")
    print(f"Labels only: {args.labels_only}")
    print(f"Curve tension: {args.curve_tension}")
    print(f"Hourglass center pull: {args.hourglass_center_pull}")
    print(f"Hourglass waist radius scale: {args.hourglass_waist_radius_scale}")
    print(f"Hourglass end handle scale: {args.hourglass_end_handle_scale}")
    print(f"Hourglass control radius scale: {args.hourglass_control_radius_scale}")
    print(f"Hourglass waist handle scale: {args.hourglass_waist_handle_scale}")
    if color_mid_scale_overrides:
        print(
            "Color mid-scale overrides: "
            + " | ".join(
                f"rgb({color_key})={scale}" for color_key, scale in color_mid_scale_overrides.items()
            )
        )
    if preserve_largest_fill_rules:
        print(
            "Preserved largest fill rules: "
            + " | ".join(
                f"rgb({color_key})={count}" for color_key, count in preserve_largest_fill_rules.items()
            )
        )
        print(f"Preserved ribbon indices: {sorted(preserve_indices)}")
    if largest_fill_mid_scale_rules:
        print(
            "Largest fill mid-scale rules: "
            + " | ".join(
                f"rgb({color_key})={scale}" for color_key, scale in largest_fill_mid_scale_rules.items()
            )
        )
        print(
            "Largest fill mid-scale indices: "
            + " | ".join(
                f"{idx}={scale}" for idx, scale in sorted(largest_fill_mid_scale_indices.items())
            )
        )


if __name__ == "__main__":
    main()
