# yapilet 使い方ガイド

---

## YAML 設定ファイルの書き方

設定ファイルは `configs/` 以下に置きます。

### 単発リクエスト（`configs/singles/*.yaml`）

```yaml
title: "001_get_simple_api_test"
note: |
  - dummyjson.com の商品情報を取得する
  - response_path で最後のタグを抽出
single_config:
  method: GET
  url: "https://dummyjson.com/products/1"
  headers:
    Content-Type: "application/json"
  response_path: "tags[-1]"
```

| フィールド | 説明 |
|---|---|
| `title:` | 設定の名前 |
| `note:` | Markdown で自由に記述できる説明 |
| `method:` | `GET` / `POST` / `PUT` / `DELETE` |
| `url:` | リクエスト先 URL（`＜API_KEY＞` などのプレースホルダー使用可） |
| `headers:` | リクエストヘッダー（dict 形式） |
| `body:` | リクエストボディ（dict 形式） |
| `response_path:` | jmespath 式でレスポンスから値を抽出 |

### アクションチェーン（`configs/actions/*.yaml`）

複数のリクエストを順番に実行し、前のステップの結果を次のステップに渡します。

```yaml
title: "echo_chain"
note: "2 ステップのチェーン — step 2 が step 1 の結果を受け取る"
action_config:
  steps:
    - config: "configs/singles/echo.yaml"
      inputs:
        - "＜user_input_0＞"
    - config: "configs/singles/echo.yaml"
      inputs:
        - "＜action_result_0＞"
```

### プレースホルダー一覧

| プレースホルダー | エイリアス | 意味 |
|---|---|---|
| `＜user_input_N＞` | `{{user_input_N}}` | N 番目のユーザー入力（0-indexed） |
| `＜action_result_N＞` | `{{action_result_N}}` | N 番目のステップの抽出結果 |
| `＜API_KEY＞` | `{{API_KEY}}` | API キー（実行時に置換） |

---

## GUI での使い方（デスクトップアプリ）

```bash
mise run gui:start
# または
yapilet-gui
```

Flet デスクトップウィンドウが起動し、4 つのタブが使えます：

| タブ | 機能 |
|---|---|
| **Single** | `configs/singles/*.yaml` を選んで、ユーザー入力を入力してリクエストを実行 |
| **Chat** | チャット設定（`body.messages` を持つ config）を選んでマルチターン対話 |
| **Action** | `configs/actions/*.yaml` を選んでチェーンを実行、ステップごとの結果を確認 |
| **Settings** | API Key と Mock Echo モードの設定 |

**Settings の挙動:**
- API Key は次のリクエストからすぐ反映（再 Load 不要）
- Mock Echo の変更は次の **[Load]** 時に反映（チャット履歴は seed messages にリセット）
- `API_KEY` 環境変数が設定済みの場合は API Key フィールドを空白のままで OK

---

## CLI での使い方

### 単発リクエスト

```bash
yapilet single <設定ファイルのパス> [オプション]
```

```bash
# 実際に HTTP リクエストを送る
yapilet single configs/singles/001_get_simple_api_test.yaml

# API キーを指定
yapilet single configs/singles/myapi.yaml --api-key sk-xxx

# 複数のユーザー入力を渡す
yapilet single configs/singles/explain.yaml \
  --user-input "機械学習" \
  --api-key sk-xxx

# --mock-echo: 実際の HTTP を送らず、リクエスト内容を echo して返す（動作確認用）
yapilet single configs/singles/echo.yaml --user-input hello --mock-echo
```

### アクションチェーン

```bash
yapilet action <設定ファイルのパス> [オプション]
```

```bash
# 2 ステップのチェーンを実行
yapilet action configs/actions/echo_chain.yaml --user-input hello --mock-echo
```

出力例：
```
step 1 (echo): hello
step 2 (echo): hello
```

### 対話型チャット

```bash
yapilet chat <設定ファイルのパス> [オプション]
```

マルチターンの対話セッションを開きます。YAML は `single_config:` 形式で、body に `messages` 配列（シードメッセージ：system prompt、会話例など）を含む必要があります。ユーザーの入力は `{"role": "user"}` として末尾に追加され、assistant の返答が追記されてから次のターンに進みます。

```bash
# 実際の API で対話（Groq の例）
yapilet chat configs/messages/groq_chat.yaml --api-key $GROQ_API_KEY

# オフライン動作確認
yapilet chat configs/singles/echo_chat.yaml --mock-echo
```

