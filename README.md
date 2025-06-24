# Time MCP Server (Python)

LLMに指定された国(もしくはタイムゾーン)の現在時刻を提供するMCPサーバーのPython実装です。

## ✨ 機能

- 指定されたタイムゾーンや国の現在時刻を取得
- 利用可能なタイムゾーンの一覧表示
- 国名から主要なタイムゾーンの自動推定
- MCPプロトコルとHTTP APIの両方をサポート

## 🚀 クイックスタート

### ワンクリックデプロイ

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/services/deploy?name=time-mcp-python&type=git&repository=github.com/yourusername/Time_MCP_Python&branch=main)

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/yourusername/Time_MCP_Python)

## インストール

```bash
pip install -e .
```

開発用依存関係も含めてインストールする場合：

```bash
pip install -e ".[dev]"
```

### Docker

```bash
# イメージをビルド
docker build -t time-mcp-server .

# コンテナを実行
docker run -p 8080:8080 time-mcp-server

# または Docker Compose を使用
docker-compose up
```

## 📖 詳細ドキュメント

- [使用例とAPI仕様](EXAMPLES.md)
- [デプロイメントガイド](DEPLOYMENT.md)
- [GitHub Actions CI/CD](.github/workflows/ci-cd.yml)

## 使用方法

### MCPサーバーとして実行（LLMとの統合用）

```bash
python -m time_mcp_server
```

または：

```bash
time-mcp-server
```

### HTTPサーバーとして実行（Web API用）

```bash
python -m time_mcp_server --http
```

## API エンドポイント（HTTPサーバー）

### 健康チェック
- `GET /health` - サーバーの状態確認

### 時刻取得
- `GET /time/{timezone}?format={format}` - 指定タイムゾーンの現在時刻

例:
```bash
curl http://localhost:8080/time/Japan
curl http://localhost:8080/time/Asia/Tokyo?format=%Y-%m-%d_%H:%M:%S
```

### タイムゾーン一覧
- `GET /timezones?country={country}` - タイムゾーン一覧取得

例:
```bash
curl http://localhost:8080/timezones
curl http://localhost:8080/timezones?country=Japan
```

## MCPツール

### get_current_time

指定されたタイムゾーンまたは国の現在時刻を取得します。

パラメータ：
- `timezone` (必須): タイムゾーン名（例: 'Asia/Tokyo', 'America/New_York'）または国名（例: 'Japan', 'United States'）
- `format` (オプション): 時刻の形式（デフォルト: '%Y-%m-%d %H:%M:%S'）

### list_timezones

利用可能なタイムゾーンの一覧を取得します。

パラメータ：
- `country` (オプション): 国名または国コードでタイムゾーンをフィルタリング

## 例

### MCPサーバーの使用例

```bash
# MCPサーバーを起動
python -m time_mcp_server

# 別のターミナルでMCPクライアントから接続
# (Claude DesktopやMCP対応のLLMから使用)
```

### HTTP APIの使用例

```bash
# HTTPサーバーを起動
python -m time_mcp_server --http

# 日本の現在時刻を取得
curl http://localhost:8080/time/Japan

# ニューヨークの現在時刻をカスタム形式で取得
curl "http://localhost:8080/time/America/New_York?format=%A, %B %d, %Y at %I:%M %p"

# アメリカのタイムゾーン一覧を取得
curl http://localhost:8080/timezones?country=United_States
```

## 対応国・タイムゾーン

主要な国とタイムゾーンに対応しています：

- 日本 (Asia/Tokyo)
- アメリカ (America/New_York, America/Chicago, America/Denver, America/Los_Angeles など)
- 中国 (Asia/Shanghai, Asia/Hong_Kong)
- イギリス (Europe/London)
- ドイツ (Europe/Berlin)
- フランス (Europe/Paris)
- オーストラリア (Australia/Sydney, Australia/Melbourne など)
- その他多数

詳細なタイムゾーンリストは `list_timezones` ツールで確認できます。

## 開発

### テスト実行

```bash
pytest
```

### コードフォーマット

```bash
black .
isort .
```

### 型チェック

```bash
mypy .
```

## ライセンス

MIT License
