import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go


CAMERA_ROTATE_SPEED = 0.01
CAMERA_ZOOM_SPEED = 0.35
CAMERA_PAN_SPEED = 0.35


def build_camera_dampening_script(
    rotate_speed=CAMERA_ROTATE_SPEED,
    zoom_speed=CAMERA_ZOOM_SPEED,
    pan_speed=CAMERA_PAN_SPEED,
):
    return f"""
(function dampenCamera(gd) {{
  var rotateSpeed = {rotate_speed};
  var zoomSpeed = {zoom_speed};
  var panSpeed = {pan_speed};

  function apply() {{
    var scene = gd._fullLayout && gd._fullLayout.scene && gd._fullLayout.scene._scene;
    if (!scene || !scene.camera) return false;
    scene.camera.rotateSpeed = rotateSpeed;
    scene.camera.zoomSpeed = zoomSpeed;
    scene.camera.translateSpeed = panSpeed;
    return true;
  }}

  if (!apply()) {{
    gd.on("plotly_afterplot", function once() {{
      if (apply()) gd.removeListener("plotly_afterplot", once);
    }});
  }}
}})(document.getElementById("{{plot_id}}"));
"""


def add_cartesian_coords(df):
    ra = np.radians(df["ra_deg"])
    dec = np.radians(df["dec_deg"])
    d = df["distance_pc"]

    df = df.copy()
    df["x_pc"] = d * np.cos(dec) * np.cos(ra)
    df["y_pc"] = d * np.cos(dec) * np.sin(ra)
    df["z_pc"] = d * np.sin(dec)
    return df


def load_edges(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def add_constellation_lines(fig, df, edges):
    positions = {
        row["name"]: (row["x_pc"], row["y_pc"], row["z_pc"])
        for _, row in df.iterrows()
    }

    xs, ys, zs = [], [], []
    for a, b in edges:
        if a not in positions:
            print(f"[WARN] Unknown star in edges: {a}")
            continue
        if b not in positions:
            print(f"[WARN] Unknown star in edges: {b}")
            continue
        ax, ay, az = positions[a]
        bx, by, bz = positions[b]
        xs.extend([ax, bx, None])
        ys.extend([ay, by, None])
        zs.extend([az, bz, None])

    if not xs:
        return

    fig.add_trace(go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="lines",
        line=dict(width=3, color="rgba(150, 150, 255, 0.8)"),
        name="Constellation lines",
        showlegend=True,
    ))


def compute_virgo_camera(df):
    coords = df[["x_pc", "y_pc", "z_pc"]].to_numpy()
    distances = df["distance_pc"].to_numpy()[:, None]
    dirs = coords / distances
    look_dir = dirs.mean(axis=0)
    look_dir /= np.linalg.norm(look_dir)

    centroid = coords.mean(axis=0)
    epsilon = df["distance_pc"].max() * 0.02
    eye = -look_dir * epsilon

    up = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(look_dir, up)) > 0.99:
        up = np.array([0.0, 1.0, 0.0])

    return dict(
        eye=dict(x=float(eye[0]), y=float(eye[1]), z=float(eye[2])),
        center=dict(x=float(centroid[0]), y=float(centroid[1]), z=float(centroid[2])),
        up=dict(x=float(up[0]), y=float(up[1]), z=float(up[2])),
    )


def build_updatemenus(df, camera, star_trace_index):
    star_names = df["name"].tolist()
    n = len(star_names)
    empty_text = [""] * n
    trace_selector = [star_trace_index]

    return [
        dict(
            type="buttons",
            direction="left",
            x=0.0,
            y=1.12,
            xanchor="left",
            yanchor="top",
            showactive=True,
            buttons=[
                dict(
                    label="Names ON",
                    method="restyle",
                    args=[
                        {"mode": ["markers+text"], "text": [star_names]},
                        trace_selector,
                    ],
                ),
                dict(
                    label="Names OFF",
                    method="restyle",
                    args=[
                        {"mode": ["markers"], "text": [empty_text]},
                        trace_selector,
                    ],
                ),
            ],
        ),
        dict(
            type="buttons",
            direction="left",
            x=0.25,
            y=1.12,
            xanchor="left",
            yanchor="top",
            showactive=False,
            buttons=[
                dict(
                    label="reset camera",
                    method="relayout",
                    args=[{"scene.camera": camera}],
                ),
            ],
        ),
    ]


def build_virgo_figure(df, edges_path="./data/virgo_edges.json"):
    edges = load_edges(edges_path)
    camera = compute_virgo_camera(df)
    fig = go.Figure()

    add_constellation_lines(fig, df, edges)

    fig.add_trace(go.Scatter3d(
        x=df["x_pc"],
        y=df["y_pc"],
        z=df["z_pc"],
        mode="markers+text",
        text=df["name"],
        name="Virgo stars",
    ))
    star_trace_index = len(fig.data) - 1

    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode="markers+text",
        text=["Earth"],
        marker=dict(size=6, color="green"),
        name="Earth",
    ))

    fig.update_layout(
        title="Virgo 3D Star Chart",
        updatemenus=build_updatemenus(df, camera, star_trace_index),
        scene=dict(
            xaxis_title="X (pc)",
            yaxis_title="Y (pc)",
            zaxis_title="Z (pc)",
            camera=camera,
        ),
    )
    return fig


def export_virgo_html(output_path, df, edges_path="./data/virgo_edges.json"):
    fig = build_virgo_figure(df, edges_path=edges_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(
        output_path,
        include_plotlyjs=True,
        full_html=True,
        post_script=build_camera_dampening_script(),
    )
    return output_path


def plot_virgo_3d_plotly(df, edges_path="./data/virgo_edges.json"):
    fig = build_virgo_figure(df, edges_path=edges_path)
    fig.show(post_script=build_camera_dampening_script())


if __name__ == "__main__":
    import argparse

    project_root = Path(__file__).resolve().parent.parent
    stars_path = project_root / "data" / "virgo_stars.csv"
    edges_path = project_root / "data" / "virgo_edges.json"
    default_html_path = project_root / "docs" / "index.html"

    parser = argparse.ArgumentParser(description="Virgo 3D star chart")
    parser.add_argument(
        "--html",
        nargs="?",
        const=default_html_path,
        default=None,
        type=Path,
        help=f"export standalone HTML (default: {default_html_path})",
    )
    args = parser.parse_args()

    df = pd.read_csv(stars_path)
    df = add_cartesian_coords(df)

    if args.html is not None:
        output_path = export_virgo_html(args.html, df, edges_path=edges_path)
        print(f"Wrote: {output_path}")
    else:
        print(df.head())
        plot_virgo_3d_plotly(df, edges_path=edges_path)
