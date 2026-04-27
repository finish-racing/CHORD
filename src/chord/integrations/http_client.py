from __future__ import annotations
import time
import httpx

class SimpleRetryClient:
    def __init__(self, *, timeout: float = 20.0, retries: int = 2, user_agent: str | None = None):
        headers = {}
        if user_agent:
            headers["User-Agent"] = user_agent
        self.timeout = timeout
        self.retries = retries
        self.client = httpx.Client(timeout=timeout, headers=headers, follow_redirects=True)

    def get_json(self, url: str, params: dict | None = None) -> dict:
        last_exc = None
        for attempt in range(self.retries + 1):
            try:
                resp = self.client.get(url, params=params)
                resp.raise_for_status()
                ctype = resp.headers.get("content-type", "")
                if "json" in ctype.lower():
                    return resp.json()
                return {"text": resp.text}
            except Exception as exc:
                last_exc = exc
                if attempt < self.retries:
                    time.sleep(0.75 * (attempt + 1))
        raise last_exc

    def close(self):
        self.client.close()
