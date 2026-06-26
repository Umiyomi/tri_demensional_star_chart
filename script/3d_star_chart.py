import plotly.graph_objects as go
import pandas as pd
import numpy as np


def add_cartesian_coords(df):
    ra = np.radians(df["ra_deg"])
    dec = np.radians(df["dec_deg"])
    d = df["distance_pc"]

    df = df.copy()
    df["x_pc"] = d * np.cos(dec) * np.cos(ra)
    df["y_pc"] = d * np.cos(dec) * np.sin(ra)
    df["z_pc"] = d * np.sin(dec)
    return df


def plot_virgo_3d_plotly(df):
    fig = go.Figure()

    # 星
    fig.add_trace(go.Scatter3d(
        x=df["x_pc"],
        y=df["y_pc"],
        z=df["z_pc"],
        mode='markers+text',
        text=df["name"],
        name="Virgo stars"
    ))

    # 地球
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers+text',
        text=["Earth"],
        marker=dict(size=6, color="green"),
        name="Earth"
    ))

    fig.update_layout(
        scene=dict(
            xaxis_title="X (pc)",
            yaxis_title="Y (pc)",
            zaxis_title="Z (pc)"
        )
    )

    fig.show()

if __name__ == "__main__":
    df = pd.read_csv("./data/virgo_stars.csv")
    df = add_cartesian_coords(df)
    print(df.head())
    plot_virgo_3d_plotly(df)