セッション例：
```
Chat started. Type 'exit' or press Ctrl+C to quit.
> こんにちは
どのようなご質問がありますか？
> Python とは何ですか？
Python は高水準プログラミング言語で...
> exit
Goodbye.
```

#### チャット設定ファイルの書き方

body に `messages` 配列を持つ `single_config:` をそのまま使います：

```yaml
title: "groq_chat"
single_config:
  method: POST
  uri: "https://api.groq.com/openai/v1/chat/completions"
  header_df:
    - Property: Authorization
      Value: "Bearer ＜API_KEY＞"
  req_body:
    model: "llama-3.1-8b-instant"
    messages:
      - role: "system"
        content: "あなたは聡明なAIです。"
      - role: "assistant"
        content: "了解です。どのような質問がありますか？"
  user_property_path: "choices[0].message.content"
```

- `messages` 配列がシード（system prompt、会話例）として機能します。セッション中のユーザー/assistant メッセージは自動的に追記されます。
- `response_path` / `user_property_path` でレスポンスから assistant の返答を抽出します。

### オプション一覧

| オプション | 説明 |
|---|---|
| `--user-input TEXT` | ユーザー入力（`single` / `action` コマンドで使用、複数回指定可） |
| `--api-key TEXT` | API キー（省略時は `API_KEY` 環境変数） |
| `--mock-echo` | MockAdapter 使用（HTTP を送らずリクエストを echo） |

### API キーを環境変数で渡す

```bash
export API_KEY=sk-xxxxxxxxxxxx
yapilet single configs/singles/myapi.yaml --user-input "機械学習"
```

---

## ライブラリとして使う

Python コードから直接 use case を呼び出せます。

### 単発リクエスト

```python
from yapilet.core.application.execute_single import ExecuteSingleUseCase
from yapilet.core.infrastructure.mock_adapter import MockAdapter  # 本番は HttpxAdapter
from yapilet.core.services.config_loader import ConfigLoader

uc = ExecuteSingleUseCase(
    http_port=MockAdapter(),
    config_loader=ConfigLoader(),
)

result = uc.run(
    "configs/singles/echo.yaml",
    user_inputs=["hello"],
    api_key="sk-demo",
)

print(result.extracted)   # → "hello"
print(result.is_success)  # → True
print(result.status_code) # → 200
```

### アクションチェーン

```python
from yapilet.core.application.execute_action import ExecuteActionUseCase
from yapilet.core.application.execute_single import ExecuteSingleUseCase
from yapilet.core.infrastructure.mock_adapter import MockAdapter
from yapilet.core.services.config_loader import ConfigLoader

single_uc = ExecuteSingleUseCase(
    http_port=MockAdapter(),
    config_loader=ConfigLoader(),
)
action_uc = ExecuteActionUseCase(
    single_usecase=single_uc,
    config_loader=ConfigLoader(),
)

results = action_uc.run(
    "configs/actions/echo_chain.yaml",
    user_inputs=["hello"],
    api_key="sk-demo",
)

for i, r in enumerate(results, start=1):
    print(f"step {i}: extracted={r.extracted}, success={r.is_success}")
```

### マルチターンチャット

```python
from yapilet.core.application.execute_chat import ExecuteChatUseCase
from yapilet.core.infrastructure.mock_adapter import MockAdapter  # 本番は HttpxAdapter
from yapilet.core.services.config_loader import ConfigLoader

uc = ExecuteChatUseCase(
    http_port=MockAdapter(),
    config_loader=ConfigLoader(),
)

uc.load("configs/singles/echo_chat.yaml")

response = uc.send("こんにちは！", api_key="sk-demo")
print(response)  # → "こんにちは！"

print(uc.history)
# → [
#     {"role": "system",    "content": "You are helpful."},
#     {"role": "user",      "content": "こんにちは！"},
#     {"role": "assistant", "content": "こんにちは！"},
#   ]
```

`ExecuteChatUseCase` は stateful です。`load()` を一度呼んでからターンごとに `send()` を呼びます。会話履歴はオブジェクトが生きている間メモリ上に保持されます。

### Result オブジェクトのフィールド

| フィールド | 型 | 説明 |
|---|---|---|
| `status_code` | `int` | HTTP ステータスコード |
| `is_success` | `bool` | 200〜299 なら `True` |
| `extracted` | `Any` | `response_path` で抽出した値 |
| `body` | `Any` | レスポンス全体 |
| `error` | `str \| None` | エラーメッセージ（成功時は `None`） |
