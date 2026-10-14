"""Web of Science: oturumlu atıf raporu (kılavuz s.10-11).

Kılavuzdaki adımlar sırasıyla otomatik uygulanır:
  1. Early Access atıflar hariç   -> Document Types: Early Access -> Exclude
  2. (Early Access ibareli ama yayımlanmış atıflar kalır)
     + Bildiri içindeki atıflar hariç -> Document Types: Proceedings Paper -> Exclude (proje kuralı)
  3. Kendine atıflar hariç        -> Researcher Profiles: <Soyad, Ad> -> Exclude
  4. Dizin sınırlaması           -> Web of Science Index: <ör. Science Citation Index Expanded> -> Refine
  5. Yıl sınırlaması             -> Publication Years: <yıl> -> Refine
  6. URL belge üzerinde görünür   -> ekran görüntüsüne URL damgası
Sayfa başındaki "Refined By: ... NOT Document Types: Early Access ... NOT Researcher Profiles: ..." satırı
filtrelerin kanıtıdır ve sarı işaretlenir.

Bir adım otomatik yapılamazsa GuidedStepRequired fırlatılır; kullanıcı aynı tarayıcıda adımı elle
tamamlar ve ekranı kanıt olarak kaydeder. Seçiciler gerçek kurum hesabıyla doğrulanmalıdır (Öğrenci 2).
"""
import re
from pathlib import Path

from playwright.sync_api import BrowserContext, Page

from app.services.dbsession.browser import DATABASES, find_page
from app.services.dbsession.common import CitationReport, GuidedStepRequired
from app.services.evidence.screenshot import highlight_terms, stamp_header

ADVANCED_SEARCH_URL = "https://www.webofscience.com/wos/woscc/advanced-search"
SEARCH_BUTTON = re.compile(r"^\s*(Search|Ara)\s*$", re.I)
RECORD_TITLE = "a[data-ta='summary-record-title-link']"
CITING_LINK = "a[href*='citing-summary']"
RESULT_COUNT_RE = re.compile(r"([\d,.]+)\s+results?", re.I)
WOS_INDEX_NAMES = {
    "SCIE": "Science Citation Index Expanded",
    "SSCI": "Social Sciences Citation Index",
    "AHCI": "Arts & Humanities Citation Index",
    "ESCI": "Emerging Sources Citation Index",
}


def _wait(page: Page) -> None:
    page.wait_for_load_state("networkidle", timeout=45_000)


def _facet(page: Page, facet_title: str, option: str | re.Pattern, action: str) -> bool:
    """Sol paneldeki bir filtre bölümünde seçeneği işaretleyip Refine/Exclude uygular."""
    try:
        section = page.get_by_text(facet_title, exact=False).first
        section.scroll_into_view_if_needed()
        section.click()
        page.get_by_role("checkbox", name=option).first.check(timeout=8_000)
        page.get_by_role("button", name=re.compile(rf"^\s*{action}\s*$", re.I)).first.click()
        _wait(page)
        return True
    except Exception:  # noqa: BLE001
        return False


def _open_citing_summary(page: Page, doi: str | None, title: str) -> None:
    page.goto(ADVANCED_SEARCH_URL, wait_until="domcontentloaded", timeout=60_000)
    _wait(page)
    page.locator("textarea").first.fill(f'DO=("{doi}")' if doi else f'TI=("{title}")')
    page.get_by_role("button", name=SEARCH_BUTTON).first.click()
    _wait(page)
    page.locator(RECORD_TITLE).first.click(timeout=15_000)
    _wait(page)
    page.locator(CITING_LINK).first.click(timeout=15_000)
    _wait(page)


def citing_report(
    ctx: BrowserContext,
    doi: str | None,
    title: str,
    applicant_surname_first: str,  # WoS biçimi: "Gursoy, Oguz"
    year: int,
    index: str,
    out_png: Path,
) -> CitationReport:
    page = find_page(ctx, DATABASES["wos"]) or ctx.new_page()
    page.bring_to_front()
    index_name = WOS_INDEX_NAMES.get(index, WOS_INDEX_NAMES["SCIE"])
    guided = [
        f"Web of Science'ta yayınınızı açın: \"{title}\" ve 'Citations' sayısına tıklayın",
        "Document Types -> Early Access -> Exclude",
        "Document Types -> Proceedings Paper -> Exclude (bildiri içindeki atıflar kabul edilmez)",
        f"Researcher Profiles -> {applicant_surname_first} -> Exclude",
        f"Web of Science Index -> {index_name} -> Refine",
        f"Publication Years -> {year} -> Refine",
        "Ardından 'Bu ekranı kanıt olarak kaydet'e basın",
    ]
    try:
        _open_citing_summary(page, doi, title)
    except Exception as e:  # noqa: BLE001
        raise GuidedStepRequired("wos", guided, page.url) from e

    applied, notes = [], []
    if _facet(page, "Document Types", re.compile("Early Access", re.I), "Exclude"):
        applied.append("NOT Document Types: Early Access")
    else:
        notes.append("Listede Early Access atıf yok (ya da filtre uygulanamadı).")
    if _facet(page, "Document Types", re.compile("Proceedings Paper", re.I), "Exclude"):
        applied.append("NOT Document Types: Proceedings Paper")
    surname = applicant_surname_first.split(",")[0].strip()
    if _facet(page, "Researcher Profiles", re.compile(re.escape(surname), re.I), "Exclude"):
        applied.append(f"NOT Researcher Profiles: {applicant_surname_first}")
    else:
        notes.append("Researcher Profiles'da adınız yok: listede kendine atıf olmadığını kontrol edin.")
    if _facet(page, "Web of Science Index", re.compile(re.escape(index_name), re.I), "Refine"):
        applied.append(f"Web of Science Index: {index_name}")
    if _facet(page, "Publication Years", re.compile(rf"^\s*{year}\b"), "Refine"):
        applied.append(f"Publication Years: {year}")

    body = page.inner_text("body")
    # Yıl ve dizin sınırlaması zorunlu: uygulanamadıysa kullanıcı tamamlar
    if f"Publication Years: {year}" not in body or "Web of Science Index" not in body:
        raise GuidedStepRequired("wos", guided[1:], page.url)

    highlight_terms(page, ["Refined By", f"Publication Years: {year}", "NOT Document Types: Early Access",
                           "NOT Document Types: Proceedings Paper", "NOT Researcher Profiles", index_name])
    out_png.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out_png), full_page=True)
    stamp_header(out_png, page.url, f"Web of Science atıf listesi - {index_name}, {year}")
    count = RESULT_COUNT_RE.search(body)
    return CitationReport(
        database="wos",
        png_path=out_png,
        url=page.url,
        result_count=int(re.sub(r"\D", "", count.group(1))) if count else None,
        applied_filters=applied,
        notes=notes,
    )
