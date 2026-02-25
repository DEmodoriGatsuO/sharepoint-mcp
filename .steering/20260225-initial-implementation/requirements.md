# Requirements — Initial Implementation

## Feature Description

SharePoint MCP Server の初期実装。Microsoft Graph API を通じて SharePoint Online のコンテンツに LLM アプリケーションからアクセスできる MCP サーバーを構築する。

## User Stories

- US-01: サイト情報の取得 — LLM から SharePoint サイトの基本情報を取得できる
- US-02: ドキュメントライブラリ一覧 — サイト内のドキュメントライブラリを列挙できる
- US-03: コンテンツ検索 — サイト全体を全文検索できる
- US-04: ドキュメント内容取得 — DOCX / PDF / XLSX / CSV / TXT ファイルの内容を読み取れる
- US-05: リストアイテム作成・更新 — SharePoint リストにアイテムを追加・編集できる
- US-06: サイト・リスト・ページ作成 — SharePoint 資産をプロビジョニングできる

## Acceptance Criteria

- [ ] Microsoft Entra ID クライアント資格情報フローで認証できる
- [ ] 全 MCP ツールが FastMCP で正しく登録・動作する
- [ ] トークン期限切れ前に自動リフレッシュが行われる
- [ ] 認証失敗時にわかりやすいエラーが LLM に返る
- [ ] `black` + `ruff` + `pytest` が全てクリーンに通過する
- [ ] `.env` を使った設定が正しく機能する

## Constraints

- Python 3.10+ のみサポート
- Microsoft Graph API v1.0 のみ使用
- クライアント資格情報フロー（委任認証は対象外）
- `.env` は絶対に Git にコミットしない
