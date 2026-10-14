"""Paylaşımlı tarayıcıya bağlanma ve WoS / Scopus oturum durumu.

Akış:
  1. Kullanıcı arayüzde "Giriş yap"a basar -> open_login(): paylaşımlı tarayıcı giriş sayfasını açar.
  2. Kullanıcı arayüzde gömülü tarayıcıda (noVNC) kurum hesabıyla giriş yapar.
  3. check_login(): sayfa içeriğinden erişim olup olmadığı anlaşılır; sonuç Redis'e yazılır.
     Algılama yanılırsa kullanıcı "Girişi yaptım" ile onaylar (confirm_login).
  4. Worker, aynı tarayıcıya CDP ile bağlanarak (shared_context) oturumlu tarama yapar.
"""
import json
import re
import socket
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import redis
from playwright.sync_api import BrowserContext, Page, sync_playwright

from app.config import get_settings
from app.services.evidence.screenshot import stamp_header


@dataclass(frozen=True)
class Database:
    key: str
    name: str
    login_url: str
    domain: str  # ana alan adı (sonuç sayfaları)
    login_domains: tuple[str, ...]  # giriş sırasında geçilen alan adları (yönlendirmeler)
    denied_patterns: tuple[str, ...]  # erişim YOK göstergeleri (URL veya sayfa metni)
    granted_patterns: tuple[str, ...]  # erişim VAR göstergeleri (sayfa metni)


DATABASES = {
    "wos": Database(
        key="wos",
        name="Web of Science",
        login_url="https://www.webofscience.com/wos/woscc/basic-search",
        domain="webofscience.com",
        login_domains=("webofscience.com", "clarivate.com", "webofknowledge.com"),
        denied_patterns=(
            "access.clarivate.com/login",
            "do not have access",
            "don't have access",
            "erişiminiz yok",
            "sign in to continue",
        ),
        granted_patterns=("Web of Science Core Collection", "Search in:", "Documents", "Researchers"),
    ),
    "scopus": Database(
        key="scopus",
        name="Scopus",
        login_url="https://www.scopus.com/search/form.uri?display=basic",
        domain="scopus.com",
        login_domains=("scopus.com", "elsevier.com"),
        denied_patterns=(
            "id.elsevier.com",
            "Scopus Preview",
            "Check access",
            "Sign in to Scopus",
        ),
        granted_patterns=("Search within", "Documents", "Advanced document search", "Search history"),
    ),
}


class DbLoginRequired(RuntimeError):
    """WoS/Scopus girişi doğrulanmadan oturum gerektiren işlem başlatıldı."""


# --------------------------------------------------------------------------- tarayıcı bağlantısı
def _cdp_endpoint() -> str:
    s = get_settings()
    # Chromium, Host başlığı IP/localhost olmayan CDP isteklerini reddeder -> servis adını IP'ye çevir
    ip = socket.gethostbyname(s.browser_cdp_host)
    return f"http://{ip}:{s.browser_cdp_port}"


@contextmanager
def shared_context() -> Iterator[BrowserContext]:
    """Kullanıcının giriş yaptığı paylaşımlı tarayıcının oturumlu bağlamı.

    Bağlantı kapatılınca tarayıcı KAPANMAZ (yalnızca CDP bağlantısı kopar).
    """
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(_cdp_endpoint(), timeout=15_000)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        yield ctx


def _target_id(ctx: BrowserContext, page: Page) -> str:
    """Chromium sekme kimliği: sekme farklı sitelere (kurum girişi vb.) yönlense de değişmez."""
    session = ctx.new_cdp_session(page)
    try:
        return session.send("Target.getTargetInfo")["targetInfo"]["targetId"]
    finally:
        session.detach()


def find_page(ctx: BrowserContext, db: Database) -> Page | None:
    """Veri tabanı için açılan sekmeyi bulur (önce kayıtlı sekme kimliği, sonra alan adı)."""
    tab = _redis().get(f"{_key(db.key)}:tab")
    if tab:
        for page in ctx.pages:
            if _target_id(ctx, page) == tab.decode():
                return page
    for page in reversed(ctx.pages):
        if any(d in page.url for d in db.login_domains):
            return page
    return None


def _remember_tab(ctx: BrowserContext, db: Database, page: Page) -> None:
    _redis().set(f"{_key(db.key)}:tab", _target_id(ctx, page))


def browser_available() -> bool:
    try:
        with shared_context():
            return True
    except Exception:  # noqa: BLE001
        return False


# --------------------------------------------------------------------------- oturum durumu (Redis)
def _redis() -> redis.Redis:
    return redis.from_url(get_settings().redis_url)


def _key(db_key: str) -> str:
    return f"dbsession:{db_key}"


