# 立体星図

乙女座 (Virgo) の立体星図。

## Viewer

GitHub Pages:

https://umiyomi.github.io/tri_demensional_star_chart/

リポジトリ: https://github.com/Umiyomi/tri_demensional_star_chart

## AR Viewer（Hiro マーカー）

スマホカメラで Hiro マーカーを映すと、紙の上に 3D 星図が重なります。

https://umiyomi.github.io/tri_demensional_star_chart/ar/

### 使い方

1. [`docs/ar/marker-hiro.png`](docs/ar/marker-hiro.png) を印刷する（マーカー幅 **8cm 前後**、マット紙推奨）
2. スマホブラウザで上記 URL を開く（HTTPS 必須・カメラ許可が必要）
3. 印刷したマーカーをカメラに映す

### AR データを再生成する

```bash
.venv/bin/python script/build_ar.py
```

`docs/ar/virgo.json` が更新されます。HTML を変更した場合もあわせて commit / push してください。

## ローカルで開く

```bash
.venv/bin/python script/3d_star_chart.py
```

ブラウザでインタラクティブな 3D viewer が起動します。

## HTML を生成する

```bash
.venv/bin/python script/3d_star_chart.py --html
```

`docs/index.html` にスタンドアロン HTML（Plotly 同梱）が出力されます。

## GitHub Pages で公開する

1. `docs/index.html` をコミットして `main` に push
2. GitHub リポジトリの **Settings → Pages**
3. **Build and deployment → Source** を `Deploy from a branch`
4. **Branch** を `main`、フォルダを `/docs` に設定

データを更新したら `script/virgo_astroquery.py` で CSV を再取得し、`--html` で HTML を再生成、`build_ar.py` で AR データを再生成してください。
