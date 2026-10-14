"""Google Scholar - SerpAPI gerçeklemesi (Sorumlu: Öğrenci 1).

  Yazar arama : GET https://serpapi.com/search?engine=google_scholar_profiles&mauthors=<ad>&api_key=...
                -> profiles[]: author_id, name, affiliations, email, cited_by, thumbnail
  Yayınlar    : engine=google_scholar_author&author_id=<id>&num=100&start=0&sort=pubdate
                -> articles[]: citation_id, title, authors, publication, year, cited_by.cites_id
  Atıflar     : engine=google_scholar&cites=<cites_id>&as_ylo=<yıl>&as_yhi=<yıl>&num=20
                -> organic_results[]
"""
from app.models.schemas import AuthorCandidate, CitingWork, Publication
from app.services.scholar.base import ScholarProvider


class SerpApiProvider(ScholarProvider):
    def search_authors(self, name: str) -> list[AuthorCandidate]:
        raise NotImplementedError("TODO(Öğrenci 1)")

    def list_publications(self, scholar_id: str) -> list[Publication]:
        raise NotImplementedError("TODO(Öğrenci 1)")

    def list_citing_works(self, publication: Publication, year: int) -> list[CitingWork]:
        raise NotImplementedError("TODO(Öğrenci 1)")