def get_status(db_key: str) -> dict:
    raw = _redis().get(_key(db_key))
    base = {"database": db_key, "name": DATABASES[db_key].name, "logged_in": False, "method": None,
            "checked_at": None, "detail": "Giriş yapılmadı", "current_url": None}
    return base | json.loads(raw) if raw else base


def _save_status(db_key: str, logged_in: bool, method: str, detail: str, url: str | None) -> dict:
    data = {"logged_in": logged_in, "method": method, "detail": detail, "current_url": url,
            "checked_at": datetime.now().isoformat(timespec="seconds")}
    ttl = get_settings().db_session_ttl_hours * 3600
    _redis().set(_key(db_key), json.dumps(data), ex=ttl)
    return get_status(db_key)


def logged_in_databases() -> list[str]:
    return [k for k in DATABASES if get_status(k)["logged_in"]]


def require_login() -> list[str]:
    """Oturum gerektiren adımların başında çağrılır."""
    dbs = logged_in_databases()
    if not dbs:
        raise DbLoginRequired("Önce Web of Science veya Scopus girişi yapılmalı.")
    return dbs


# --------------------------------------------------------------------------- giriş akışı
def open_login(db_key: str) -> dict:
    db = DATABASES[db_key]
    with shared_context() as ctx:
        page = find_page(ctx, db) or ctx.new_page()
        _remember_tab(ctx, db, page)
        page.goto(db.login_url, wait_until="domcontentloaded", timeout=60_000)
        page.bring_to_front()
        return {"opened": page.url}


def _evaluate_access(page: Page, db: Database) -> tuple[bool, str]:
    url = page.url
    text = page.inner_text("body", timeout=10_000)
    haystack = f"{url}\n{text}".lower()
    for pattern in db.denied_patterns:
        if pattern.lower() in haystack:
            return False, f"Erişim görünmüyor ('{pattern}'). Kurum hesabınızla giriş yapın."
    if db.domain not in url:
        return False, f"Giriş işlemi sürüyor (şu an: {url.split('/')[2] if '//' in url else url})."
    if any(re.search(re.escape(p), text, re.I) for p in db.granted_patterns):
        return True, "Erişim doğrulandı."
    return False, "Erişim otomatik doğrulanamadı. Giriş yaptıysanız 'Girişi yaptım' ile onaylayın."


def check_login(db_key: str) -> dict:
    db = DATABASES[db_key]
    with shared_context() as ctx:
        page = find_page(ctx, db)
        if page is None:
            return _save_status(db_key, False, "auto", "Giriş sayfası açık değil.", None)
        page.wait_for_load_state("domcontentloaded")
        ok, detail = _evaluate_access(page, db)
        return _save_status(db_key, ok, "auto", detail, page.url)


def confirm_login(db_key: str) -> dict:
    """Otomatik algılama yanıldığında kullanıcının onayı (tarayıcının hâlâ ilgili sitede olması şartıyla)."""
    db = DATABASES[db_key]
    with shared_context() as ctx:
        page = find_page(ctx, db)
        if page is None:
            return _save_status(db_key, False, "manual", f"Tarayıcıda {db.name} sayfası açık değil.", None)
        return _save_status(db_key, True, "manual", "Kullanıcı girişi onayladı.", page.url)


def logout(db_key: str) -> dict:
    _redis().delete(_key(db_key))
    return get_status(db_key)


# --------------------------------------------------------------------------- yönlendirmeli adımlar
def goto(db_key: str, url: str) -> dict:
    """Kullanıcıya bir sayfayı tarayıcıda göster (yarı otomatik adımlar için)."""
    with shared_context() as ctx:
        db = DATABASES[db_key]
        page = find_page(ctx, db) or ctx.new_page()
        _remember_tab(ctx, db, page)
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        page.bring_to_front()
        return {"opened": page.url}


def capture_current(db_key: str, out_png: Path, label: str, full_page: bool = True) -> Path:
    """Kullanıcının tarayıcıda ulaştığı (ör. filtreleri elle uyguladığı) ekranı kanıt olarak kaydeder.

    Kılavuz: ekran görüntüsünün alındığı web adresi belge üzerinde görülmeli -> URL damgası eklenir.
    """
    out_png.parent.mkdir(parents=True, exist_ok=True)
    with shared_context() as ctx:
        page = find_page(ctx, DATABASES[db_key])
        if page is None:
            raise DbLoginRequired(f"Tarayıcıda {DATABASES[db_key].name} sayfası açık değil.")
        page.wait_for_load_state("networkidle", timeout=30_000)
        time.sleep(0.5)
        page.screenshot(path=str(out_png), full_page=full_page)
        url = page.url
    stamp_header(out_png, url, label)
    return out_png
