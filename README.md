# 立体星図

乙女座 (Virgo) の立体星図。

## Viewer

GitHub Pages で公開したインタラクティブ viewer:

`https://<GitHubユーザー名>.github.io/tri_dimensional_star_chart/`

例: `https://umiyomi.github.io/tri_dimensional_star_chart/`

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

データを更新したら `script/virgo_astroquery.py` で CSV を再取得し、`--html` で HTML を再生成してください。
