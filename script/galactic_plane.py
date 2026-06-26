import matplotlib.pyplot as plt
import numpy as np
import pandas as pd



def add_cartesian_coords_xy(df):
    ra = np.radians(df["ra_deg"])
    d = df["distance_pc"]

    df = df.copy()

    # 上から見た投影（Z無視）
    df["x_pc"] = d * np.cos(ra)
    df["y_pc"] = d * np.sin(ra)

    return df

def invert_axis(df):
    df = df.copy()
    df["x_pc"] = -df["x_pc"]
    df["y_pc"] = -df["y_pc"]
    return df

def plot_galactic_plane_antique(df, output_path=None):
    df = add_cartesian_coords_xy(df)
    df = invert_axis(df)
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)

    # 背景（完全白）
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # グリッド（薄い点線）
    ax.grid(True, linestyle=":", linewidth=0.5, color="0.8")

    # 星（グレー階調のみ）
    ax.scatter(
        df["x_pc"],
        df["y_pc"],
        s=10,
        c="black",
        alpha=0.35,
        linewidths=0
    )

    # 太陽（強調点）
    ax.scatter(
        0, 0,
        s=60,
        c="black",
        marker="o"
    )

    # 軸の線を“地図風”に
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color("0.2")

    # 軸ラベルも控えめに
    ax.set_xlabel("X (pc)", fontsize=9)
    ax.set_ylabel("Y (pc)", fontsize=9)

    # 等スケール（超重要）
    ax.set_aspect("equal", adjustable="box")

    # 余白を広く（アンティーク感の核心）
    plt.margins(0.1)

    # 目盛りも控えめ
    ax.tick_params(axis='both', which='major', labelsize=8, colors='0.2')

    if output_path:
        plt.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight",
            facecolor="white"
        )

    plt.savefig("./output/galactic_plane_antique.png")
    plt.show()
    
if __name__ == "__main__":
    df = pd.read_csv("./data/virgo_stars.csv")
    plot_galactic_plane_antique(df, output_path="./output/galactic_plane_antique.png") 