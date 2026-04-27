from __future__ import annotations
import json
import httpx

class OpenAIResponsesClient:
    def __init__(self, api_key: str, model: str = "gpt-5.4", timeout: float = 30.0):
        self.api_key = api_key
        self.model = model
        self.client = httpx.Client(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    def enhance_explanations(self, payload: dict) -> dict:
        # Responses API payload scaffold; deterministic fallback handled elsewhere if this fails.
        body = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "You are enhancing playlist recommendation explanations for CHORD. "
                                "Return concise, precise rationale and do not invent track facts."
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": json.dumps(payload)}],
                },
            ],
        }
        resp = self.client.post("https://api.openai.com/v1/responses", json=body)
        resp.raise_for_status()
        return resp.json()

    def close(self):
        self.client.close()
