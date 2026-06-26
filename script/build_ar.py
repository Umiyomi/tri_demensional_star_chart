import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

AR_SPAN_METERS = 0.25


def load_chart_module(script_dir: Path):
    spec = importlib.util.spec_from_file_location(
        "chart3d", script_dir / "3d_star_chart.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["chart3d"] = module
    spec.loader.exec_module(module)
    return module


def pc_to_ar(x_pc: float, y_pc: float, z_pc: float, scale: float) -> dict:
    return {
        "x": float(x_pc * scale),
        "y": float(z_pc * scale),
        "z": float(-y_pc * scale),
    }


def build_ar_data(df, edges, span_meters: float = AR_SPAN_METERS) -> dict:
    max_distance = float(df["distance_pc"].max())
    scale = span_meters / max_distance

    stars = []
    positions = {}
    for _, row in df.iterrows():
        pos = pc_to_ar(row["x_pc"], row["y_pc"], row["z_pc"], scale)
        star = {"name": row["name"], **pos}
        stars.append(star)
        positions[row["name"]] = pos

    edge_segments = []
    for a, b in edges:
        if a not in positions or b not in positions:
            print(f"[WARN] Unknown star in edges: {a} -> {b}")
            continue
        pa, pb = positions[a], positions[b]
        edge_segments.append({
            "a": a,
            "b": b,
            "ax": pa["x"], "ay": pa["y"], "az": pa["z"],
            "bx": pb["x"], "by": pb["y"], "bz": pb["z"],
        })

    return {
        "scale_pc": scale,
        "span_meters": span_meters,
        "stars": stars,
        "edges": edge_segments,
    }


def main():
    project_root = Path(__file__).resolve().parent.parent
    chart = load_chart_module(project_root / "script")

    df = pd.read_csv(project_root / "data" / "virgo_stars.csv")
    df = chart.add_cartesian_coords(df)
    edges = chart.load_edges(project_root / "data" / "virgo_edges.json")

    payload = build_ar_data(df, edges)
    output_path = project_root / "docs" / "ar" / "virgo.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Wrote: {output_path}")
    print(f"  stars: {len(payload['stars'])}")
    print(f"  edges: {len(payload['edges'])}")


if __name__ == "__main__":
    main()
