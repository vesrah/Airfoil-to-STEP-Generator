import argparse
import requests
import cadquery as cq


def parse_lednicer_or_selig(raw_text):
    """
    Checks if a file is Lednicer or Selig format then
    return a clean, continuous loop from
    Trailing Edge > Upper > Leading Edge > Lower > Trailing Edge.
    """
    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]

    header_name = lines[0]
    data_lines = lines[1:]

    first_data_parts = data_lines[0].split()

    try:
        val1 = float(first_data_parts[0])
        val2 = float(first_data_parts[1])
        is_lednicer = val1 > 1.0 and val2 > 1.0
    except (ValueError, IndexError):
        is_lednicer = False

    points = []

    if is_lednicer:
        print("Parsing native Lednicer format structure...")

        num_upper = int(val1)
        num_lower = int(val2)

        coord_pairs = []
        for line in data_lines[1:]:
            parts = line.split()
            if len(parts) == 2:
                try:
                    coord_pairs.append((float(parts[0]), float(parts[1])))
                except ValueError:
                    continue

        upper_pts = coord_pairs[:num_upper]
        lower_pts = coord_pairs[num_upper:num_upper + num_lower]

        upper_pts.reverse()

        points = upper_pts + lower_pts

    else:
        print("Parsing standard Selig format structure...")

        for line in data_lines:
            parts = line.split()
            if len(parts) == 2:
                try:
                    points.append((float(parts[0]), float(parts[1])))
                except ValueError:
                    continue

    return points


def fetch_fallback_airfoil_tools(airfoil_name):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    target_id = airfoil_name.lower().strip()

    dat_url = f"http://airfoiltools.com/airfoil/seligdatfile?airfoil={target_id}"

    print(f"Connecting directly to AirfoilTools for: {target_id}...")
    response = requests.get(dat_url, headers=headers, timeout=10)

    if (
        response.status_code != 200
        or "html" in response.headers.get("Content-Type", "").lower()
    ):
        if not target_id.endswith("-il"):
            fallback_id = f"{target_id}-il"
            print(
                f"Direct lookup failed. Trying fallback: "
                f"{fallback_id}..."
            )

            dat_url = (
                f"http://airfoiltools.com/airfoil/seligdatfile?airfoil={fallback_id}"
            )

            response = requests.get(dat_url, headers=headers, timeout=10)

        if (
            response.status_code != 200
            or "html" in response.headers.get("Content-Type", "").lower()
        ):
            raise ValueError(
                f"Airfoil identifier '{airfoil_name}' could not be resolved."
            )

    return parse_lednicer_or_selig(response.text)


def generate_parametric_airfoil_step(
    airfoil_name,
    chord_mm,
    span_mm,
    filename=None,
):
    if filename is None:
        filename = f"{airfoil_name}_{int(chord_mm)}x{int(span_mm)}.step"

    print(f"Processing target: {airfoil_name}...")

    try:
        normalized_points = fetch_fallback_airfoil_tools(airfoil_name)
    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"Scaling profile to {chord_mm} mm chord...")

    scaled_points = [
        (x * chord_mm, y * chord_mm, 0.0)
        for x, y in normalized_points
    ]

    if scaled_points[0] != scaled_points[-1]:
        scaled_points.append(scaled_points[0])

    print("Generating 3D geometry via CadQuery...")

    airfoil_profile = (
        cq.Workplane("XY")
        .polyline(scaled_points)
        .close()
        .extrude(span_mm)
    )

    print(f"Exporting STEP file to {filename}...")
    cq.exporters.export(airfoil_profile, filename)

    print("Success!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a STEP model from an AirfoilTools airfoil"
    )

    parser.add_argument(
        "airfoil",
        help="Airfoil name (e.g. clarky-il, naca2412-il)"
    )

    parser.add_argument(
        "chord",
        type=float,
        help="Chord length in mm"
    )

    parser.add_argument(
        "span",
        type=float,
        help="Span/extrusion length in mm"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output STEP filename"
    )

    args = parser.parse_args()

    generate_parametric_airfoil_step(
        airfoil_name=args.airfoil,
        chord_mm=args.chord,
        span_mm=args.span,
        filename=args.output
    )