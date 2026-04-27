from __future__ import annotations
from chord.integrations.http_client import SimpleRetryClient

class LastFMClient:
    def __init__(self, api_root: str, api_key: str, *, user_agent: str = "CHORD/0.1.0"):
        self.api_root = api_root
        self.api_key = api_key
        self.http = SimpleRetryClient(user_agent=user_agent)

    def track_info(self, *, artist: str, track: str) -> dict:
        return self.http.get_json(self.api_root, {
            "method": "track.getInfo",
            "api_key": self.api_key,
            "artist": artist,
            "track": track,
            "format": "json",
            "autocorrect": 1,
        })

    def track_top_tags(self, *, artist: str, track: str) -> dict:
        return self.http.get_json(self.api_root, {
            "method": "track.getTopTags",
            "api_key": self.api_key,
            "artist": artist,
            "track": track,
            "format": "json",
            "autocorrect": 1,
        })

    def close(self):
        self.http.close()
