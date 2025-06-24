# Time MCP Server Python - Deployment Guide

このドキュメントでは、Time MCP Server（Python版）をKoyeb、Heroku、その他のクラウドプラットフォームにデプロイする方法を説明します。

## 🚀 Koyeb デプロイメント（推奨）

### 重要なアップデート

**2025年6月24日**: Koyebデプロイメントの問題を修正しました。以下の変更が適用されています：

- ✅ **Procfile**: `python -m uvicorn time_mcp_server.http_server:app --host 0.0.0.0 --port $PORT`
- ✅ **uvicorn**: ファクトリーパターンでの起動をサポート
- ✅ **ポート**: 環境変数 `$PORT` を正しく使用
- ✅ **ヘルスチェック**: `/health` エンドポイントでの監視

### ワンクリックデプロイ

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/services/deploy?name=time-mcp-python&type=git&repository=github.com/yourusername/Time_MCP_Python&branch=main)

### 前提条件

- Koyebアカウント
- GitHubリポジトリ（このプロジェクトをフォーク/クローン）

### 方法1: Koyeb Web UI を使用

1. **Koyebにログイン**
   - https://app.koyeb.com にアクセス
   - GitHubアカウントでサインイン

2. **新しいサービスを作成**
   - "Deploy your first app" または "Create Service" をクリック
   - "GitHub" を選択

3. **リポジトリを設定**
   - このプロジェクトのGitHubリポジトリを選択
   - ブランチを選択（通常は `main` または `master`）

4. **ビルド設定**
   - **Build command**: `pip install -r requirements.txt`
   - **Run command**: `python -m time_mcp_server --http`

5. **環境変数を設定**
   ```
   PORT = 8080
   PYTHON_VERSION = 3.11
   ENVIRONMENT = production
   ```

6. **その他の設定**
   - **Regions**: お好みのリージョンを選択
   - **Instance type**: Nano (無料プラン) または必要に応じてより大きなインスタンス

7. **デプロイ**
   - "Deploy" ボタンをクリック
   - デプロイが完了するまで数分待機

### 方法2: Koyeb CLI を使用

1. **Koyeb CLI をインストール**
   ```bash
   # macOS (Homebrew)
   brew install koyeb/tap/koyeb

   # Linux/Windows
   curl -L https://github.com/koyeb/koyeb-cli/releases/latest/download/koyeb-linux-amd64.tar.gz | tar xz
   ```

2. **認証**
   ```bash
   koyeb auth login
   ```

3. **デプロイ**
   ```bash
   # リポジトリのルートディレクトリで実行
   koyeb service create time-mcp-python \
     --git https://github.com/yourusername/Time_MCP_Python \
     --git-branch main \
     --ports 8080:http \
     --env PORT=8080 \
     --env PYTHON_VERSION=3.11 \
     --env ENVIRONMENT=production
   ```

### 方法3: koyeb.yaml を使用

プロジェクトに含まれる `koyeb.yaml` ファイルを使用：

```bash
koyeb service create --definition koyeb.yaml
```

## Heroku デプロイメント

### ワンクリックデプロイ

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/yourusername/Time_MCP_Python)

### 手動デプロイ

1. **Heroku CLI をインストール**
   ```bash
   # インストール方法は https://devcenter.heroku.com/articles/heroku-cli を参照
   ```

2. **アプリを作成**
   ```bash
   heroku create your-time-mcp-app
   ```

3. **環境変数を設定**
   ```bash
   heroku config:set PYTHON_VERSION=3.11
   heroku config:set ENVIRONMENT=production
   ```

4. **デプロイ**
   ```bash
   git push heroku main
   ```

## その他のクラウドプラットフォーム

### Railway

1. Railwayにサインアップ: https://railway.app
2. "Deploy from GitHub repo" を選択
3. このリポジトリを選択
4. 環境変数を設定:
   ```
   PORT = 8080
   PYTHON_VERSION = 3.11
   ```
5. Start Command: `python -m time_mcp_server --http`

### Render

1. Renderにサインアップ: https://render.com
2. "New Web Service" を選択
3. GitHubリポジトリを接続
4. 設定:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m time_mcp_server --http`
5. 環境変数を設定:
   ```
   PYTHON_VERSION = 3.11
   ENVIRONMENT = production
   ```

### Vercel (サーバーレス)

注意: Vercelはサーバーレス環境のため、永続的なHTTPサーバーには適していません。APIエンドポイントとしての利用を検討してください。

### Docker でのデプロイ

どのクラウドプラットフォームでも使用可能：

```bash
# イメージをビルド
docker build -t time-mcp-server .

# ローカルで実行
docker run -p 8080:8080 time-mcp-server

# DockerHubにプッシュ（オプション）
docker tag time-mcp-server yourusername/time-mcp-server
docker push yourusername/time-mcp-server
```

## 環境変数の説明

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `PORT` | HTTPサーバーのポート番号 | 8080 | いいえ |
| `HOST` | HTTPサーバーのホスト | 0.0.0.0 | いいえ |
| `PYTHON_VERSION` | Pythonバージョン | 3.11 | いいえ |
| `ENVIRONMENT` | 実行環境 | production | いいえ |

## ヘルスチェック

すべてのデプロイメントで、以下のエンドポイントがヘルスチェックに使用可能です：

- **URL**: `/health`
- **Method**: GET
- **Response**: 
  ```json
  {
    "status": "healthy",
    "service": "time-mcp-server",
    "version": "1.0.0",
    "timestamp": "2025-06-24T01:59:35.171015"
  }
  ```

## トラブルシューティング

### デプロイが失敗する場合

1. **依存関係の問題**
   ```bash
   # requirements.txt が正しいことを確認
   pip install -r requirements.txt
   ```

2. **ポートの問題**
   - 環境変数 `PORT` が設定されていることを確認
   - プラットフォームが提供するポートを使用

3. **Pythonバージョン**
   - Python 3.8以上が必要
   - `runtime.txt` ファイルでバージョンを指定（一部プラットフォーム）

### ログの確認

```bash
# Heroku
heroku logs --tail

# Koyeb
koyeb service logs your-service-name --follow
```

## パフォーマンス最適化

1. **メモリ使用量の最適化**
   - 必要に応じてより大きなインスタンスタイプを選択

2. **レスポンス時間の改善**
   - アプリケーションサーバーと地理的に近いリージョンを選択

3. **可用性の向上**
   - 複数のリージョンにデプロイ（プレミアムプランが必要な場合があります）

## コスト最適化

- **無料プラン**: Koyeb、Heroku、Renderは無料プランを提供
- **スリープモード**: 非アクティブ時にインスタンスがスリープする場合があります
- **使用量監視**: 使用量とコストを定期的に確認
