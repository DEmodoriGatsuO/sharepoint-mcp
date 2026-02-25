# Task List — Initial Implementation

## 完了基準

- `black` / `ruff` / `pytest` が全てクリーンに通過する
- CLAUDE.md が要求する永続ドキュメント6件が `docs/` に存在する
- `.steering/20260225-initial-implementation/` の3ドキュメントが存在する

---

## タスク

### Phase 1: 品質チェック整備

- [x] `pytest-asyncio` インストール (`pip install pytest-asyncio`)
- [x] `pytest.ini` に `asyncio_mode = auto` 追加
- [x] `black .` で全ファイルをフォーマット
- [x] `ruff check --fix .` で自動修正可能な11件を修正
- [x] `config_checker.py:96` — 未使用変数 `domain` 削除 (F841)
- [x] `resources/site.py:22` — 未使用変数 `graph_client` 削除 (F841)
- [x] `resources/site.py` — 未使用インポート `GraphClient` 削除 (F401)
- [x] `server.py` — インポートをログ設定より前に移動 (E402)
- [x] `tests/test_auth.py` — `== True/False` を真偽値評価に変更 (E712 × 5件)
- [x] `utils/document_processor.py` — `openpyxl` に `# noqa: F401` 付与
- [x] 全チェック通過確認: `black --check .` / `ruff check .` / `pytest`

### Phase 2: 永続ドキュメント作成

- [x] `docs/product-requirements.md` 作成・承認
- [x] `docs/functional-design.md` 作成・承認
- [x] `docs/architecture.md` 作成・承認
- [x] `docs/repository-structure.md` 作成・承認
- [x] `docs/development-guidelines.md` 作成・承認
- [x] `docs/glossary.md` 作成・承認

### Phase 3: ステアリングドキュメント作成

- [x] `.steering/20260225-initial-implementation/` ディレクトリ作成
- [x] `requirements.md` 作成
- [x] `design.md` 作成
- [x] `tasklist.md` 作成（本ファイル）

---

## 結果

| チェック | 結果 |
|---------|------|
| `black --check .` | 全21ファイル通過 |
| `ruff check .` | エラー0件 |
| `pytest` | 5/5 通過 |
