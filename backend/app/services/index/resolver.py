"""Derginin tarandığı dizinlerin tespiti (Sorumlu: Öğrenci 2).

Girdi: JournalInfo (ad, ISSN, eISSN). Çıktı: JournalInfo.indexes + index_evidence_urls + founded_year.

Kaynaklar (öncelik sırasıyla) ve yöntem:
  1. WoS Master Journal List (SCIE/SSCI/AHCI/ESCI) - kılavuz s.5, s.17
       https://mjl.clarivate.com/search-results?issn=<ISSN>   (Playwright; sayfa JS ile yüklenir)
       "Web of Science Core Collection:" satırındaki dizin adı okunur.
  2. TR Dizin (ULAKBİM) - kılavuz s.20
       https://search.trdizin.gov.tr/tr/dergi/ara?q=<dergi adı>  ; yıl rozetleri (yeşil = o yıl taranıyor)
  3. Scopus
       a) ELSEVIER_API_KEY varsa: https://api.elsevier.com/content/serial/title/issn/<ISSN>
       b) yoksa: Scopus Source List (Elsevier'in yayımladığı xlsx) -> /data/cache/scopus_sources.xlsx, ISSN eşleşmesi
  4. Diğer uluslararası (kılavuz s.6-7, s.26-27)
       Derginin kendi sitesi / DergiPark sayfası: 'Index', 'Indexing', 'Abstracting', 'Dizinler'
       bağlantıları bulunur; kuruluş yılı ('Founded', 'Since', ilk sayı/arşiv) ve
       'Editorial Board' sayfası tespit edilir.
Tüm sonuçlar önbelleğe alınır (aynı dergi tekrar sorgulanmaz).
"""
from app.models.schemas import JournalInfo


def resolve_indexes(journal: JournalInfo) -> JournalInfo:
    raise NotImplementedError("TODO(Öğrenci 2)")


def find_journal_pages(homepage_url: str) -> dict[str, str]:
    """{'indexing': url, 'editorial_board': url, 'archive': url, 'about': url}"""
    raise NotImplementedError("TODO(Öğrenci 2)")


def foreign_board_members(editorial_board_url: str) -> list[str]:
    """Yayın kurulunda Türkiye dışındaki üye satırları (işaretlenecek metinler)."""
    raise NotImplementedError("TODO(Öğrenci 2)")
