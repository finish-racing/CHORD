from __future__ import annotations
from chord.integrations.http_client import SimpleRetryClient

class AcousticBrainzClient:
    def __init__(self, api_root: str, *, user_agent: str = "CHORD/0.1.0"):
        self.api_root = api_root.rstrip("/")
        self.http = SimpleRetryClient(user_agent=user_agent)

    def by_mbid(self, recording_mbid: str) -> dict:
        return self.http.get_json(f"{self.api_root}/{recording_mbid}/high-level")

    def close(self):
        self.http.close()
