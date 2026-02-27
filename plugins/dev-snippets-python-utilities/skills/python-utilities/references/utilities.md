# Python Utility References

## 1) Store Secrets in System Keyring

```python
import json
import keyring

def store_secret(app_name: str, namespace: str, content, secret_type: str = "api_token"):
    service_name = f"com.{app_name}.{secret_type}"
    if isinstance(content, dict):
        content = "JSON:" + json.dumps(content)
    keyring.set_password(service_name, namespace, content)

def retrieve_secret(app_name: str, namespace: str, secret_type: str = "api_token"):
    service_name = f"com.{app_name}.{secret_type}"
    content = keyring.get_password(service_name, namespace)
    if content and content.startswith("JSON:"):
        return json.loads(content[5:])
    return content
```

Caveats:
- Linux needs `libsecret` provider installed.
- Windows credential size limits may apply.

Verification:
```python
store_secret("demoapp", "default", {"token": "abc"})
assert retrieve_secret("demoapp", "default")["token"] == "abc"
```

Fallback:
- If keyring backend is unavailable, require explicit env-var fallback with clear risk note.

## 2) Convert HTML to Markdown In-Memory

```python
from markitdown.converters._html_converter import HtmlConverter

html_converter = HtmlConverter()

def convert_html_to_markdown(html_text: str) -> str:
    return html_converter.convert_string(html_text).markdown.strip()
```

Prerequisites:
- `pip install "markitdown[all]"`

Verification:
```python
assert "# Title" in convert_html_to_markdown("<h1>Title</h1>")
```

Fallback:
- If converter import fails, use a simpler parser and note fidelity tradeoff.

## 3) Sync/Async Compatible Decorator

Use this when you need one callable function usable by sync and async callers.

```python
import asyncio
import concurrent.futures
from functools import wraps

def sync_async_compatible(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            asyncio.get_running_loop()

            def run_in_new_loop():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(func(*args, **kwargs))
                finally:
                    new_loop.close()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_new_loop)
                return future.result()
        except RuntimeError:
            return asyncio.run(func(*args, **kwargs))
    return wrapper
```

Caveats:
- Running inside async context creates thread/executor overhead.
- Not ideal for high-frequency calls.
- Exceptions from async function propagate through future result path.

Verification:
```python
@sync_async_compatible
async def ping(v):
    return v

assert ping("ok") == "ok"
```

Fallback:
- For async-heavy call paths, expose explicit `async def` API and keep sync wrapper as convenience only.

