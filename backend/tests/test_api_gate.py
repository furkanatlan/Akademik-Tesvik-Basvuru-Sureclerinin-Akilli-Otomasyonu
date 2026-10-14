from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


def test_scan_blocked_without_db_login(monkeypatch):
    """Gerçek modda WoS/Scopus girişi yapılmadan tarama ve iş başlatılamaz (409)."""
    monkeypatch.setattr(get_settings(), "scholar_provider", "playwright")
    monkeypatch.setattr(get_settings(), "require_db_login", True)
    monkeypatch.setattr("app.services.dbsession.browser.logged_in_databases", lambda: [])
    client = TestClient(app)
    r = client.get("/api/authors/X/citations", params={"year": 2026, "author_name": "A B"})
    assert r.status_code == 409 and r.json()["code"] == "db_login_required"
    r = client.post("/api/jobs", json={"kind": "articles", "scholar_id": "X", "author_name": "A", "data_year": 2026})
    assert r.status_code == 409
