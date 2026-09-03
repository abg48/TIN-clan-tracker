import importlib


def test_bot_uses_sync_api_when_configured(monkeypatch):
    monkeypatch.setenv("SYNC_API_BASE_URL", "https://sync.example.com")

    import app.bot.db_queries as db_queries
    importlib.reload(db_queries)

    class FakeResponse:
        status_code = 200

        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    calls = {}

    def fake_get(url, params=None, timeout=None):
        calls["url"] = url
        calls["params"] = params
        calls["timeout"] = timeout
        return FakeResponse({"rsn": "Bob", "rank": "Recruit", "total_xp": 12345, "timestamp": "2025-01-01 00:00:00"})

    monkeypatch.setattr(db_queries.requests, "get", fake_get)

    member = db_queries.get_member_total_xp("Bob")

    assert member["rsn"] == "Bob"
    assert member["total_xp"] == 12345
    assert calls["url"] == "https://sync.example.com/member/Bob" 
