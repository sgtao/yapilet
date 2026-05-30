# yapilet

YAML ファイルで API リクエストとアクションチェーンを定義・実行する Python ツールキット。
ライブラリ・CLI・GUI・API サーバーとして利用できます。

---

## インストール

```bash
git clone <repo-url>
cd yapilet
mise install        # Python 3.13 + uv のセットアップ
mise run install    # 依存関係のインストール
```

---

詳しい使い方は **[USAGE.ja.md](USAGE.ja.md)** を参照してください。

English documentation: [README.md](README.md) / [USAGE.md](USAGE.md)

---

## 開発コマンド

```bash
mise run test       # テスト実行
mise run test-cov   # カバレッジ付きテスト
mise run lint       # ruff によるリント
mise run format     # ruff によるフォーマット
mise run check      # lint + mypy + test の一括実行
mise run build      # wheel ビルド（dist/）
mise run cli:single # CLI スモークテスト（single）
mise run cli:action # CLI スモークテスト（action）
mise run cli:chat   # CLI スモークテスト（対話チャット、1ターン）
mise run gui:start  # Flet デスクトップ GUI を起動
```

---

## ライセンス

[Apache License 2.0](LICENSE)

---

🤖 Built with [Claude Code](https://claude.com/claude-code)
