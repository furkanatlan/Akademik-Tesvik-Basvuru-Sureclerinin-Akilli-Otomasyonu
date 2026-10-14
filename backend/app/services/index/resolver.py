"""Derginin tarandığı dizinlerin tespiti (Sorumlu: Öğrenci 2).

Girdi: JournalInfo (ad, ISSN, eISSN). Çıktı: JournalInfo.indexes + index_evidence_urls (+ founded_year).
WoS / Scopus girişi yapıldıktan SONRA çalışır (kılavuz akışı: giriş -> dizin taraması -> kanıt).

Kaynaklar (öncelik sırasıyla):
  1. WoS Master Journal List (SCIE/SSCI/AHCI/ESCI) - kılavuz s.5, s.17
       https://mjl.clarivate.com/search-results?issn=<ISSN>   (Playwright)
       "Web of Science Core Collection:" satırındaki dizin adı okunur.
  2. Scopus - oturumlu paylaşımlı tarayıcı: app.services.dbsession.scopus.journal_coverage
  3. TR Dizin (ULAKBİM) - kılavuz s.20
       https://search.trdizin.gov.tr/tr/dergi/ara?q=<dergi adı>  ; yıl rozetleri (yeşil = o yıl taranıyor)
  4. Diğer uluslararası - dergi sitesi: app.services.journal.site (Öğrenci 3)
Tüm sonuçlar önbelleğe alınır (aynı dergi tekrar sorgulanmaz).
"""
from app.models.schemas import JournalInfo


def resolve_indexes(journal: JournalInfo) -> JournalInfo:
    raise NotImplementedError("TODO(Öğrenci 2)")
