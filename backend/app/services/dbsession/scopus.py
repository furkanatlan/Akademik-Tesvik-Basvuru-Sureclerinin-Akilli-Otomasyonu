"""Scopus: oturumlu atıf raporu ve dergi kapsam kanıtı (kılavuz s.12-13).

Filtreler arayüz tıklamaları yerine Scopus gelişmiş arama sorgusuyla uygulanır; sorgu metni sonuç
sayfasında ve URL'de görünür, böylece ekran görüntüsü filtreleri kendiliğinden belgeler:

    REFEID(2-s2.0-XXXX)        -> bu yayına atıf yapan belgeler
    AND PUBYEAR IS 2026        -> kılavuz madde 3: atıf yılı sınırlaması
    AND PUBSTAGE(final)        -> kılavuz madde 1: "Article in Press" hariç
    AND NOT AU-ID(123456)      -> kılavuz madde 2: başvuru sahibinin kendi atıfları hariç
    AND DOCTYPE(ar OR re)      -> yalnızca makale/derleme (bildiri 'cp' atıfları hariç)

Not (Öğrenci 2): seçiciler gerçek kurum hesabıyla doğrulanmalıdır; sayfa yapısı değişirse yalnızca
bu dosyadaki sabitler güncellenir.
"""
import re
from pathlib import Path
from urllib.parse import urlencode

from playwright.sync_api import BrowserContext, Page

from app.core.names import same_person
from app.services.dbsession.browser import DATABASES, find_page
from app.services.dbsession.common import CitationReport, GuidedStepRequired
from app.services.evidence.screenshot import highlight_terms, stamp_header

RESULTS_URL = "https://www.scopus.com/results/results.uri"
RECORD_URL = "https://www.scopus.com/record/display.uri"
SOURCE_URL = "https://www.scopus.com/sourceid/{source_id}"
EID_RE = re.compile(r"2-s2\.0-\d{6,}")
AUTHOR_LINK = "a[href*='authorId=']"
RESULT_COUNT_RE = re.compile(r"([\d.,]+)\s+(?:documents? (?:found|have cited)|belge)", re.I)


def query_url(query: str) -> str:
    return f"{RESULTS_URL}?" + urlencode(
        {"sort": "plf-f", "src": "s", "sot": "a", "sdt": "a", "s": query, "origin": "searchadvanced"}
    )


def citing_query(eid: str, year: int, author_id: str | None) -> str:
    q = f"REFEID({eid}) AND PUBYEAR IS {year} AND PUBSTAGE(final) AND DOCTYPE(ar OR re)"
    return q + (f" AND NOT AU-ID({author_id})" if author_id else "")


def _page(ctx: BrowserContext) -> Page:
    page = find_page(ctx, DATABASES["scopus"]) or ctx.new_page()
    page.bring_to_front()
    return page


def _open(page: Page, url: str) -> str:
    page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    page.wait_for_load_state("networkidle", timeout=45_000)
    return page.content()


def find_eid(page: Page, doi: str | None, title: str) -> str | None:
    query = f'DOI("{doi}")' if doi else f'TITLE("{title}")'
    match = EID_RE.search(_open(page, query_url(query)))
    return match.group(0) if match else None


def find_author_id(page: Page, eid: str, applicant_name: str) -> str | None:
    _open(page, f"{RECORD_URL}?eid={eid}&origin=resultslist")
    for link in page.locator(AUTHOR_LINK).all():
        text = link.inner_text().strip()
        href = link.get_attribute("href") or ""
        m = re.search(r"authorId=(\d+)", href)
        if m and text and same_person(applicant_name, text):
            return m.group(1)
    return None


def citing_report(
    ctx: BrowserContext, doi: str | None, title: str, applicant_name: str, year: int, out_png: Path
) -> CitationReport:
    page = _page(ctx)
    eid = find_eid(page, doi, title)
    if not eid:
        raise GuidedStepRequired(
            "scopus",
            [f"Scopus'ta yayınınızı bulun: \"{title}\"", "Yayının 'Cited by' bağlantısına tıklayın",
             f"Year bölümünden {year} -> Limit to", "Author name bölümünden adınız -> Exclude",
             "Article in Press olanlar listede kalmasın", "Ardından 'Bu ekranı kanıt olarak kaydet'e basın"],
            page.url,
        )
    author_id = find_author_id(page, eid, applicant_name)
    query = citing_query(eid, year, author_id)
    html = _open(page, query_url(query))
    count_match = RESULT_COUNT_RE.search(page.inner_text("body"))
    highlight_terms(page, [f"PUBYEAR IS {year}", "PUBSTAGE(final)", "NOT AU-ID", "REFEID"])
    out_png.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out_png), full_page=True)
    stamp_header(out_png, page.url, f"Scopus atıf listesi - {year} yılı, kendine atıflar ve Article in Press hariç")

    notes = [] if author_id else ["Scopus yazar kimliğiniz bulunamadı: kendine atıflar sorguyla hariç tutulamadı, "
                                  "listeyi kontrol edin."]
    if "No documents were found" in html or "sonuç bulunamadı" in html:
        notes.append(f"{year} yılında Scopus'ta atıf bulunamadı.")
    return CitationReport(
        database="scopus",
        png_path=out_png,
        url=page.url,
        result_count=int(re.sub(r"\D", "", count_match.group(1))) if count_match else None,
        applied_filters=[f"PUBYEAR IS {year}", "PUBSTAGE(final)"] + ([f"NOT AU-ID({author_id})"] if author_id else []),
        notes=notes,
    )


def journal_coverage(ctx: BrowserContext, issn: str, journal_title: str, out_png: Path) -> Path:
    """Derginin Scopus'ta tarandığını gösteren kaynak sayfası (işaretli + URL damgalı)."""
    page = _page(ctx)
    match = re.search(r"sourceid/(\d+)", _open(page, query_url(f"ISSN({issn})")))
    if not match:
        raise GuidedStepRequired(
            "scopus",
            [f"Scopus 'Sources' sayfasında ISSN {issn} ile dergiyi açın", "Ardından ekranı kanıt olarak kaydedin"],
            page.url,
        )
    _open(page, SOURCE_URL.format(source_id=match.group(1)))
    highlight_terms(page, [journal_title, "Scopus coverage years", "Years currently covered by Scopus"])
    out_png.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out_png), full_page=False)
    stamp_header(out_png, page.url, "derginin Scopus'ta tarandığını gösteren belge")
    return out_png
