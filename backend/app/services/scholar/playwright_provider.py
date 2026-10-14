"""Google Scholar - Playwright gerçeklemesi (Sorumlu: Öğrenci 1).

Kullanılacak URL'ler:
  Yazar arama : https://scholar.google.com/citations?view_op=search_authors&mauthors=<ad soyad>&hl=tr
                -> div.gsc_1usr : fotoğraf (img), ad (h3 a), kurum (.gs_ai_aff), e-posta (.gs_ai_eml), atıf (.gs_ai_cby)
  Yayın listesi: https://scholar.google.com/citations?user=<id>&hl=tr&cstart=0&pagesize=100&sortby=pubdate
                -> tr.gsc_a_tr  (sayfalama: cstart += 100)
  Atıflar     : https://scholar.google.com/scholar?cites=<cites_id>&as_ylo=<yıl>&as_yhi=<yıl>&hl=tr
                -> div.gs_r.gs_or.gs_scl

Kurallar (engellenmemek için ZORUNLU):
  * Tek bir kalıcı tarayıcı bağlamı (persistent context), gerçekçi User-Agent, tr-TR locale.
  * Her istek arasında SCRAPE_MIN_DELAY_SEC..SCRAPE_MAX_DELAY_SEC rastgele bekleme.
  * Sonuçlar Postgres'te CACHE_TTL_HOURS süreyle önbelleklenir; aynı sayfa tekrar çekilmez.
  * CAPTCHA ('gs_captcha', 'sorry/index') görülürse işlemi durdur, kullanıcıya bildir,
    SerpAPI'ye geç (fallback). CAPTCHA çözme/atlatma yapılmaz.
"""
from app.models.schemas import AuthorCandidate, CitingWork, Publication
from app.services.scholar.base import ScholarProvider


class PlaywrightScholarProvider(ScholarProvider):
    def search_authors(self, name: str) -> list[AuthorCandidate]:
        raise NotImplementedError("TODO(Öğrenci 1)")

    def list_publications(self, scholar_id: str) -> list[Publication]:
        raise NotImplementedError("TODO(Öğrenci 1)")

    def list_citing_works(self, publication: Publication, year: int) -> list[CitingWork]:
        raise NotImplementedError("TODO(Öğrenci 1)")
