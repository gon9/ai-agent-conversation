# AI Agent Conversation for Job Applications

求人サイトの登録ユーザから追加情報を対話形式で自然に取得し、離脱を最小化して最終的な応募率を高めるAIエージェントの実装です。

## プロジェクト概要

このプロジェクトは、求人サイトにおいて登録ユーザーから追加情報を対話形式で効率的に収集するAIエージェントを実装しています。ユーザー体験を最適化し、離脱率を最小化することで、最終的な応募率の向上を目指します。

### 主な特徴

- 自然な対話形式でユーザーから情報を収集
- 質問数を最小限に抑え、必要に応じてスキップ/後回し可能
- 進捗インジケータによりユーザーの不安を軽減
- 一時離脱→再開をサポート（中断位置から再質問しない）
- 選択肢のあるクエリはボタン化して回答しやすく

## 技術スタック

### バックエンド
- FastAPI (Python 3.11)
- LangGraph + LangChain による対話フローとLLM呼び出し
- InMemoryStore によるメモリ実装（将来的にRedisなどに拡張可能）

### フロントエンド
- Gradio による簡易チャットUI

## ディレクトリ構成

```
.
├── app/                    # アプリケーションコード
│   ├── config/            # 設定ファイル
│   ├── interface/         # フロントエンドUI (Gradio)
│   ├── graph/             # LangGraphフロー定義
│   ├── models/            # データモデル
│   └── utils/             # ユーティリティ関数
├── tests/                 # テストコード
│   ├── integration/       # 統合テスト
│   └── unit/              # 単体テスト
├── .env.example           # 環境変数サンプル
├── .gitignore             # Gitの除外ファイル設定
├── .python-version        # Pythonバージョン指定
├── docker-compose.yml     # Dockerコンポーズ設定
├── Dockerfile             # Dockerビルド設定
├── pyproject.toml         # プロジェクト依存関係
└── README.md              # プロジェクト説明
```

## セットアップ手順

### 前提条件
- Python 3.11
- uv (パッケージマネージャー)
- Docker および Docker Compose (オプション)

### ローカル開発環境のセットアップ

1. リポジトリをクローン
   ```bash
   git clone <repository-url>
   cd ai-agent-conversation
   ```

2. 仮想環境を作成し、依存関係をインストール
   ```bash
   uv venv .venv
   source .venv/bin/activate  # Windowsの場合: .venv\Scripts\activate
   uv pip install -e .
   ```

3. 環境変数の設定
   ```bash
   cp .env.example .env
   # .envファイルを編集し、必要な環境変数（特にOPENAI_API_KEY）を設定
   ```

4. アプリケーションの起動
   ```bash
   # バックエンドの起動
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # 別のターミナルでフロントエンドの起動
   python -m app.interface.ui
   ```

### Dockerを使用したセットアップ

1. 環境変数の設定
   ```bash
   cp .env.example .env
   # .envファイルを編集し、必要な環境変数を設定
   ```

2. Dockerコンテナのビルドと起動
   ```bash
   docker-compose up -d
   ```

3. ブラウザでアクセス
   - バックエンドAPI: http://localhost:8000
   - フロントエンドUI: http://localhost:7860

## テストの実行

```bash
# 全てのテストを実行
pytest

# 単体テストのみ実行
pytest tests/unit

# 統合テストのみ実行
pytest tests/integration

# カバレッジレポートの生成
pytest --cov=app tests/
```

## ユーザー体験設計の要点

1. **最小限の質問数**
   - 必要最低限の情報のみを収集
   - スキップ機能により、ユーザーが後で回答できるようにする

2. **自然な対話体験**
   - 質問は1行以内で簡潔に
   - 肯定的なトーンで質問を提示
   - 選択肢がある場合はボタン化して回答しやすく

3. **進捗の可視化**
   - 残りの質問数を表示し、完了までの見通しを提供
   - 必須質問と任意質問を区別

4. **セッション継続性**
   - 一時離脱後も状態を保持
   - 再開時に同じ質問を繰り返さない

## 拡張ポイント

- **データストレージ**: 現在はInMemoryStoreを使用していますが、RedisやMongoDBなどに置き換え可能
- **質問カスタマイズ**: `app/config/settings.py`の`QUESTIONS`リストを編集することで質問内容をカスタマイズ可能
- **UIの拡張**: 現在はGradioによる最小限のUIですが、より洗練されたUIに置き換え可能
- **マルチモーダル対応**: 画像や音声による入力にも拡張可能