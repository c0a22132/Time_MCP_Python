# Time MCP Server Examples

このドキュメントでは、Time MCP ServerのPython実装の使用例を示します。

## インストール

```bash
# リポジトリをクローン
git clone <repository_url>
cd Time_MCP_Python

# セットアップスクリプトを実行
./setup.sh   # Linux/macOS
# または
setup.bat    # Windows
```

## MCP サーバーとしての使用

### 基本的な起動

```bash
python -m time_mcp_server
```

### Claude Desktop との統合

Claude Desktopの設定ファイル（`claude_desktop_config.json`）に以下を追加：

```json
{
  "mcpServers": {
    "time-server": {
      "command": "python",
      "args": ["-m", "time_mcp_server"],
      "cwd": "/path/to/Time_MCP_Python"
    }
  }
}
```

## HTTP API サーバーとしての使用

### サーバー起動

```bash
python -m time_mcp_server --http
```

### API エンドポイント

#### 1. ヘルスチェック

```bash
curl http://localhost:8080/health
```

レスポンス：
```json
{
  "status": "healthy",
  "service": "time-mcp-server", 
  "version": "1.0.0",
  "timestamp": "2025-06-24T01:53:37.170168"
}
```

#### 2. 現在時刻の取得

##### 国名で指定

```bash
curl http://localhost:8080/time/Japan
curl http://localhost:8080/time/United%20States
curl http://localhost:8080/time/Australia
```

##### タイムゾーンで指定

```bash
curl http://localhost:8080/time/Asia/Tokyo
curl http://localhost:8080/time/America/New_York
curl http://localhost:8080/time/Europe/London
```

##### カスタム形式で指定

```bash
curl "http://localhost:8080/time/Asia/Tokyo?format=%Y年%m月%d日%20%H時%M分%S秒"
curl "http://localhost:8080/time/UTC?format=%A,%20%B%20%d,%20%Y%20at%20%I:%M%20%p"
```

レスポンス例：
```json
{
  "timezone": "Asia/Tokyo",
  "current_time": "2025-06-24 10:53:42",
  "timezone_name": "JST",
  "utc_offset": "+0900",
  "timestamp": 1750730022,
  "iso_string": "2025-06-24T10:53:42.132462+09:00"
}
```

#### 3. タイムゾーン一覧の取得

##### 全タイムゾーン

```bash
curl http://localhost:8080/timezones
```

##### 国で絞り込み

```bash
curl "http://localhost:8080/timezones?country=Japan"
curl "http://localhost:8080/timezones?country=United%20States"
curl "http://localhost:8080/timezones?country=Australia"
```

レスポンス例：
```json
{
  "query": "Japan",
  "total_timezones": 1,
  "timezones": ["Asia/Tokyo"]
}
```

## スタンドアロン テスト

```bash
python -m time_mcp_server --standalone
```

このモードでは、依存関係なしでサーバーの機能をテストできます。

## MCPツールの使用例

### get_current_time

```json
{
  "name": "get_current_time",
  "arguments": {
    "timezone": "Japan",
    "format": "%Y-%m-%d %H:%M:%S"
  }
}
```

### list_timezones

```json
{
  "name": "list_timezones", 
  "arguments": {
    "country": "United States"
  }
}
```

## 対応している国・地域

- **アジア**: 日本、韓国、中国、シンガポール、タイ、インド、パキスタン、UAE
- **ヨーロッパ**: イギリス、ドイツ、フランス、イタリア、スペイン、オランダ、スイス
- **北米**: アメリカ、カナダ、メキシコ
- **オセアニア**: オーストラリア、ニュージーランド
- **南米**: ブラジル、アルゼンチン、チリ、コロンビア
- **アフリカ**: 南アフリカ、エジプト、ナイジェリア、ケニア

## トラブルシューティング

### 依存関係のエラー

```bash
pip install -r requirements.txt
```

### Python環境の問題

```bash
python --version  # 3.8以上であることを確認
pip install --upgrade pip
```

### ポートが使用中の場合

```bash
python -m time_mcp_server --http --port 8081
```

## テストの実行

```bash
pip install pytest
pytest tests/
```

## 開発

### コードフォーマット

```bash
pip install black isort
black .
isort .
```

### 型チェック

```bash
pip install mypy
mypy .
```
