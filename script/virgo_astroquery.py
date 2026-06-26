# virgo_astroquery.py

from astroquery.simbad import Simbad
import astropy.units as u
from astropy.coordinates import SkyCoord
import pandas as pd
import numpy as np


# =========================
# 1. Virgo主要星リスト
# =========================
VIRGO_STARS = [
    "Spica",        # α Vir
    "Zavijava",     # β Vir
    "Porrima",      # γ Vir
    "Minelauva",    # δ Vir
    "Vindemiatrix", # ε Vir
    "Heze",         # ζ Vir
    "Zaniah",       # η Vir
    "Syrma",        # ι Vir
    "Kang",         # κ Vir
    "Khambalia",    # λ Vir
    "Elgafar"       # φ Vir
]


# =========================
# 2. SIMBAD設定
# =========================
custom_simbad = Simbad()
custom_simbad.add_votable_fields(
    "ra",
    "dec",
    "parallax"
)


# =========================
# 3. 取得関数
# =========================
def query_star(name: str):
    """
    SIMBADから単一天体情報を取得
    """
    result = custom_simbad.query_object(name)

    if result is None:
        print(f"[WARN] {name} not found")
        return None

    ra = result["ra"][0]
    dec = result["dec"][0]
    parallax = result["plx_value"][0]  # mas

    # 視差 → 距離 (pc)
    if parallax is None or parallax <= 0:
        distance_pc = np.nan
        distance_ly = np.nan
    else:
        distance_pc = 1000.0 / parallax
        distance_ly = distance_pc * 3.26156

    return {
        "name": name,
        "ra_deg": ra,
        "dec_deg": dec,
        "parallax_mas": parallax,
        "distance_pc": distance_pc,
        "distance_ly": distance_ly
    }


# =========================
# 4. 一括取得
# =========================
def build_virgo_catalog():
    records = []

    for star in VIRGO_STARS:
        print(f"querying {star}...")
        data = query_star(star)
        if data is not None:
            records.append(data)

    df = pd.DataFrame(records)
    return df


# =========================
# 5. 実行
# =========================
if __name__ == "__main__":
    df = build_virgo_catalog()

    print("\n=== Virgo Star Catalog ===")
    print(df)

    # CSV保存
    df.to_csv("virgo_stars.csv", index=False)
    print("\nSaved: virgo_stars.csv")