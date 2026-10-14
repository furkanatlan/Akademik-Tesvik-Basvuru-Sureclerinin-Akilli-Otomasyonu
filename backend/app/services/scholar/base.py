"""Google Scholar veri sağlayıcı arayüzü (Sorumlu: Öğrenci 1).

Üç gerçekleme vardır, .env içindeki SCHOLAR_PROVIDER ile seçilir:
    mock       -> fixtures/mock_data.json (arayüz geliştirme / test)
    playwright -> scholar.google.com headless Chromium ile (ücretsiz, yavaş, CAPTCHA riski)
    serpapi    -> serpapi.com Google Scholar API (en güvenilir)
"""
from abc import ABC, abstractmethod

from app.models.schemas import AuthorCandidate, CitingWork, Publication


class ScholarProvider(ABC):
    @abstractmethod
    def search_authors(self, name: str) -> list[AuthorCandidate]:
        """Ad-soyad ile profil ara. Fotoğraf, kurum, doğrulanmış e-posta alanı döndür."""

    @abstractmethod
    def list_publications(self, scholar_id: str) -> list[Publication]:
        """Yazarın TÜM yayınları (yıl filtresi çağıran tarafta uygulanır)."""

    @abstractmethod
    def list_citing_works(self, publication: Publication, year: int) -> list[CitingWork]:
        """Verilen yayına, verilen YILDA atıf yapan çalışmalar.

        Scholar: cited_by bağlantısına &as_ylo=YIL&as_yhi=YIL eklenir.
        Eski bir yayına bu yıl yapılan atıflar da böylece bulunur.
        """


def get_provider() -> ScholarProvider:
    from app.config import get_settings

    name = get_settings().scholar_provider
    if name == "mock":
        from app.services.scholar.mock_provider import MockProvider

        return MockProvider()
    if name == "playwright":
        from app.services.scholar.playwright_provider import PlaywrightScholarProvider

        return PlaywrightScholarProvider()
    if name == "serpapi":
        from app.services.scholar.serpapi_provider import SerpApiProvider

        return SerpApiProvider()
    raise ValueError(f"Bilinmeyen SCHOLAR_PROVIDER: {name}")
