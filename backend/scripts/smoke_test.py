"""Kurulum doğrulama: container içindeki tüm araçların çalıştığını kontrol eder.

Çalıştırma:  docker compose exec backend python scripts/smoke_test.py
Çıktılar  :  data/smoke/  (host'ta da görünür)
"""
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # "app" paketini bul

OUT = Path("/data/smoke")
OUT.mkdir(parents=True, exist_ok=True)
results: list[tuple[str, bool, str]] = []


def check(name):
    def deco(fn):
        try:
            results.append((name, True, fn() or ""))
        except Exception as e:  # noqa: BLE001
            results.append((name, False, f"{type(e).__name__}: {e}"))
        return fn
    return deco


@check("Tesseract OCR (tur + eng)")
def _():
    langs = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True).stdout
    assert "tur" in langs and "eng" in langs, langs
    return "diller: tur, eng"


@check("ocrmypdf + ghostscript")
def _():
    v = subprocess.run(["ocrmypdf", "--version"], capture_output=True, text=True).stdout.strip()
    assert shutil.which("gs"), "ghostscript yok"
    return f"ocrmypdf {v}"


@check("PyMuPDF: PDF oluştur, metin bul, highlight + kırmızı etiket")
def _():
    import pymupdf

    from app.services.pdf.highlight import add_label, highlight_on_page

    doc = pymupdf.open()
    page = doc.new_page()
    font = {"fontname": "dejavu", "fontfile": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"}
    page.insert_text((72, 120), "Science of the Total Environment 778 (2022) 146362", fontsize=11, **font)
    page.insert_text((72, 160), "Ahmet Yılmaz, Mehmet Kaya", fontsize=11, **font)
    n = highlight_on_page(page, ["2022", "Kaya"])
    add_label(page, "tarihin işaretlenmesi / ilgili yazarın işaretlenmesi")
    doc.save(OUT / "pdf_highlight.pdf")
    assert n >= 2, f"bulunan: {n}"
    return f"{n} alan işaretlendi -> data/smoke/pdf_highlight.pdf"


@check("Playwright Chromium: sayfa aç, highlight, URL damgalı ekran görüntüsü")
def _():
    from playwright.sync_api import sync_playwright

    from app.services.evidence.screenshot import highlight_terms, stamp_header

    html = ("<h2>ENERGY CONVERSION AND MANAGEMENT</h2><p>Web of Science Core Collection: "
            "Science Citation Index Expanded</p>")
    png = OUT / "screenshot.png"
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        page = b.new_page()
        page.set_content(html)
        n = highlight_terms(page, ["Science Citation Index Expanded"])
        page.screenshot(path=str(png))
        b.close()
    stamp_header(png, "https://mjl.clarivate.com/search-results", "sci indeksin işaretlenmesi")
    assert n == 1
    return "-> data/smoke/screenshot.png"


@check("img2pdf + birleştirme (tek dosya)")
def _():
    from app.services.pdf.assemble import merge_pdfs, png_to_pdf

    png_pdf = png_to_pdf(OUT / "screenshot.png", OUT / "screenshot.pdf")
    merged = merge_pdfs([OUT / "pdf_highlight.pdf", png_pdf], OUT / "birlesik_ornek.pdf")
    return f"-> data/smoke/{merged.name}"


@check("Kılavuz kuralları + yıl mantığı")
def _():
    from app.core.years import year_options

    return " | ".join(o.label for o in year_options())


@check("PostgreSQL bağlantısı")
def _():
    from sqlalchemy import create_engine, text

    from app.config import get_settings

    with create_engine(get_settings().database_url).connect() as c:
        return c.execute(text("select version()")).scalar().split(",")[0]


@check("Redis bağlantısı")
def _():
    import redis

    from app.config import get_settings

    assert redis.from_url(get_settings().redis_url).ping()
    return "PONG"


@check("Paylaşımlı tarayıcı (WoS/Scopus girişi): CDP bağlantısı")
def _():
    from app.services.dbsession.browser import shared_context

    with shared_context() as ctx:
        return f"bağlandı, açık sekme: {len(ctx.pages)} (kullanıcı ekranı: http://localhost:6080/vnc.html)"


@check("İnternet erişimi (OpenAlex API)")
def _():
    import httpx

    r = httpx.get("https://api.openalex.org/works?per_page=1", timeout=20)
    r.raise_for_status()
    return f"HTTP {r.status_code}"


width = max(len(n) for n, _, _ in results)
for name, ok, info in results:
    print(f"{'OK  ' if ok else 'HATA'}  {name.ljust(width)}  {info}")
sys.exit(0 if all(ok for _, ok, _ in results) else 1)
