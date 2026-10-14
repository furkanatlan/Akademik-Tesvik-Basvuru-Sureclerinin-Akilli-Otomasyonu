"""WoS / Scopus girişi: paylaşımlı tarayıcı üzerinden yönlendirmeli oturum açma."""
import re
from datetime import datetime
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import get_settings
from app.services.dbsession import browser
from app.services.dbsession.browser import DbLoginRequired

router = APIRouter(prefix="/db-session", tags=["WoS / Scopus girişi"])
DbKey = Literal["wos", "scopus"]


def login_gate_active() -> bool:
    s = get_settings()
    return s.require_db_login and s.scholar_provider != "mock"


def ensure_db_session() -> None:
    """Yayın/atıf taraması ve kanıt üretimi öncesi çağrılır (mock modda atlanır)."""
    if login_gate_active():
        browser.require_login()


def _call(fn, *args):
    try:
        return fn(*args)
    except DbLoginRequired as e:
        raise HTTPException(409, str(e)) from e
    except Exception as e:  # noqa: BLE001  tarayıcıya ulaşılamadı vb.
        raise HTTPException(503, f"Paylaşımlı tarayıcıya ulaşılamadı: {e}") from e


@router.get("")
def overview():
    s = get_settings()
    return {
        "novnc_url": s.novnc_public_url,
        "login_required": login_gate_active(),
        "mock_mode": s.scholar_provider == "mock",
        "browser_ready": browser.browser_available(),
        "databases": [browser.get_status(k) for k in browser.DATABASES],
    }


@router.post("/{db}/open")
def open_login(db: DbKey):
    return _call(browser.open_login, db)


@router.post("/{db}/check")
def check_login(db: DbKey):
    return _call(browser.check_login, db)


@router.post("/{db}/confirm")
def confirm_login(db: DbKey):
    return _call(browser.confirm_login, db)


@router.post("/{db}/logout")
def logout(db: DbKey):
    return browser.logout(db)


class GotoRequest(BaseModel):
    url: str


@router.post("/{db}/goto")
def goto(db: DbKey, req: GotoRequest):
    if browser.DATABASES[db].domain not in req.url:
        raise HTTPException(400, "Yalnızca ilgili veri tabanı adresleri açılabilir.")
    return _call(browser.goto, db, req.url)


class CaptureRequest(BaseModel):
    label: str
    name: str = "kanit"


@router.post("/{db}/capture")
def capture(db: DbKey, req: CaptureRequest):
    """Yönlendirmeli adım: kullanıcının tarayıcıda ulaştığı ekranı URL damgalı kanıt olarak kaydeder."""
    if not browser.get_status(db)["logged_in"]:
        raise HTTPException(409, "Önce giriş yapılmalı.")
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", req.name)[:60]
    out = Path(get_settings().data_dir) / "captures" / f"{db}_{safe}_{datetime.now():%Y%m%d_%H%M%S}.png"
    path = _call(browser.capture_current, db, out, req.label)
    return {"file": str(path.relative_to(get_settings().data_dir))}
