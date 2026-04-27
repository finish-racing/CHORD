from __future__ import annotations
from chord.integrations.http_client import SimpleRetryClient

class MusicBrainzClient:
    def __init__(self, api_root: str, user_agent: str):
        self.api_root = api_root.rstrip("/")
        self.http = SimpleRetryClient(user_agent=user_agent)

    def search_recording(self, *, artist: str, title: str) -> dict:
        query = f'recording:"{title}" AND artist:"{artist}"'
        return self.http.get_json(f"{self.api_root}/recording", {
            "query": query,
            "fmt": "json",
            "limit": 5,
        })

    def close(self):
        self.http.close()
