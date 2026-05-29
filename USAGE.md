# yapilet Usage Guide

---

## YAML Configuration Files

Place configuration files under `configs/`.

### Single Request (`configs/singles/*.yaml`)

```yaml
title: "001_get_simple_api_test"
note: |
  - Fetch product info from dummyjson.com
  - Extract the last tag with response_path
single_config:
  method: GET
  url: "https://dummyjson.com/products/1"
  headers:
    Content-Type: "application/json"
  response_path: "tags[-1]"
```

| Field | Description |
|---|---|
| `title:` | Config name |
| `note:` | Free-form Markdown description |
| `method:` | `GET` / `POST` / `PUT` / `DELETE` |
| `url:` | Request URL (placeholders like `＜API_KEY＞` are supported) |
| `headers:` | Request headers (dict format) |
| `body:` | Request body (dict format) |
| `response_path:` | jmespath expression to extract a value from the response |

### Action Chain (`configs/actions/*.yaml`)

Run multiple requests in sequence, passing each step's result to the next.

```yaml
title: "echo_chain"
note: "Two-step chain — step 2 receives step 1's extracted result"
action_config:
  steps:
    - config: "configs/singles/echo.yaml"
      inputs:
        - "＜user_input_0＞"
    - config: "configs/singles/echo.yaml"
      inputs:
        - "＜action_result_0＞"
```

### Placeholders

| Placeholder | Alias | Meaning |
|---|---|---|
| `＜user_input_N＞` | `{{user_input_N}}` | N-th user input (0-indexed) |
| `＜action_result_N＞` | `{{action_result_N}}` | Extracted result of step N |
| `＜API_KEY＞` | `{{API_KEY}}` | API key (substituted at runtime) |

### Legacy Field Aliases (inside `single_config:`)

| Canonical | Legacy alias |
|---|---|
| `url:` | `uri:` |
| `body:` | `req_body:` |
| `headers:` (dict) | `header_df:` (list of `{Property, Value}`) |
| `response_path:` | `user_property_path:` |

---

## CLI Usage

### Single Request

```bash
yapilet single <path-to-yaml> [OPTIONS]
```

```bash
# Send a real HTTP request
yapilet single configs/singles/001_get_simple_api_test.yaml

# Pass an API key
yapilet single configs/singles/myapi.yaml --api-key sk-xxx

# Pass multiple user inputs
yapilet single configs/singles/explain.yaml \
  --user-input "machine learning" \
  --api-key sk-xxx

# --mock-echo: no real HTTP sent; echoes request as response (for testing)
yapilet single configs/singles/echo.yaml --user-input hello --mock-echo
```

### Action Chain

```bash
yapilet action <path-to-yaml> [OPTIONS]
```

```bash
# Run a two-step chain
yapilet action configs/actions/echo_chain.yaml --user-input hello --mock-echo
```

Output:
```
step 1 (echo): hello
step 2 (echo): hello
```

### Options

| Option | Description |
|---|---|
| `--user-input TEXT` | User input (repeatable) |
| `--api-key TEXT` | API key (falls back to `API_KEY` env var) |
| `--mock-echo` | Use MockAdapter — echo request offline |

### API Key via Environment Variable

```bash
export API_KEY=sk-xxxxxxxxxxxx
yapilet single configs/singles/myapi.yaml --user-input "machine learning"
```

---

## Library Usage

Call use cases directly from Python code.

### Single Request

```python
from yapilet.core.application.execute_single import ExecuteSingleUseCase
from yapilet.core.infrastructure.mock_adapter import MockAdapter  # Use HttpxAdapter in production
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

### Action Chain

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

### Result Object Fields

| Field | Type | Description |
|---|---|---|
| `status_code` | `int` | HTTP status code |
| `is_success` | `bool` | `True` if 200–299 |
| `extracted` | `Any` | Value extracted by `response_path` |
| `body` | `Any` | Full response body |
| `error` | `str \| None` | Error message (None on success) |
