import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_stars(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[~df["name"].astype(str).str.strip().str.startswith("#")]
    df = df.dropna(subset=["ra_deg", "dec_deg"])
    df["name"] = df["name"].astype(str).str.strip()
    return df.reset_index(drop=True)


def load_edges(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def mean_radec(df: pd.DataFrame) -> tuple[float, float]:
    ra_rad = np.radians(df["ra_deg"])
    dec_rad = np.radians(df["dec_deg"])
    ra0 = np.degrees(np.arctan2(np.mean(np.sin(ra_rad)), np.mean(np.cos(ra_rad))))
    dec0 = np.degrees(np.mean(dec_rad))
    return ra0, dec0


def project_radec(
    ra_deg: np.ndarray,
    dec_deg: np.ndarray,
    ra0_deg: float,
    dec0_deg: float,
) -> tuple[np.ndarray, np.ndarray]:
    ra = np.radians(ra_deg)
    dec = np.radians(dec_deg)
    ra0 = np.radians(ra0_deg)
    dec0 = np.radians(dec0_deg)

    cos_c = (
        np.sin(dec0) * np.sin(dec)
        + np.cos(dec0) * np.cos(dec) * np.cos(ra - ra0)
    )
    cos_c = np.where(np.abs(cos_c) < 1e-12, 1e-12, cos_c)

    x = np.cos(dec) * np.sin(ra - ra0) / cos_c
    y = (np.cos(dec0) * np.sin(dec) - np.sin(dec0) * np.cos(dec) * np.cos(ra - ra0)) / cos_c
    return x, y


def add_projected_coords(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ra0, dec0 = mean_radec(df)
    x, y = project_radec(df["ra_deg"].to_numpy(), df["dec_deg"].to_numpy(), ra0, dec0)
    df["x"] = x
    df["y"] = y
    return df


def plot_constellation_2d(
    df: pd.DataFrame,
    edges: list,
    output_path: Path,
    show_labels: bool = True,
    show: bool = False,
):
    df = add_projected_coords(df)
    df["x"] = -df["x"]
    positions = {row["name"]: (row["x"], row["y"]) for _, row in df.iterrows()}

    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    for a, b in edges:
        if a not in positions:
            print(f"[WARN] Unknown star in edges: {a}")
            continue
        if b not in positions:
            print(f"[WARN] Unknown star in edges: {b}")
            continue
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        ax.plot([x1, x2], [y1, y2], color="black", alpha=0.35, linewidth=0.8, zorder=1)

    ax.scatter(df["x"], df["y"], s=35, c="black", alpha=0.35, zorder=2)

    if show_labels:
        for _, row in df.iterrows():
            ax.annotate(
                row["name"],
                (row["x"], row["y"]),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=8,
                color="black",
            )

    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    plt.margins(0.15)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"Wrote: {output_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)


def parse_args():
    project_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Virgo 2D constellation chart (B/W PNG)")
    parser.add_argument(
        "--labels",
        dest="show_labels",
        action="store_true",
        default=True,
        help="show star name labels (default)",
    )
    parser.add_argument(
        "--no-labels",
        dest="show_labels",
        action="store_false",
        help="hide star name labels",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=project_root / "output" / "virgo_constellation.png",
        help="output PNG path",
    )
    parser.add_argument(
        "--stars",
        type=Path,
        default=project_root / "data" / "virgo_stars.csv",
        help="star catalog CSV",
    )
    parser.add_argument(
        "--edges",
        type=Path,
        default=project_root / "data" / "virgo_edges.json",
        help="constellation edges JSON",
    )
    parser.add_argument("--show", action="store_true", help="show plot window")
    return parser.parse_args()


def main():
    args = parse_args()
    df = load_stars(args.stars)
    edges = load_edges(args.edges)
    plot_constellation_2d(
        df,
        edges,
        args.output,
        show_labels=args.show_labels,
        show=args.show,
    )


if __name__ == "__main__":
    main()
